# Metric Definitions

| Metric | Definition |
|---|---|
| `active_members` | Distinct customers with at least one active membership day |
| `member_days` | Distinct customer-days with active membership |
| `orders` | Orders recorded on the selected customer-days |
| `items` | Items recorded on the selected customer-days |
| `nmv` | Net merchandise value recorded on the selected customer-days |
| `commerce_pc1` | First contribution margin recorded on active membership days |
| `shipping_contribution` | Shipping revenue less variable shipping cost |
| `benefit_cost` | Direct cost of subscription benefits used by members |
| `service_cost` | Direct daily cost of serving active memberships |
| `membership_fee_revenue` | Plan fee allocated to days overlapping the period |
| `portfolio_contribution` | Fee revenue + PC1 + shipping contribution - benefit cost - service cost |
| `eligible_subscriptions` | Plans whose end date and full renewal grace period are observable |
| `renewed_subscriptions` | Eligible plans followed by a qualifying next plan |
| `renewal_rate` | Renewed subscriptions divided by eligible subscriptions |
| `order_frequency` | Orders divided by customers in the segment |
| `aov` | NMV divided by orders |

All financial fields use the same currency unit as the input data.
