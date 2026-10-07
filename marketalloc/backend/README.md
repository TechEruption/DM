# MARKETALLOC Backend

This directory contains the Python/FastAPI backend for the MARKETALLOC application. The backend is a PostgreSQL-backed marketing attribution and budget optimization service that exposes deterministic, explainable APIs for analytics, conversion tracking, customer journeys, and scenario planning.

## Project overview

MARKETALLOC helps teams evaluate marketing performance using multi-touch attribution, campaign analytics, funnel analysis, and explainable budget recommendations. The backend is intentionally deterministic, without black-box ML or AI-powered scoring.

## Architecture

- FastAPI application entry point: `app/main.py`
- Environment/configuration: `app/core/config.py`
- SQLAlchemy session and engine: `app/core/database.py`
- Models: `app/models/`
- Schemas: `app/schemas/`
- Services: `app/services/`
- Repositories: `app/repositories/`
- CSV import + seed data: `app/utils/` and `app/seed/`
- API routes: `app/api/`

## Technology stack

- Python 3.11+
- FastAPI
- Pydantic + Pydantic Settings
- SQLAlchemy
- PostgreSQL
- Uvicorn
- Pandas / NumPy
- python-multipart
- pytest

## Features

- Multi-touch attribution: first touch, last touch, linear, time decay, and position-based
- Customer journey timeline builder
- Dashboard KPIs and trends
- Channel and campaign analytics
- Budget optimizer with constrained, explainable allocation logic
- Scenario simulator for multiple budget cases
- Funnel analysis with stage leakage reporting
- Insight engine based on deterministic rules
- CSV upload validation for supported marketing datasets
- Swagger/OpenAPI documentation

## Prerequisites

1. Install Python 3.11 or later.
2. Create a Supabase project and have its PostgreSQL database password available.
3. Use the PostgreSQL connection URI from the Supabase Dashboard's **Connect** panel.

The backend uses SQLAlchemy and PostgreSQL directly. A Supabase REST URL (`/rest/v1/...`) and Supabase anon/service-role API keys are not database connection credentials and are not used by this backend.

## Python virtual environment

From the backend directory:

```powershell
cd D:\NewProject\digital_marketing\marketalloc\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If execution policy blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configure environment variables

Copy the example config:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and replace `YOUR_DATABASE_PASSWORD` with the database password from Supabase. The project reference in the example is based on the supplied project URL:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_DATABASE_PASSWORD@db.jzuqjibyqpcoxjmyuqoe.supabase.co:5432/postgres?sslmode=require
CORS_ORIGINS=["http://localhost:5173"]
APP_ENV=development
```

Prefer copying the exact URI shown under **Connect** in Supabase if it provides a pooler URI or a different host/username for your project. Keep `sslmode=require`. Percent-encode reserved URL characters in the password. Do not use an anon key or service-role key in `DATABASE_URL`, and do not commit `.env` or share database credentials.

## Database initialization

If you want to initialize the database tables manually, run:

```powershell
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

The application also includes a reliable demo seeding workflow through the seed script.

## Seed demo data

From the backend directory:

```powershell
python -m app.seed.seed_database
```

This script creates the required tables if absent and inserts the demo dataset. It is designed to be idempotent by stable key checks and avoids duplicate inserts.

Expected seeded dataset characteristics:

- multiple months
- 100+ customers
- multiple campaigns
- multiple channels
- multi-touch and single-touch journeys
- converting and non-converting journeys
- realistic spend, impressions, clicks, sessions, leads, conversions, and revenue

## Start FastAPI

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Swagger and docs

Open the API documentation in a browser:

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Verify health endpoint

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

The response should return a status indicating the API is healthy and the PostgreSQL database is connected.

## Connect the frontend

Run the Vite frontend separately from the project root, then point it at the backend API:

```powershell
cd ..\frontend
npm install
npm run dev
```

The frontend should target http://localhost:8000 unless overridden by `VITE_API_BASE_URL`.

## API overview

Key routes include:

- `GET /api/health`
- `GET /api/dashboard/summary`
- `GET /api/dashboard/trends`
- `GET /api/channels`
- `GET /api/channels/{channel_id}`
- `GET /api/campaigns`
- `GET /api/campaigns/{campaign_id}`
- `GET /api/customers/{customer_id}/journey`
- `POST /api/attribution/calculate`
- `GET /api/attribution/results`
- `GET /api/attribution/compare`
- `POST /api/budget/optimize`
- `POST /api/budget/scenario`
- `GET /api/funnel`
- `GET /api/insights`
- `POST /api/data/upload`

## Testing

Run the backend tests:

```powershell
python -m pytest
```

If plugin autoload interferes in a local environment, use:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -m pytest
```

## Troubleshooting

- PostgreSQL connection refused: check that `DATABASE_URL` matches the PostgreSQL URI in Supabase's **Connect** panel and that the project is active.
- Authentication failed: use the database password, not the Supabase anon or service-role API key. Reset the database password in Supabase if it is unknown.
- Direct connection unavailable: try the session pooler connection URI provided by Supabase, especially on networks that do not support IPv6.
- Missing tables: run `python -m app.seed.seed_database`.
- Swagger not loading: ensure FastAPI is running on the expected port and the app imports cleanly.
- Import or dependency issues: recreate the virtual environment and reinstall dependencies.

## Notes

- The demo data is explicitly labelled as `DEMO DATASET` and is intended for local development and frontend validation.
- Future budget values are labelled `Projected / Estimated` so they are not confused with historical actual results.
- This backend uses deterministic calculations and explainable logic rather than black-box ML models.
