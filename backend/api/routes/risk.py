"""Risk scoring and SHAP explainability API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from backend.services.risk_service import RiskService

router = APIRouter(prefix="/api/risk", tags=["risk"])
risk_service = RiskService()

class ApplicantEvaluationRequest(BaseModel):
    AMT_INCOME_TOTAL: float = Field(..., example=150000.0)
    AMT_CREDIT: float = Field(..., example=500000.0)
    AMT_ANNUITY: float = Field(..., example=25000.0)
    AMT_GOODS_PRICE: Optional[float] = Field(None, example=480000.0)
    NAME_CONTRACT_TYPE: Optional[str] = Field("Cash loans", example="Cash loans")
    CODE_GENDER: Optional[str] = Field("M", example="M")
    NAME_INCOME_TYPE: Optional[str] = Field("Working", example="Working")
    NAME_EDUCATION_TYPE: Optional[str] = Field("Higher education", example="Higher education")
    OCCUPATION_TYPE: Optional[str] = Field("Laborers", example="Laborers")
    AGE: Optional[float] = Field(35.0, example=35.0)
    YEARS_EMPLOYED: Optional[float] = Field(4.0, example=4.0)
    EXT_SOURCE_2: Optional[float] = Field(0.50, example=0.50)
    EXT_SOURCE_3: Optional[float] = Field(0.50, example=0.50)
    BUREAU_ACTIVE_LOANS: Optional[float] = Field(1.0, example=1.0)
    PREV_APP_REFUSED_RATE: Optional[float] = Field(0.0, example=0.0)

@router.get("/presets")
def get_applicant_presets():
    """Returns pre-configured applicant archetypes (Prime, Borderline, High-Risk)."""
    return risk_service.get_presets()

@router.get("/samples")
def get_sample_applicants():
    """Returns verified historical applicant IDs from the credit risk database."""
    return risk_service.get_sample_applicant_ids()

@router.get("/lookup/{sk_id}")
def lookup_applicant(sk_id: int):
    """Looks up a real historical applicant record by SK_ID_CURR."""
    res = risk_service.lookup_applicant(sk_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Applicant SK_ID_CURR {sk_id} not found in database.")
    return res

@router.post("/predict")
def evaluate_applicant(payload: ApplicantEvaluationRequest):
    """Evaluates applicant credit default risk, calculates SHAP drivers, and provides underwriting recommendation."""
    try:
        data_dict = payload.model_dump()
        result = risk_service.evaluate_applicant(data_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk evaluation error: {str(e)}")
