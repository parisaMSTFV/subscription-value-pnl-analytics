from __future__ import annotations

import numpy as np
import pandas as pd

ACTIVITY_METRICS = [
    "orders",
    "items",
    "nmv",
    "pc1",
    "shipping_contribution",
    "benefit_cost",
    "service_cost",
]

REQUIRED_ACTIVITY_COLUMNS = {
    "customer_id",
    "day",
    "rfm_segment",
    "membership_active",
    *ACTIVITY_METRICS,
}


def validate_period(
    start: str,
    end_exclusive: str,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    period_start = pd.Timestamp(start)
    period_end = pd.Timestamp(end_exclusive)
    if period_end <= period_start:
        raise ValueError("end_exclusive must be after start.")
    return period_start, period_end


def prepare_activity(activity: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_ACTIVITY_COLUMNS.difference(activity.columns)
    if missing:
        raise ValueError(f"Activity data is missing columns: {sorted(missing)}")

    frame = activity.copy()
    frame["day"] = pd.to_datetime(frame["day"])
    if frame.duplicated(["customer_id", "day"]).any():
        raise ValueError("Activity data must contain one row per customer and day.")
    if not frame["membership_active"].isin([0, 1, False, True]).all():
        raise ValueError("membership_active must contain only 0 and 1.")

    frame["membership_active"] = frame["membership_active"].astype(int)
    return frame


def build_customer_period(
    activity: pd.DataFrame,
    start: str,
    end_exclusive: str,
) -> pd.DataFrame:
    frame = prepare_activity(activity)
    period_start, period_end = validate_period(start, end_exclusive)
    period = frame[frame["day"].between(period_start, period_end, inclusive="left")]
    if period.empty:
        raise ValueError("No activity rows fall inside the analysis period.")

    totals = period.groupby("customer_id")[ACTIVITY_METRICS].sum()
    latest_segment = (
        period.sort_values("day")
        .groupby("customer_id")["rfm_segment"]
        .last()
        .rename("rfm_segment")
    )
    member_days = (
        period.groupby("customer_id")["membership_active"].sum().rename("member_days")
    )
    prior_membership = (
        frame[frame["day"] < period_start]
        .groupby("customer_id")["membership_active"]
        .max()
    )

    customer_period = totals.join([latest_segment, member_days])
    was_member_before = (
        customer_period.index.to_series().map(prior_membership).fillna(0).eq(1)
    )
    customer_period["membership_status"] = "never_member"
    customer_period.loc[was_member_before, "membership_status"] = "lapsed_member"
    customer_period.loc[customer_period["member_days"].gt(0), "membership_status"] = (
        "active_member"
    )
    customer_period["active_customer"] = customer_period["orders"].gt(0)
    return customer_period.reset_index()


def build_segment_performance(customer_period: pd.DataFrame) -> pd.DataFrame:
    required = {
        "customer_id",
        "membership_status",
        "rfm_segment",
        "active_customer",
        "member_days",
        *ACTIVITY_METRICS,
    }
    missing = required.difference(customer_period.columns)
    if missing:
        raise ValueError(f"Customer-period data is missing columns: {sorted(missing)}")

    segment = (
        customer_period.groupby(
            ["membership_status", "rfm_segment"],
            as_index=False,
            observed=True,
        )
        .agg(
            customers=("customer_id", "nunique"),
            active_customers=("active_customer", "sum"),
            member_days=("member_days", "sum"),
            orders=("orders", "sum"),
            items=("items", "sum"),
            nmv=("nmv", "sum"),
            pc1=("pc1", "sum"),
            shipping_contribution=("shipping_contribution", "sum"),
            benefit_cost=("benefit_cost", "sum"),
            service_cost=("service_cost", "sum"),
        )
        .sort_values(["membership_status", "nmv"], ascending=[True, False])
    )
    segment["order_frequency"] = segment["orders"].div(segment["customers"])
    segment["aov"] = segment["nmv"].div(segment["orders"].replace(0, np.nan)).fillna(0)
    segment["operating_contribution"] = (
        segment["pc1"]
        + segment["shipping_contribution"]
        - segment["benefit_cost"]
        - segment["service_cost"]
    )
    return segment.reset_index(drop=True)


def build_monthly_member_trend(
    activity: pd.DataFrame,
    start: str,
    end_exclusive: str,
) -> pd.DataFrame:
    frame = prepare_activity(activity)
    period_start, period_end = validate_period(start, end_exclusive)
    period = frame[frame["day"].between(period_start, period_end, inclusive="left")]
    member_activity = period[period["membership_active"].eq(1)].copy()
    if member_activity.empty:
        return pd.DataFrame(
            columns=[
                "month",
                "active_members",
                "member_days",
                *ACTIVITY_METRICS,
                "orders_per_member",
                "nmv_per_member",
                "operating_contribution",
            ]
        )

    member_activity["month"] = member_activity["day"].dt.to_period("M").astype(str)
    monthly = (
        member_activity.groupby("month", as_index=False)
        .agg(
            active_members=("customer_id", "nunique"),
            member_days=("customer_id", "size"),
            orders=("orders", "sum"),
            items=("items", "sum"),
            nmv=("nmv", "sum"),
            pc1=("pc1", "sum"),
            shipping_contribution=("shipping_contribution", "sum"),
            benefit_cost=("benefit_cost", "sum"),
            service_cost=("service_cost", "sum"),
        )
        .sort_values("month")
    )
    monthly["orders_per_member"] = monthly["orders"].div(monthly["active_members"])
    monthly["nmv_per_member"] = monthly["nmv"].div(monthly["active_members"])
    monthly["operating_contribution"] = (
        monthly["pc1"]
        + monthly["shipping_contribution"]
        - monthly["benefit_cost"]
        - monthly["service_cost"]
    )
    return monthly.reset_index(drop=True)
