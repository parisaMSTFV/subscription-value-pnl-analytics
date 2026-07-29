from __future__ import annotations

import pandas as pd

from digiplus_case.analysis import (
    build_customer_period,
    build_segment_performance,
)


def _activity_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "customer_id": 1,
                "day": "2025-01-15",
                "rfm_segment": "Loyal",
                "membership_active": 1,
                "orders": 1,
                "items": 2,
                "nmv": 100.0,
                "pc1": 15.0,
                "shipping_contribution": -2.0,
                "benefit_cost": 3.0,
                "service_cost": 1.0,
            },
            {
                "customer_id": 1,
                "day": "2025-02-01",
                "rfm_segment": "Loyal",
                "membership_active": 1,
                "orders": 2,
                "items": 3,
                "nmv": 220.0,
                "pc1": 32.0,
                "shipping_contribution": -3.0,
                "benefit_cost": 5.0,
                "service_cost": 1.0,
            },
            {
                "customer_id": 2,
                "day": "2025-01-15",
                "rfm_segment": "At Risk",
                "membership_active": 1,
                "orders": 1,
                "items": 1,
                "nmv": 80.0,
                "pc1": 10.0,
                "shipping_contribution": -1.0,
                "benefit_cost": 2.0,
                "service_cost": 1.0,
            },
            {
                "customer_id": 2,
                "day": "2025-02-01",
                "rfm_segment": "At Risk",
                "membership_active": 0,
                "orders": 1,
                "items": 1,
                "nmv": 90.0,
                "pc1": 11.0,
                "shipping_contribution": 1.0,
                "benefit_cost": 0.0,
                "service_cost": 0.0,
            },
            {
                "customer_id": 3,
                "day": "2025-02-01",
                "rfm_segment": "Potential Loyalist",
                "membership_active": 0,
                "orders": 0,
                "items": 0,
                "nmv": 0.0,
                "pc1": 0.0,
                "shipping_contribution": 0.0,
                "benefit_cost": 0.0,
                "service_cost": 0.0,
            },
        ]
    )


def test_customer_period_assigns_membership_status() -> None:
    customer_period = build_customer_period(
        _activity_rows(),
        "2025-02-01",
        "2025-03-01",
    ).set_index("customer_id")

    assert customer_period.loc[1, "membership_status"] == "active_member"
    assert customer_period.loc[2, "membership_status"] == "lapsed_member"
    assert customer_period.loc[3, "membership_status"] == "never_member"
    assert customer_period.loc[1, "orders"] == 2


def test_segment_performance_reconciles_customer_totals() -> None:
    customer_period = build_customer_period(
        _activity_rows(),
        "2025-02-01",
        "2025-03-01",
    )
    segment = build_segment_performance(customer_period)

    assert segment["orders"].sum() == customer_period["orders"].sum()
    assert segment["nmv"].sum() == customer_period["nmv"].sum()
    assert segment["customers"].sum() == customer_period["customer_id"].nunique()
