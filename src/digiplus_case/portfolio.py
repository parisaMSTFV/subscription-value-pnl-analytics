from __future__ import annotations

import pandas as pd

from .analysis import prepare_activity, validate_period
from .revenue import allocate_revenue_by_plan


def build_portfolio_pnl(
    activity: pd.DataFrame,
    subscriptions: pd.DataFrame,
    start: str,
    end_exclusive: str,
) -> pd.DataFrame:
    frame = prepare_activity(activity)
    period_start, period_end = validate_period(start, end_exclusive)
    period = frame[frame["day"].between(period_start, period_end, inclusive="left")]
    member_activity = period[period["membership_active"].eq(1)]
    revenue = allocate_revenue_by_plan(subscriptions, start, end_exclusive)

    membership_fee_revenue = float(revenue["allocated_revenue"].sum())
    commerce_pc1 = float(member_activity["pc1"].sum())
    shipping_contribution = float(member_activity["shipping_contribution"].sum())
    benefit_cost = float(member_activity["benefit_cost"].sum())
    service_cost = float(member_activity["service_cost"].sum())
    portfolio_contribution = (
        membership_fee_revenue
        + commerce_pc1
        + shipping_contribution
        - benefit_cost
        - service_cost
    )

    return pd.DataFrame(
        [
            {
                "period_start": period_start.date().isoformat(),
                "period_end_exclusive": period_end.date().isoformat(),
                "active_members": int(member_activity["customer_id"].nunique()),
                "member_days": int(len(member_activity)),
                "member_orders": int(member_activity["orders"].sum()),
                "member_nmv": float(member_activity["nmv"].sum()),
                "membership_fee_revenue": membership_fee_revenue,
                "commerce_pc1": commerce_pc1,
                "shipping_contribution": shipping_contribution,
                "benefit_cost": benefit_cost,
                "service_cost": service_cost,
                "portfolio_contribution": float(portfolio_contribution),
            }
        ]
    )
