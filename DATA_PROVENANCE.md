# Data Provenance

The committed run uses data created by
`subscription_value.synthetic.generate_synthetic_inputs`.

The generator creates:

- daily customer activity across multiple RFM segments;
- subscription plans with different start dates and durations;
- renewals with short gaps between consecutive plans;
- fee revenue, commerce margin, shipping contribution, and direct benefit
  costs.

Customer IDs, dates, prices, and financial results are synthetic. The fixed
random seed makes the run reproducible. Generated row-level files are excluded
from version control; aggregate reports and figures are committed.

`data/fixture/` contains nine fictional activity rows and three fictional plan
rows. The fixture verifies the external CSV contract in CI and is not the source
of the reported portfolio results.
