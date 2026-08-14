from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from subscription_value.cli import run_analysis, write_decision_evidence
from subscription_value.synthetic import generate_synthetic_inputs


def test_demo_runs_end_to_end() -> None:
    with TemporaryDirectory() as temporary_dir:
        root = Path(temporary_dir)
        data_dir = root / "data"
        output_dir = root / "artifacts"
        reports_dir = root / "reports"
        activity, subscriptions = generate_synthetic_inputs(
            data_dir,
            n_customers=120,
            seed=11,
        )
        tables = run_analysis(
            activity,
            subscriptions,
            output_dir,
            "2025-07-01",
            "2025-10-01",
            "2026-01-01",
        )
        metrics = write_decision_evidence(tables, reports_dir)

        assert subscriptions["start_date"].nunique() > 1
        assert tables["portfolio_pnl"].loc[0, "active_members"] > 0
        assert not tables["segment_performance"].empty
        assert not tables["monthly_member_trend"].empty
        assert metrics["eligible_subscriptions"] > 0
        assert (output_dir / "summary.md").exists()
        assert (reports_dir / "decision_report.md").exists()
        assert (reports_dir / "figures" / "pnl_components.png").exists()
