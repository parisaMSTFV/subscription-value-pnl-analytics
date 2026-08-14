from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .analysis import (
    build_customer_period,
    build_monthly_member_trend,
    build_segment_performance,
)
from .decision_evidence import (
    build_decision_metrics,
    build_pnl_sensitivity,
    build_renewal_cohorts,
)
from .portfolio import build_portfolio_pnl
from .renewal import build_renewal_detail, build_renewal_summary
from .reporting import (
    write_decision_figures,
    write_decision_report,
    write_metrics,
    write_summary,
)
from .synthetic import generate_synthetic_inputs


def _write_report_csv(table: pd.DataFrame, path: Path) -> None:
    """Write stable numeric evidence across supported Python/NumPy versions."""
    table.to_csv(path, index=False, float_format="%.8f")


def run_analysis(
    activity: pd.DataFrame,
    subscriptions: pd.DataFrame,
    output_dir: str | Path,
    start: str,
    end_exclusive: str,
    as_of_date: str,
) -> dict[str, pd.DataFrame]:
    customer_period = build_customer_period(activity, start, end_exclusive)
    segment_performance = build_segment_performance(customer_period)
    portfolio_pnl = build_portfolio_pnl(
        activity,
        subscriptions,
        start,
        end_exclusive,
    )
    renewal_detail = build_renewal_detail(subscriptions, as_of_date)
    renewal_summary = build_renewal_summary(renewal_detail)
    monthly_member_trend = build_monthly_member_trend(
        activity,
        start,
        end_exclusive,
    )

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    tables = {
        "customer_period": customer_period,
        "segment_performance": segment_performance,
        "portfolio_pnl": portfolio_pnl,
        "renewal_detail": renewal_detail,
        "renewal_summary": renewal_summary,
        "monthly_member_trend": monthly_member_trend,
    }
    for name, table in tables.items():
        table.to_csv(output / f"{name}.csv", index=False)
    write_summary(
        output / "summary.md",
        portfolio_pnl,
        renewal_summary,
        segment_performance,
    )
    return tables


def write_decision_evidence(
    tables: dict[str, pd.DataFrame],
    reports_dir: str | Path,
) -> dict[str, float | int | str]:
    reports = Path(reports_dir)
    figures = reports / "figures"
    reports.mkdir(parents=True, exist_ok=True)
    renewal_cohorts = build_renewal_cohorts(tables["renewal_detail"])
    sensitivity = build_pnl_sensitivity(tables["portfolio_pnl"])
    metrics = build_decision_metrics(
        tables["portfolio_pnl"],
        tables["renewal_summary"],
        tables["segment_performance"],
        tables["monthly_member_trend"],
        sensitivity,
    )
    _write_report_csv(renewal_cohorts, reports / "renewal_cohorts.csv")
    _write_report_csv(sensitivity, reports / "pnl_sensitivity.csv")
    _write_report_csv(tables["portfolio_pnl"], reports / "portfolio_pnl.csv")
    _write_report_csv(tables["renewal_summary"], reports / "renewal_summary.csv")
    _write_report_csv(
        tables["monthly_member_trend"], reports / "monthly_member_trend.csv"
    )
    write_metrics(reports / "metrics.json", metrics)
    write_decision_report(reports / "decision_report.md", metrics)
    write_decision_figures(
        figures,
        tables["portfolio_pnl"],
        tables["monthly_member_trend"],
        renewal_cohorts,
        sensitivity,
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze subscription value, renewal, and portfolio P&L."
    )
    parser.add_argument(
        "command",
        choices=("generate", "analyze", "demo"),
        nargs="?",
        default="demo",
    )
    parser.add_argument("--data-dir", default="data/sample")
    parser.add_argument("--output-dir", default="artifacts")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--start", default="2025-07-01")
    parser.add_argument("--end", default="2025-10-01")
    parser.add_argument("--as-of", default="2026-01-01")
    parser.add_argument("--customers", type=int, default=1_200)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if args.command in {"generate", "demo"}:
        generate_synthetic_inputs(
            data_dir,
            n_customers=args.customers,
            seed=args.seed,
        )
        if args.command == "generate":
            print(f"Synthetic inputs written to {data_dir.resolve()}")
            return

    activity_path = data_dir / "activity_daily.csv"
    subscriptions_path = data_dir / "subscriptions.csv"
    if not activity_path.exists() or not subscriptions_path.exists():
        raise FileNotFoundError(
            "Expected activity_daily.csv and subscriptions.csv in "
            f"{data_dir.resolve()}."
        )

    activity = pd.read_csv(activity_path)
    subscriptions = pd.read_csv(subscriptions_path)
    tables = run_analysis(
        activity,
        subscriptions,
        args.output_dir,
        args.start,
        args.end,
        args.as_of,
    )
    write_decision_evidence(tables, args.reports_dir)
    pnl = tables["portfolio_pnl"].iloc[0]
    renewal = tables["renewal_summary"].iloc[0]
    print(f"Active members: {int(pnl['active_members']):,}")
    print(f"Member orders: {int(pnl['member_orders']):,}")
    print(f"Portfolio contribution: {pnl['portfolio_contribution']:,.2f}")
    print(f"Renewal rate: {renewal['renewal_rate']:.1%}")
    print(f"Reports written to {Path(args.output_dir).resolve()}")
    print(f"Decision evidence written to {Path(args.reports_dir).resolve()}")


if __name__ == "__main__":
    main()
