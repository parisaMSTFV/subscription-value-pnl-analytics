from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_summary(
    output_path: str | Path,
    pnl: pd.DataFrame,
    renewal: pd.DataFrame,
    segments: pd.DataFrame,
) -> None:
    pnl_row = pnl.iloc[0]
    renewal_row = renewal.iloc[0]
    active_segments = (
        segments[segments["membership_status"].eq("active_member")]
        .sort_values("operating_contribution", ascending=False)
        .head(3)
    )

    lines = [
        "# Subscription portfolio summary",
        "",
        (
            f"Analysis period: {pnl_row['period_start']} to "
            f"{pnl_row['period_end_exclusive']} (end date excluded)"
        ),
        "",
        "| KPI | Result |",
        "|---|---:|",
        f"| Active members | {int(pnl_row['active_members']):,} |",
        f"| Member orders | {int(pnl_row['member_orders']):,} |",
        f"| Member NMV | {pnl_row['member_nmv']:,.2f} |",
        (
            "| Allocated membership fee revenue | "
            f"{pnl_row['membership_fee_revenue']:,.2f} |"
        ),
        (f"| Portfolio contribution | {pnl_row['portfolio_contribution']:,.2f} |"),
        f"| Eligible subscriptions | {int(renewal_row['eligible_subscriptions']):,} |",
        f"| Renewal rate | {renewal_row['renewal_rate']:.1%} |",
        "",
        "## Active-member segments",
        "",
        "| RFM segment | Customers | Orders per customer | Operating contribution |",
        "|---|---:|---:|---:|",
    ]
    for row in active_segments.itertuples(index=False):
        lines.append(
            f"| {row.rfm_segment} | {int(row.customers):,} | "
            f"{row.order_frequency:.2f} | {row.operating_contribution:,.2f} |"
        )
    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
