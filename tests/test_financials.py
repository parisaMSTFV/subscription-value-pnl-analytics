from __future__ import annotations

import math

import pandas as pd

from subscription_value.portfolio import build_portfolio_pnl
from subscription_value.revenue import allocate_revenue_by_plan


def _subscriptions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "subscription_id": "S1",
                "customer_id": 1,
                "start_date": "2025-01-01",
                "duration_days": 30,
                "paid_price": 300.0,
                "plan_name": "Monthly",
            }
        ]
    )


def _activity() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "customer_id": 1,
                "day": "2025-01-12",
                "rfm_segment": "Loyal",
                "membership_active": 1,
                "orders": 2,
                "items": 3,
                "nmv": 200.0,
                "pc1": 30.0,
                "shipping_contribution": -2.0,
                "benefit_cost": 5.0,
                "service_cost": 1.0,
            }
        ]
    )


def test_revenue_uses_only_overlapping_plan_days() -> None:
    allocation = allocate_revenue_by_plan(
        _subscriptions(),
        "2025-01-11",
        "2025-01-21",
    )

    assert allocation.loc[0, "overlap_days"] == 10
    assert math.isclose(allocation.loc[0, "allocated_revenue"], 100.0)


def test_portfolio_pnl_reconciles_all_components() -> None:
    pnl = build_portfolio_pnl(
        _activity(),
        _subscriptions(),
        "2025-01-11",
        "2025-01-21",
    ).iloc[0]

    expected = 100.0 + 30.0 - 2.0 - 5.0 - 1.0
    assert math.isclose(pnl["membership_fee_revenue"], 100.0)
    assert math.isclose(pnl["portfolio_contribution"], expected)
