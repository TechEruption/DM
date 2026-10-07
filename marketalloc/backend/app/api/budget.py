from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models import BudgetScenario
from app.schemas.budget import BudgetOptimizationRequest, BudgetScenarioRequest
from app.schemas.budget import BudgetOptimizationResponse, SavedRecommendationsResponse
from app.services.attribution_engine import normalize_model
from app.services.budget_optimizer import optimize_budget
from app.services.performance_service import channel_rows

router = APIRouter(prefix="/api/budget", tags=["budget"])


def _run_optimization(payload: BudgetOptimizationRequest, db: Session):
    try:
        model = normalize_model(payload.attribution_model)
        channels = channel_rows(db, model=model)
        if not any(row["spend"] > 0 or row["conversions"] > 0 for row in channels):
            raise ValueError("No channel performance data is available. Seed or import a dataset first.")
        result = optimize_budget(
            channels,
            payload.total_budget,
            min_allocations=payload.min_allocations,
            max_allocations=payload.max_allocations,
        )
        result["attribution_model"] = model
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _save_scenario(db: Session, name: str, payload: BudgetOptimizationRequest, result: dict):
    scenario = BudgetScenario(
        name=name,
        attribution_model=result["attribution_model"],
        total_budget=Decimal(str(result["total_budget"])),
        constraints={
            "min_allocations": payload.min_allocations,
            "max_allocations": payload.max_allocations,
        },
        results=result,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.post("/optimize", summary="Generate deterministic budget allocation recommendations", response_model=BudgetOptimizationResponse)
def optimize(payload: BudgetOptimizationRequest, db: Session = Depends(get_db_session)):
    result = _run_optimization(payload, db)
    scenario = _save_scenario(db, "Budget optimization", payload, result)
    result["scenario_id"] = scenario.id
    return result


@router.post("/scenario", summary="Simulate and save a budget scenario", response_model=BudgetOptimizationResponse)
def simulate(payload: BudgetScenarioRequest, db: Session = Depends(get_db_session)):
    result = _run_optimization(payload, db)
    result["scenario_name"] = payload.scenario_name
    scenario = _save_scenario(db, payload.scenario_name, payload, result)
    result["scenario_id"] = scenario.id
    return result


@router.get("/recommendations", summary="Get latest saved budget recommendations", response_model=SavedRecommendationsResponse)
def recommendations(db: Session = Depends(get_db_session)):
    scenario = db.query(BudgetScenario).order_by(BudgetScenario.created_at.desc(), BudgetScenario.id.desc()).first()
    if scenario is None:
        return {"recommendations": [], "message": "No saved budget scenarios yet."}
    return {
        "scenario_id": scenario.id,
        "scenario_name": scenario.name,
        "created_at": scenario.created_at,
        "recommendations": scenario.results.get("channels", []),
        "projected": {
            key: scenario.results.get(key)
            for key in ("projected_revenue", "projected_conversions", "projected_roas", "projected_roi", "projected_cac")
        },
    }
