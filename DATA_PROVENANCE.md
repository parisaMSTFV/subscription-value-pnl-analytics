# Data Provenance

The public demo uses data created by
`subscription_value.synthetic.generate_synthetic_inputs`.

The generator creates:

- daily customer activity across multiple RFM segments;
- subscription plans with different start dates and durations;
- renewals with short gaps between consecutive plans;
- fee revenue, commerce margin, shipping contribution, and direct benefit
  costs.

Customer IDs, dates, prices, and financial results are synthetic. No row-level
company or customer data is included in this repository. The fixed random seed
makes the demo reproducible.
