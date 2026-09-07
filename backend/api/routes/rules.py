"""Decision rules API route."""

from fastapi import APIRouter, Query
from typing import Optional
from backend.services.rules_service import RulesService

router = APIRouter(prefix="/api/rules", tags=["rules"])
rules_service = RulesService()

@router.get("")
def get_decision_rules(risk: Optional[str] = Query("all", description="Filter by risk tier: all, high, low")):
    """Returns credit policy decision rules derived from LightGBM splits and SHAP distributions."""
    return rules_service.get_rules(risk_filter=risk.lower() if risk else "all")
