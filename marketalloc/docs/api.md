# API contract overview

The backend exposes a set of structured routes for dashboard analytics, customer journeys, attribution calculations, channel and campaign views, scenario simulation, funnel analysis, and marketing insights.

## Core endpoints

- GET /api/health
- GET /api/dashboard/summary
- GET /api/dashboard/trends
- GET /api/channels
- GET /api/channels/{channel_id}
- GET /api/campaigns
- GET /api/campaigns/{campaign_id}
- GET /api/customers/{customer_id}/journey
- POST /api/attribution/calculate
- GET /api/attribution/results
- GET /api/attribution/compare
- POST /api/budget/optimize
- POST /api/budget/scenario
- GET /api/budget/recommendations
- GET /api/funnel
- GET /api/insights
- POST /api/data/upload

## Common filters and payloads

Analytics endpoints accept `date_from` and `date_to` in `YYYY-MM-DD` form where applicable. Channel selectors use the channel integer ID; campaign selectors accept the stable string `campaign_id` returned by campaign endpoints. Attribution uses `attribution_model` (`first_touch`, `last_touch`, `linear`, `time_decay`, or `position_based`); the calculate body also accepts the alias `model`, configurable `decay_parameter`, and position weights.

`POST /api/budget/optimize` and `POST /api/budget/scenario` accept `total_budget`, `attribution_model`, and optional `min_allocations` / `max_allocations` maps keyed by channel name. Their future figures are labelled `Projected / Estimated`.

`POST /api/data/upload` is multipart form data with `dataset_type` (`channels`, `campaigns`, `customers`, or `touchpoints`) and a `.csv` file. Import channels before campaigns, customers before touchpoints, and campaigns before touchpoints that reference campaigns. Validation errors identify missing/invalid fields and unknown references.

All documented routes expose Pydantic response schemas in Swagger. The API returns 400 for malformed CSV or business-rule inputs, 404 for missing resources, 422 for request schema validation, and a sanitized 500 for unexpected database/server errors.
