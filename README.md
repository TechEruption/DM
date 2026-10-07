# MARKETALLOC

**Multi-Touch Marketing Attribution & Budget Optimization Platform**

MARKETALLOC provides deterministic marketing analytics, multi-touch attribution, explainable budget allocation, funnel reporting, and insights. Its FastAPI backend uses PostgreSQL; the React/Vite frontend runs separately.

## Architecture

```text
React + Vite frontend :5173
          |
       FastAPI :8000
          |
  SQLAlchemy + psycopg
          |
  Supabase PostgreSQL
```

## Technology

- Backend: Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Pandas, NumPy
- Frontend: React, TypeScript, Vite
- Testing: pytest

## Database configuration (Supabase)

Create/open the Supabase project and copy its PostgreSQL connection URI from the dashboard's **Connect** panel. This application connects to PostgreSQL through SQLAlchemy. A Supabase REST endpoint ending in `/rest/v1/...` and anon/service-role API keys are not PostgreSQL connection details.

In PowerShell, copy the backend template:

```powershell
cd D:\NewProject\digital_marketing\marketalloc\backend
Copy-Item .env.example .env
```

Edit `backend\.env` and replace `YOUR_DATABASE_PASSWORD` with the database password from Supabase:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_DATABASE_PASSWORD@db.jzuqjibyqpcoxjmyuqoe.supabase.co:5432/postgres?sslmode=require
CORS_ORIGINS=["http://localhost:5173"]
APP_ENV=development
```

Use the exact PostgreSQL URI in the Supabase **Connect** panel if it provides a different host, username, or session-pooler URI. Keep SSL enabled. Percent-encode reserved URL characters in the password. Do not use or share a Supabase API key as the database password. Never commit `.env`.

## Run the backend (Windows)

```powershell
cd D:\NewProject\digital_marketing\marketalloc\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app.seed.seed_database
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The seed command creates SQLAlchemy tables and inserts the idempotent, explicitly labelled `DEMO DATASET`. Confirm connectivity at `http://localhost:8000/api/health`.

## Run the frontend

In another PowerShell window:

```powershell
cd D:\NewProject\digital_marketing\marketalloc\frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend API client defaults to `http://localhost:8000`. The backend allows the Vite origin by default.

## API and documentation

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Health: `GET /api/health`
- Analytics: `/api/dashboard`, `/api/channels`, `/api/campaigns`
- Attribution: `/api/attribution`
- Budget: `/api/budget`
- Other: `/api/customers`, `/api/funnel`, `/api/insights`, `/api/data/upload`

## Tests and build

```powershell
cd D:\NewProject\digital_marketing\marketalloc\backend
python -m pytest
```

```powershell
cd D:\NewProject\digital_marketing\marketalloc\frontend
npm run build
```

## Methodology and limitations

Attribution supports first-touch, last-touch, linear, time-decay, and position-based models. Budget recommendations use deterministic historical metrics and diminishing-return estimates; future values are labelled **Projected / Estimated**, not actual revenue. Demo records are synthetic and intended for development and evaluation, not business reporting. No AI or black-box ML is used.
