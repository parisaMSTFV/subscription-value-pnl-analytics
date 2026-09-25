from __future__ import annotations

import numpy as np
import pandas as pd

from .revenue import prepare_subscriptions


def build_renewal_detail(
    subscriptions: pd.DataFrame,
    as_of_date: str,
    grace_days: int = 14,
) -> pd.DataFrame:
    if grace_days < 0:
        raise ValueError("grace_days cannot be negative.")

    frame = prepare_subscriptions(subscriptions).sort_values(
        ["customer_id", "start_date", "subscription_id"]
    )
    as_of = pd.Timestamp(as_of_date)
    frame["plan_end"] = frame["start_date"] + pd.to_timedelta(
        frame["duration_days"], unit="D"
    )
    frame["next_start"] = frame.groupby("customer_id")["start_date"].shift(-1)
    frame["renewal_gap_days"] = frame["next_start"].sub(frame["plan_end"]).dt.days
    frame["eligible_for_renewal"] = (
        frame["plan_end"].add(pd.to_timedelta(grace_days, unit="D")).le(as_of)
    )
    frame["renewed"] = (
        frame["eligible_for_renewal"]
        & frame["renewal_gap_days"].ge(-7)
        & frame["renewal_gap_days"].le(grace_days)
    )
    return frame[
        [
            "subscription_id",
            "customer_id",
            "start_date",
            "plan_end",
            "next_start",
            "renewal_gap_days",
            "eligible_for_renewal",
            "renewed",
        ]
    ].reset_index(drop=True)


def build_renewal_summary(renewal_detail: pd.DataFrame) -> pd.DataFrame:
    required = {
        "eligible_for_renewal",
        "renewed",
        "renewal_gap_days",
    }
    missing = required.difference(renewal_detail.columns)
    if missing:
        raise ValueError(f"Renewal detail is missing columns: {sorted(missing)}")

    eligible = renewal_detail[renewal_detail["eligible_for_renewal"]]
    renewed = eligible[eligible["renewed"]]
    eligible_count = int(len(eligible))
    renewed_count = int(len(renewed))
    renewal_rate = renewed_count / eligible_count if eligible_count else 0.0
    median_gap = (
        float(renewed["renewal_gap_days"].median()) if renewed_count else float(np.nan)
    )
    return pd.DataFrame(
        [
            {
                "eligible_subscriptions": eligible_count,
                "renewed_subscriptions": renewed_count,
                "renewal_rate": renewal_rate,
                "median_renewal_gap_days": median_gap,
            }
        ]
    )
