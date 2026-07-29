from __future__ import annotations

import pandas as pd
import pytest

from digiplus_case.renewal import (
    build_renewal_detail,
    build_renewal_summary,
)


def test_renewal_summary_uses_only_eligible_plans() -> None:
    subscriptions = pd.DataFrame(
        [
            {
                "subscription_id": "S1",
                "customer_id": 1,
                "start_date": "2025-01-01",
                "duration_days": 30,
                "paid_price": 100.0,
            },
            {
                "subscription_id": "S2",
                "customer_id": 1,
                "start_date": "2025-01-31",
                "duration_days": 30,
                "paid_price": 100.0,
            },
            {
                "subscription_id": "S3",
                "customer_id": 2,
                "start_date": "2025-01-01",
                "duration_days": 30,
                "paid_price": 100.0,
            },
            {
                "subscription_id": "S4",
                "customer_id": 3,
                "start_date": "2025-03-20",
                "duration_days": 30,
                "paid_price": 100.0,
            },
        ]
    )
    detail = build_renewal_detail(subscriptions, "2025-04-01")
    summary = build_renewal_summary(detail).iloc[0]

    assert summary["eligible_subscriptions"] == 3
    assert summary["renewed_subscriptions"] == 1
    assert summary["renewal_rate"] == pytest.approx(1 / 3)
    assert summary["median_renewal_gap_days"] == 0
