from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def build_renewal_cohorts(renewal_detail: pd.DataFrame) -> pd.DataFrame:
    required = {"plan_end", "eligible_for_renewal", "renewed"}
    missing = required.difference(renewal_detail.columns)
    if missing:
        raise ValueError(f"Renewal detail is missing columns: {sorted(missing)}")

    detail = renewal_detail.copy()
    detail["plan_end"] = pd.to_datetime(detail["plan_end"])
    detail["expiry_cohort"] = detail["plan_end"].dt.to_period("M").astype(str)
    eligible = detail[detail["eligible_for_renewal"]]
    if eligible.empty:
        return pd.DataFrame(
            columns=[
                "expiry_cohort",
                "total_plans",
                "eligible_subscriptions",
                "renewed_subscriptions",
                "renewal_rate",
                "cohort_complete",
            ]
        )

    cohorts = (
        detail.groupby("expiry_cohort", as_index=False)
        .agg(
            total_plans=("renewed", "size"),
            eligible_subscriptions=("eligible_for_renewal", "sum"),
            renewed_subscriptions=("renewed", "sum"),
            cohort_complete=("eligible_for_renewal", "all"),
        )
        .sort_values("expiry_cohort")
    )
    cohorts = cohorts[cohorts["eligible_subscriptions"].gt(0)].copy()
    cohorts["renewal_rate"] = cohorts["renewed_subscriptions"].div(
        cohorts["eligible_subscriptions"]
    )
    return cohorts.reset_index(drop=True)


def build_pnl_sensitivity(
    portfolio_pnl: pd.DataFrame,
    fee_multipliers: Iterable[float] = (0.8, 1.0, 1.2),
    direct_cost_multipliers: Iterable[float] = (0.8, 1.0, 1.2),
) -> pd.DataFrame:
    if portfolio_pnl.empty:
        raise ValueError("Portfolio P&L cannot be empty.")
    required = {
        "membership_fee_revenue",
        "commerce_pc1",
        "shipping_contribution",
        "benefit_cost",
        "service_cost",
    }
    missing = required.difference(portfolio_pnl.columns)
    if missing:
        raise ValueError(f"Portfolio P&L is missing columns: {sorted(missing)}")

    pnl = portfolio_pnl.iloc[0]
    fee_values = tuple(float(value) for value in fee_multipliers)
    cost_values = tuple(float(value) for value in direct_cost_multipliers)
    if not fee_values or not cost_values:
        raise ValueError("Sensitivity grids cannot be empty.")
    if min(*fee_values, *cost_values) < 0:
        raise ValueError("Sensitivity multipliers cannot be negative.")

    operating_before_direct_cost = float(
        pnl["commerce_pc1"] + pnl["shipping_contribution"]
    )
    direct_cost = float(pnl["benefit_cost"] + pnl["service_cost"])
    rows: list[dict[str, float]] = []
    for fee_multiplier in fee_values:
        for cost_multiplier in cost_values:
            fee_revenue = float(pnl["membership_fee_revenue"] * fee_multiplier)
            scenario_direct_cost = direct_cost * cost_multiplier
            contribution = (
                fee_revenue + operating_before_direct_cost - scenario_direct_cost
            )
            rows.append(
                {
                    "fee_multiplier": fee_multiplier,
                    "direct_cost_multiplier": cost_multiplier,
                    "membership_fee_revenue": fee_revenue,
                    "direct_cost": scenario_direct_cost,
                    "portfolio_contribution": contribution,
                }
            )
    return pd.DataFrame(rows)


def build_decision_metrics(
    portfolio_pnl: pd.DataFrame,
    renewal_summary: pd.DataFrame,
    segment_performance: pd.DataFrame,
    monthly_member_trend: pd.DataFrame,
    sensitivity: pd.DataFrame,
) -> dict[str, float | int | str]:
    if portfolio_pnl.empty or renewal_summary.empty:
        raise ValueError("P&L and renewal summary cannot be empty.")
    pnl = portfolio_pnl.iloc[0]
    renewal = renewal_summary.iloc[0]

    portfolio_contribution = float(pnl["portfolio_contribution"])
    fee_share = (
        float(pnl["membership_fee_revenue"]) / portfolio_contribution
        if portfolio_contribution
        else 0.0
    )
    contribution_excluding_fee = float(
        pnl["commerce_pc1"]
        + pnl["shipping_contribution"]
        - pnl["benefit_cost"]
        - pnl["service_cost"]
    )

    active_segments = segment_performance[
        segment_performance["membership_status"].eq("active_member")
    ]
    champion = active_segments[active_segments["rfm_segment"].eq("Champion")]
    active_contribution = float(active_segments["operating_contribution"].sum())
    champion_share = (
        float(champion["operating_contribution"].sum()) / active_contribution
        if active_contribution
        else 0.0
    )

    monthly = monthly_member_trend.sort_values("month")
    if monthly.empty:
        member_change = 0.0
        first_unit_contribution = 0.0
        last_unit_contribution = 0.0
    else:
        first = monthly.iloc[0]
        last = monthly.iloc[-1]
        member_change = (
            float(last["active_members"] / first["active_members"] - 1)
            if first["active_members"]
            else 0.0
        )
        first_unit_contribution = (
            float(first["operating_contribution"] / first["active_members"])
            if first["active_members"]
            else 0.0
        )
        last_unit_contribution = (
            float(last["operating_contribution"] / last["active_members"])
            if last["active_members"]
            else 0.0
        )

    base = sensitivity[
        sensitivity["fee_multiplier"].eq(1.0)
        & sensitivity["direct_cost_multiplier"].eq(1.0)
    ]
    if base.empty:
        raise ValueError("Sensitivity output must contain the 1.0 / 1.0 base case.")
    worst = sensitivity.loc[sensitivity["portfolio_contribution"].idxmin()]

    return {
        "analysis_period_start": str(pnl["period_start"]),
        "analysis_period_end_exclusive": str(pnl["period_end_exclusive"]),
        "active_members": int(pnl["active_members"]),
        "portfolio_contribution": portfolio_contribution,
        "membership_fee_revenue": float(pnl["membership_fee_revenue"]),
        "membership_fee_share_of_contribution": float(fee_share),
        "contribution_excluding_membership_fee": contribution_excluding_fee,
        "renewal_rate": float(renewal["renewal_rate"]),
        "eligible_subscriptions": int(renewal["eligible_subscriptions"]),
        "champion_share_of_active_segment_contribution": champion_share,
        "active_member_change_first_to_last_month": member_change,
        "first_month_contribution_per_active_member": first_unit_contribution,
        "last_month_contribution_per_active_member": last_unit_contribution,
        "worst_grid_fee_multiplier": float(worst["fee_multiplier"]),
        "worst_grid_direct_cost_multiplier": float(
            worst["direct_cost_multiplier"]
        ),
        "worst_grid_portfolio_contribution": float(
            worst["portfolio_contribution"]
        ),
    }
