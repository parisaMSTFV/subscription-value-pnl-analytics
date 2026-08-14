from __future__ import annotations

import math

import pandas as pd

from subscription_value.decision_evidence import (
    build_pnl_sensitivity,
    build_renewal_cohorts,
)


def test_renewal_cohorts_exclude_censored_plans() -> None:
    detail = pd.DataFrame(
        [
            {
                "plan_end": "2025-01-31",
                "eligible_for_renewal": True,
                "renewed": True,
            },
            {
                "plan_end": "2025-01-15",
                "eligible_for_renewal": True,
                "renewed": False,
            },
            {
                "plan_end": "2025-01-31",
                "eligible_for_renewal": False,
                "renewed": False,
            },
        ]
    )

    cohorts = build_renewal_cohorts(detail)

    assert cohorts["expiry_cohort"].tolist() == ["2025-01"]
    assert cohorts.loc[0, "eligible_subscriptions"] == 2
    assert math.isclose(cohorts.loc[0, "renewal_rate"], 0.5)
    assert not bool(cohorts.loc[0, "cohort_complete"])


def test_pnl_sensitivity_reconciles_base_and_worst_case() -> None:
    pnl = pd.DataFrame(
        [
            {
                "membership_fee_revenue": 100.0,
                "commerce_pc1": 30.0,
                "shipping_contribution": -5.0,
                "benefit_cost": 10.0,
                "service_cost": 5.0,
            }
        ]
    )

    sensitivity = build_pnl_sensitivity(pnl)
    base = sensitivity[
        sensitivity["fee_multiplier"].eq(1.0)
        & sensitivity["direct_cost_multiplier"].eq(1.0)
    ].iloc[0]
    worst = sensitivity.loc[sensitivity["portfolio_contribution"].idxmin()]

    assert math.isclose(base["portfolio_contribution"], 110.0)
    assert math.isclose(worst["portfolio_contribution"], 87.0)
