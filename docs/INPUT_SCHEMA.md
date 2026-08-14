# Input contract

The `analyze` command accepts two UTF-8 CSV files in the directory supplied
with `--data-dir`.

## `activity_daily.csv`

Grain: one row per customer and calendar day. Duplicate
`customer_id`–`day` pairs are rejected.

| Column | Type | Rule |
|---|---|---|
| `customer_id` | string or integer | Stable identifier within both input files |
| `day` | `YYYY-MM-DD` | Activity date |
| `rfm_segment` | string | Latest available segment label on that day |
| `membership_active` | `0` or `1` | Whether the plan is active on that day |
| `orders` | integer | Completed orders attributed to the day |
| `items` | integer | Completed items attributed to the day |
| `nmv` | number | Net merchandise value after cancellations and returns |
| `pc1` | number | First contribution margin on recorded activity |
| `shipping_contribution` | number | Shipping revenue less variable shipping cost |
| `benefit_cost` | number | Direct cost of membership benefits used that day |
| `service_cost` | number | Direct daily cost of serving the active plan |

All financial columns must use one consistent currency unit. Missing rows are
not interpreted as zero activity; upstream extraction must define and apply the
calendar coverage rule.

## `subscriptions.csv`

Grain: one row per subscription plan. Duplicate `subscription_id` values are
rejected.

| Column | Type | Rule |
|---|---|---|
| `subscription_id` | string | Unique plan identifier |
| `customer_id` | string or integer | Matches the activity file |
| `start_date` | `YYYY-MM-DD` | First active day, inclusive |
| `duration_days` | positive integer | Contract duration used to derive the exclusive plan end |
| `paid_price` | non-negative number | Realized plan revenue before period allocation |
| `plan_name` | string, optional | Human-readable plan type |

## Temporal parameters

- `--start` is the first included activity date.
- `--end` is exclusive.
- `--as-of` is the latest date considered observable for renewal eligibility.
- A renewal is eligible only when the plan end plus the complete grace period
  falls on or before `--as-of`.

The committed files under `data/fixture/` provide a small integration example.
They are designed to verify the contract, not to represent portfolio results.
