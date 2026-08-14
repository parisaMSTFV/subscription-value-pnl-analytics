from __future__ import annotations

import pandas as pd

REQUIRED_SUBSCRIPTION_COLUMNS = {
    "subscription_id",
    "customer_id",
    "start_date",
    "duration_days",
    "paid_price",
}


def prepare_subscriptions(subscriptions: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_SUBSCRIPTION_COLUMNS.difference(subscriptions.columns)
    if missing:
        raise ValueError(f"Subscription data is missing columns: {sorted(missing)}")

    frame = subscriptions.copy()
    frame["start_date"] = pd.to_datetime(frame["start_date"])
    frame["duration_days"] = frame["duration_days"].astype(int)
    frame["paid_price"] = frame["paid_price"].astype(float)
    if frame["subscription_id"].duplicated().any():
        raise ValueError("subscription_id must be unique.")
    if frame["duration_days"].le(0).any():
        raise ValueError("duration_days must be positive.")
    if frame["paid_price"].lt(0).any():
        raise ValueError("paid_price cannot be negative.")
    return frame


def allocate_revenue_by_plan(
    subscriptions: pd.DataFrame,
    start: str,
    end_exclusive: str,
) -> pd.DataFrame:
    from .analysis import validate_period

    frame = prepare_subscriptions(subscriptions)
    period_start, period_end = validate_period(start, end_exclusive)
    frame["plan_end"] = frame["start_date"] + pd.to_timedelta(
        frame["duration_days"], unit="D"
    )
    frame["overlap_start"] = frame["start_date"].where(
        frame["start_date"].gt(period_start), period_start
    )
    frame["overlap_end"] = frame["plan_end"].where(
        frame["plan_end"].lt(period_end), period_end
    )
    frame["overlap_days"] = (
        frame["overlap_end"].sub(frame["overlap_start"]).dt.days.clip(lower=0)
    )
    frame["allocated_revenue"] = (
        frame["paid_price"].div(frame["duration_days"]) * frame["overlap_days"]
    )
    return frame[
        [
            "subscription_id",
            "customer_id",
            "start_date",
            "plan_end",
            "duration_days",
            "paid_price",
            "overlap_days",
            "allocated_revenue",
        ]
    ]
