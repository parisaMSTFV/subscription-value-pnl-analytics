from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
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


def write_decision_report(
    output_path: str | Path,
    metrics: dict[str, float | int | str],
) -> None:
    member_change = float(metrics["active_member_change_first_to_last_month"])
    fee_share = float(metrics["membership_fee_share_of_contribution"])
    champion_share = float(metrics["champion_share_of_active_segment_contribution"])
    first_unit = float(metrics["first_month_contribution_per_active_member"])
    last_unit = float(metrics["last_month_contribution_per_active_member"])
    lines = [
        "# Subscription portfolio decision report",
        "",
        (
            f"Executed period: {metrics['analysis_period_start']} to "
            f"{metrics['analysis_period_end_exclusive']} (end excluded)."
        ),
        "",
        "## Decision snapshot",
        "",
        "| Measure | Executed synthetic result |",
        "|---|---:|",
        f"| Active members | {int(metrics['active_members']):,} |",
        (
            "| Portfolio contribution | "
            f"{float(metrics['portfolio_contribution']):,.2f} |"
        ),
        f"| Renewal rate | {float(metrics['renewal_rate']):.1%} |",
        (
            "| Contribution excluding membership fees | "
            f"{float(metrics['contribution_excluding_membership_fee']):,.2f} |"
        ),
        f"| Membership-fee share of contribution | {fee_share:.1%} |",
        (
            "| Champion share of active-segment contribution | "
            f"{champion_share:.1%} |"
        ),
        "",
        "## Operating interpretation",
        "",
        (
            f"Active membership fell {abs(member_change):.1%} from the first to the "
            "last month of the period."
            if member_change < 0
            else (
                f"Active membership increased {member_change:.1%} from the first "
                "to the last month of the period."
            )
        ),
        (
            "Operating contribution per active member moved from "
            f"{first_unit:,.2f} to {last_unit:,.2f}. The difference between the "
            "membership trend and unit economics should be investigated before "
            "changing price or benefit policy."
        ),
        (
            f"The least favorable configured sensitivity point uses "
            f"{float(metrics['worst_grid_fee_multiplier']):.1f}x fee revenue and "
            f"{float(metrics['worst_grid_direct_cost_multiplier']):.1f}x direct "
            "cost. Portfolio contribution remains "
            f"{float(metrics['worst_grid_portfolio_contribution']):,.2f}."
        ),
        "",
        "These are descriptive synthetic portfolio results. They do not estimate "
        "the incremental effect of membership.",
    ]
    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_metrics(
    output_path: str | Path,
    metrics: dict[str, float | int | str],
) -> None:
    Path(output_path).write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_decision_figures(
    output_dir: str | Path,
    portfolio_pnl: pd.DataFrame,
    monthly_member_trend: pd.DataFrame,
    renewal_cohorts: pd.DataFrame,
    sensitivity: pd.DataFrame,
) -> None:
    figure_dir = Path(output_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    pnl = portfolio_pnl.iloc[0]
    component_names = [
        "Membership fees",
        "Commerce PC1",
        "Shipping",
        "Benefit cost",
        "Service cost",
    ]
    component_values = [
        float(pnl["membership_fee_revenue"]),
        float(pnl["commerce_pc1"]),
        float(pnl["shipping_contribution"]),
        -float(pnl["benefit_cost"]),
        -float(pnl["service_cost"]),
    ]
    colors = ["#2A9D8F" if value >= 0 else "#D65A4A" for value in component_values]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.barh(component_names[::-1], component_values[::-1], color=colors[::-1])
    ax.axvline(0, color="#334155", linewidth=0.8)
    ax.set_title("Executed subscription portfolio P&L components")
    ax.set_xlabel("Synthetic currency units")
    for bar, value in zip(bars, component_values[::-1], strict=True):
        ax.annotate(
            f"{value:,.0f}",
            xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
            xytext=(4 if value >= 0 else -4, 0),
            textcoords="offset points",
            ha="left" if value >= 0 else "right",
            va="center",
            fontsize=9,
        )
    ax.margins(x=0.1)
    ax.text(
        0.99,
        0.04,
        f"Portfolio contribution: {float(pnl['portfolio_contribution']):,.0f}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color="#334155",
        fontsize=10,
        weight="bold",
    )
    fig.tight_layout()
    fig.savefig(figure_dir / "pnl_components.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    monthly = monthly_member_trend.sort_values("month").copy()
    monthly["contribution_per_active_member"] = monthly[
        "operating_contribution"
    ].div(monthly["active_members"])
    fig, left = plt.subplots(figsize=(9, 4.8))
    right = left.twinx()
    left.plot(
        monthly["month"],
        monthly["active_members"],
        marker="o",
        linewidth=2.2,
        color="#264653",
        label="Active members",
    )
    right.plot(
        monthly["month"],
        monthly["contribution_per_active_member"],
        marker="s",
        linewidth=2.2,
        color="#E76F51",
        label="Contribution per active member",
    )
    left.set_ylabel("Active members", color="#264653")
    right.set_ylabel("Contribution per active member", color="#E76F51")
    left.set_title("Membership base and unit economics")
    lines = left.get_lines() + right.get_lines()
    left.legend(lines, [line.get_label() for line in lines], loc="best")
    fig.tight_layout()
    fig.savefig(figure_dir / "monthly_unit_economics.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.bar(
        renewal_cohorts["expiry_cohort"],
        renewal_cohorts["renewal_rate"],
        color="#457B9D",
    )
    for bar, complete in zip(
        bars, renewal_cohorts["cohort_complete"], strict=True
    ):
        if not complete:
            bar.set_hatch("//")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Renewal rate")
    ax.set_title("Renewal rate by plan-expiry cohort")
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    if not renewal_cohorts["cohort_complete"].all():
        ax.text(
            0.99,
            0.96,
            "Hatched cohort is only partially eligible as of the analysis date",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8.5,
            color="#334155",
        )
    fig.tight_layout()
    fig.savefig(figure_dir / "renewal_cohorts.png", dpi=150)
    plt.close(fig)

    grid = sensitivity.pivot(
        index="direct_cost_multiplier",
        columns="fee_multiplier",
        values="portfolio_contribution",
    ).sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    image = ax.imshow(grid.to_numpy(), cmap="YlGn", aspect="auto")
    ax.set_xticks(
        np.arange(len(grid.columns)),
        [f"{value:.1f}x" for value in grid.columns],
    )
    ax.set_yticks(np.arange(len(grid.index)), [f"{value:.1f}x" for value in grid.index])
    ax.set_xlabel("Membership-fee revenue multiplier")
    ax.set_ylabel("Benefit + service cost multiplier")
    ax.set_title("Portfolio contribution sensitivity")
    for row_index in range(len(grid.index)):
        for column_index in range(len(grid.columns)):
            value = grid.iloc[row_index, column_index]
            ax.text(
                column_index,
                row_index,
                f"{value:,.0f}",
                ha="center",
                va="center",
                color="white" if value > grid.to_numpy().mean() else "#17202A",
                fontsize=9,
            )
    fig.colorbar(image, ax=ax, label="Portfolio contribution")
    fig.tight_layout()
    fig.savefig(figure_dir / "pnl_sensitivity.png", dpi=150)
    plt.close(fig)
