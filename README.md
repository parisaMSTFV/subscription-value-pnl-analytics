# DigiPlus Subscription Value & P&L Case Study

This project turns subscription activity, plan revenue, and direct cost data
into an operating view of member value.

It is designed around four business questions:

- Which member segments generate the strongest order and margin contribution?
- How do membership fees and direct benefit costs reconcile at portfolio level?
- What share of eligible subscriptions renew within the agreed grace period?
- How do active-member economics change month by month?

## What the pipeline produces

| Output | Decision supported |
|---|---|
| `portfolio_pnl.csv` | Reconciles fee revenue, commerce margin, shipping contribution, and direct costs |
| `segment_performance.csv` | Profiles active, lapsed, and never-member customers by RFM segment |
| `renewal_summary.csv` | Tracks eligible plans, renewed plans, renewal rate, and renewal timing |
| `monthly_member_trend.csv` | Shows active members, orders, NMV, and contribution over time |
| `customer_period.csv` | Provides the customer-level audit table behind the aggregates |
| `summary.md` | Collects the main period results in a short business readout |

The P&L is built from observed member activity and directly recorded costs. It
is a portfolio performance view, not an estimate of incremental impact.

## Run the case study

```bash
python -m pip install -e ".[dev]"
digiplus-case demo
```

The demo creates a reproducible synthetic dataset, runs the full analysis, and
writes the outputs to `artifacts/`.

To run the pipeline on another dataset:

```bash
digiplus-case analyze \
  --data-dir path/to/input \
  --output-dir path/to/output \
  --start 2025-07-01 \
  --end 2025-10-01 \
  --as-of 2026-01-01
```

## Project structure

```text
src/digiplus_case/     analysis pipeline and synthetic data generator
tests/                 metric, reconciliation, and end-to-end tests
docs/                  case-study design and metric definitions
sql/                   warehouse extraction contract
```

## Validation

```bash
pytest -q
ruff check .
```

The public version contains no company data. See
[Data Provenance](DATA_PROVENANCE.md) for the synthetic-data design and
[Case Study Design](docs/CASE_STUDY.md) for the analytical decisions.
