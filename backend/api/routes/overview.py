"""Overview API route."""

from fastapi import APIRouter
from backend.services.eda_service import EDAService

router = APIRouter(prefix="/api/overview", tags=["overview"])
eda_service = EDAService()

@router.get("")
def get_overview():
    """Returns top-level model metrics, portfolio overview, and summary statistics."""
    metrics = eda_service.get_overview_metrics()
    insights = eda_service.get_business_insights()
    
    # Return all 6 executive insight cards for overview
    return {
        "metrics": metrics,
        "key_insights": [
            {
                "id": ins["id"],
                "number": ins["number"],
                "title": ins["title"],
                "summary": ins["summary"],
                "metric": ins["metrics"][0],
                "policy": ins.get("policy_recommendation", "")
            }
            for ins in insights[:6]
        ]
    }
