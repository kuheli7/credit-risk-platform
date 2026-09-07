"""Decision rules service derived from LightGBM tree splits and SHAP values."""

from typing import Dict, Any, List, Optional
from src.xai.explainer import CreditRiskExplainer

class RulesService:
    """Service serving automated credit policy rules derived from machine learning."""

    def __init__(self):
        self.explainer = CreditRiskExplainer()

    def get_rules(self, risk_filter: Optional[str] = "all") -> Dict[str, Any]:
        all_rules = self.explainer.get_derived_decision_rules()
        
        # Count statistics
        high_count = sum(1 for r in all_rules if "HIGH" in r["risk_outcome"])
        med_count = sum(1 for r in all_rules if "MEDIUM" in r["risk_outcome"])
        low_count = sum(1 for r in all_rules if "LOW" in r["risk_outcome"])

        # Filter
        filtered_rules = []
        for r in all_rules:
            is_high = "HIGH" in r["risk_outcome"]
            is_med = "MEDIUM" in r["risk_outcome"]
            is_low = "LOW" in r["risk_outcome"]

            if risk_filter == "high" and not is_high:
                continue
            if risk_filter == "medium" and not is_med:
                continue
            if risk_filter == "low" and not is_low:
                continue
            
            rule_copy = dict(r)
            if is_high:
                rule_copy["risk_tier"] = "HIGH RISK"
                rule_copy["risk_type"] = "high"
            elif is_med:
                rule_copy["risk_tier"] = "MEDIUM RISK"
                rule_copy["risk_type"] = "medium"
            else:
                rule_copy["risk_tier"] = "LOW RISK"
                rule_copy["risk_type"] = "low"
            filtered_rules.append(rule_copy)

        methodology = [
            {"step": 1, "title": "Model Feature Splits", "desc": "LightGBM identifies optimal information gain thresholds across 144 engineered features."},
            {"step": 2, "title": "Feature Importance & SHAP", "desc": "TreeSHAP quantifies global non-linear impact and directional effect on default probability."},
            {"step": 3, "title": "Decision Boundaries", "desc": "High-confidence leaves are clustered to extract recurrent multi-variable decision paths."},
            {"step": 4, "title": "Business Rules", "desc": "Mathematical split expressions are synthesized into human-auditable IF/THEN logical statements."},
            {"step": 5, "title": "Underwriting Policy", "desc": "Credit committee binds enforceable credit underwriting mandates (caps, declines, guarantor demands)."}
        ]

        global_importance = self.explainer.get_global_feature_importance(top_k=10)

        return {
            "total_rules": len(all_rules),
            "high_risk_count": high_count,
            "medium_risk_count": med_count,
            "low_risk_count": low_count,
            "filter_applied": risk_filter,
            "rules": filtered_rules,
            "global_feature_importance": global_importance,
            "methodology": methodology
        }
