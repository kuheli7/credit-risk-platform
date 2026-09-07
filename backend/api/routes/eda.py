"""EDA and business insights API routes."""

from fastapi import APIRouter
from backend.services.eda_service import EDAService

router = APIRouter(prefix="/api/eda", tags=["eda"])
eda_service = EDAService()

@router.get("/insights")
def get_insights():
    """Returns all 5 business insights with Chart.js-compatible dataset specifications."""
    return eda_service.get_business_insights()

@router.get("/categories")
def get_categories():
    """Returns architectural feature categorization across the 4 banking domains."""
    return eda_service.get_feature_categories()

@router.get("/data-quality")
def get_data_quality():
    """Returns missing value audit and dataset anomaly correction details."""
    return eda_service.get_data_quality()

@router.get("/portfolio")
def get_portfolio():
    """Returns high-level portfolio volume and default rate breakdown."""
    return eda_service.get_overview_metrics()["portfolio"]
