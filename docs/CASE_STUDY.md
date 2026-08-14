# Case Study Design

## Decision context

A subscription team needs one view that connects customer behavior to the
economics of the portfolio. Fee revenue alone is incomplete, while order volume
alone does not show whether benefits and service costs are affordable.

This case study combines three grains of data:

1. customer-day activity and direct cost;
2. subscription-plan revenue and duration;
3. the latest RFM segment available in the analysis period.

## Analysis flow

### 1. Build the customer-period table

Each customer-day is counted once inside a fixed analysis period. Customers are
classified as:

- `active_member`: membership was active on at least one day in the period;
- `lapsed_member`: membership ended before the period;
- `never_member`: no membership activity was observed up to the period end.

The table keeps order, item, NMV, margin, and direct-cost totals at customer
level so every segment aggregate can be audited.

### 2. Reconcile the member portfolio P&L

Only activity recorded on active membership days enters the operating P&L.
Subscription fees are allocated by the number of plan days that overlap the
analysis period.

```text
portfolio contribution =
  allocated membership fee revenue
  + commerce PC1
  + shipping contribution
  - benefit cost
  - service cost
```

This makes the accounting boundary explicit and prevents a plan that overlaps
two reporting periods from being counted in full in both.

### 3. Measure renewal

A plan becomes eligible for renewal measurement only after its end date and the
full grace period have passed. A renewal is recorded when the next plan starts
between seven days before expiry and the end of the grace period.

### 4. Track the portfolio over time

The monthly table reports active members, orders, NMV, and operating
contribution. It is intended for trend review and investigation of changes in
member economics.

### 5. Separate membership-base movement from unit economics

The executed report compares active-member count with operating contribution
per active member. This prevents a decline in aggregate contribution from being
interpreted automatically as weaker per-member economics.

### 6. Stress fee and direct-cost assumptions

The sensitivity grid changes realized membership-fee revenue and combined
benefit/service cost from 0.8x to 1.2x. Commerce and shipping contribution stay
fixed. The grid is an arithmetic stress test, not a behavioral forecast.

## How to use the outputs

- Use `portfolio_pnl.csv` for period-level economics and reconciliation.
- Use `segment_performance.csv` to locate high-value or high-cost member groups.
- Use `renewal_summary.csv` to monitor retention of eligible plans.
- Use `monthly_member_trend.csv` to find months that need deeper diagnosis.
- Use `customer_period.csv` to trace every aggregate back to customer-level
  inputs.
- Use `reports/decision_report.md` for the executed operating interpretation.
- Use `reports/pnl_sensitivity.csv` to compare the configured fee/cost scenarios.

## Analytical boundary

The pipeline describes observed portfolio performance. Measuring the
incremental effect of membership requires a separate experimental or causal
design and is outside this case study.

The [input contract](INPUT_SCHEMA.md) defines the two accepted CSV files and the
temporal parameters used for period and renewal eligibility.
