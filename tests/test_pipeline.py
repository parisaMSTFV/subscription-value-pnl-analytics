from __future__ import annotations

from subscription_value.cli import run_analysis
from subscription_value.synthetic import generate_synthetic_inputs


def test_demo_runs_end_to_end(tmp_path) -> None:
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "reports"
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

    assert subscriptions["start_date"].nunique() > 1
    assert tables["portfolio_pnl"].loc[0, "active_members"] > 0
    assert not tables["segment_performance"].empty
    assert not tables["monthly_member_trend"].empty
    assert (output_dir / "summary.md").exists()
