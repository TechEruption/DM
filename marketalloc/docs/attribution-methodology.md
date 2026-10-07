# Attribution methodology

The platform supports five attribution models: first touch, last touch, linear, time decay, and position-based. Each model distributes credit across the marketing journey while normalizing to exactly 100% of conversion value per journey.

## Model definitions

- First touch: 100% of revenue is assigned to the first eligible touchpoint.
- Last touch: 100% is assigned to the last eligible touchpoint.
- Linear: credit is split evenly across all touchpoints in the journey.
- Time decay: more recent interactions receive greater weight according to a configurable decay parameter.
- Position-based: default allocation is 40% first touch, 40% last touch, and the remaining 20% shared across middle touchpoints.

## Implementation policy

Each attribution run is deterministic and normalizes touchpoint shares to exactly 100%. Single-touch journeys receive full credit. Two-touch position-based journeys split first/last weights proportionally. Missing channel labels are retained in an `Unknown` channel bucket; a conversion with no recorded touchpoints also receives 100% `Unknown` credit so conversion value is not silently dropped. Duplicate timestamps are resolved with a stable touchpoint identifier ordering.

Attribution revenue is persisted per conversion, model, and touchpoint. Unfiltered default-model runs can reuse persisted results; importing new records invalidates the cache.
