import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api import attribution, budget, campaigns, channels, customers, dashboard, data, funnel, insights
from app.core.config import settings
from app.core.database import engine
from app.models import AttributionResult, BudgetScenario, Campaign, Channel, Conversion, Customer, Touchpoint

logger = logging.getLogger("marketalloc")

app = FastAPI(
    title="MARKETALLOC",
    version="1.0.0",
    description=(
        "Multi-Touch Marketing Attribution & Budget Optimization Platform. "
        "All attribution and budget estimates are deterministic and explainable."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    dashboard.router,
    attribution.router,
    channels.router,
    campaigns.router,
    customers.router,
    budget.router,
    funnel.router,
    insights.router,
    data.router,
):
    app.include_router(router)


@app.get("/api/health", tags=["system"], summary="Check API and PostgreSQL health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        logger.exception("Health check database connection failed")
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "service": "marketalloc-backend", "database": "unavailable"},
        )
    return {"status": "ok", "service": "marketalloc-backend", "database": "connected"}


@app.exception_handler(ValueError)
async def invalid_request_handler(request: Request, error: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(error)})


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, error: SQLAlchemyError):
    logger.exception("Database operation failed", exc_info=error)
    return JSONResponse(status_code=500, content={"detail": "A database operation failed."})


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, error: Exception):
    logger.exception("Unexpected API error", exc_info=error)
    return JSONResponse(status_code=500, content={"detail": "An unexpected server error occurred."})
