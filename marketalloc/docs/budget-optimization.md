# Budget optimization methodology

The optimizer intentionally avoids allocating the entire budget to the single highest ROAS channel. It evaluates historical efficiency, conversion quality, and minimum/maximum constraints across the portfolio.

## Allocation method

The optimizer validates channel names and allocation bounds, starts from minimum allocations, then distributes the remaining amount in deterministic increments. For each increment it evaluates a marginal-return score based on historical ROAS, inverse CAC, and conversion rate. An exponential diminishing-return factor reduces a channel's marginal score as its allocation grows. A stable channel ordering breaks ties.

To avoid a single-channel recommendation, the default maximum is 40% of the total for portfolios with three or more channels, or 50% for two channels. A user-provided maximum overrides that default for the named channel. All channel maxima must jointly accommodate the complete requested budget; minimums may not exceed maximums or the total.

## Inputs

- historical ROAS
- CAC
- conversion rate
- current allocation
- revenue contribution
- channel efficiency
- minimum and maximum caps
- diminishing-return assumptions

## Outputs

The optimizer produces projected values for conversions, revenue, ROAS, ROI, and CAC. All future-oriented values are clearly labelled as projected or estimated to prevent misuse as actual business results.

Projected revenue uses an integrated exponential response curve anchored to historical ROAS. Projected conversions use observed CAC when available and otherwise use the historical conversion rate. These are deterministic scenario estimates, not guarantees or observed outcomes.
