# Architecture overview

This project is designed around a clean three-layer software architecture: frontend, API, and data/analytics services. The platform keeps the business logic deterministic, explainable, and tightly coupled to clear stage boundaries so that attribution and budget recommendations remain auditable.

## Layers

### Frontend
The React + Vite + TypeScript frontend is responsible for dashboard navigation, filters, charts, and SaaS reporting surfaces.

### API layer
FastAPI routers provide request validation, endpoint organization, and the stable contract between the UI and backend services.

### Service layer
The service layer handles deterministic calculations for attribution, metrics, budget optimization, and funnel analysis.

### Repository layer
Repositories isolate database queries and allow SQLAlchemy-specific access without leaking implementation details to business logic modules.

### Persistence layer
PostgreSQL stores all source data, scenario records, and final attribution outputs.

## Request flow

A UI page requests data from the API using a focused service wrapper. The router validates input, calls the appropriate service, and returns normalized JSON. The frontend converts payloads into charts and KPI cards.
