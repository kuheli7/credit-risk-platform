"""Risk evaluation and SHAP explainability service."""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.ml.predict import RiskPredictor
from src.xai.explainer import CreditRiskExplainer
from src.utils.logger import logger

# Preset applicant archetypes
PRESET_APPLICANTS = {
    "prime_low_risk": {
        "id": "prime_low_risk",
        "name": "Prime Low Risk (Senior Software Executive)",
        "description": "High income, low debt-to-income, strong bureau scores, 0 past rejections.",
        "data": {
            "AMT_INCOME_TOTAL": 320000.0,
            "AMT_CREDIT": 600000.0,
            "AMT_ANNUITY": 24000.0,
            "AMT_GOODS_PRICE": 600000.0,
            "NAME_CONTRACT_TYPE": "Cash loans",
            "CODE_GENDER": "M",
            "NAME_INCOME_TYPE": "Commercial associate",
            "NAME_EDUCATION_TYPE": "Higher education",
            "OCCUPATION_TYPE": "Managers",
            "AGE": 38,
            "YEARS_EMPLOYED": 9.5,
            "EXT_SOURCE_2": 0.72,
            "EXT_SOURCE_3": 0.68,
            "BUREAU_ACTIVE_LOANS": 1.0,
            "PREV_APP_REFUSED_RATE": 0.0
        }
    },
    "borderline_risk": {
        "id": "borderline_risk",
        "name": "Borderline Risk (Mid-Career Sales Representative)",
        "description": "Moderate income, average bureau score, 25% past rejection history.",
        "data": {
            "AMT_INCOME_TOTAL": 140000.0,
            "AMT_CREDIT": 450000.0,
            "AMT_ANNUITY": 28000.0,
            "AMT_GOODS_PRICE": 420000.0,
            "NAME_CONTRACT_TYPE": "Cash loans",
            "CODE_GENDER": "F",
            "NAME_INCOME_TYPE": "Working",
            "NAME_EDUCATION_TYPE": "Secondary / secondary special",
            "OCCUPATION_TYPE": "Sales staff",
            "AGE": 29,
            "YEARS_EMPLOYED": 2.1,
            "EXT_SOURCE_2": 0.44,
            "EXT_SOURCE_3": 0.38,
            "BUREAU_ACTIVE_LOANS": 3.0,
            "PREV_APP_REFUSED_RATE": 0.25
        }
    },
    "high_risk_defaulter": {
        "id": "high_risk_defaulter",
        "name": "High Risk Defaulter (Overleveraged Driver)",
        "description": "High credit-to-income (7.2x), low bureau score (<0.20), 60% past rejections.",
        "data": {
            "AMT_INCOME_TOTAL": 90000.0,
            "AMT_CREDIT": 650000.0,
            "AMT_ANNUITY": 35000.0,
            "AMT_GOODS_PRICE": 580000.0,
            "NAME_CONTRACT_TYPE": "Cash loans",
            "CODE_GENDER": "M",
            "NAME_INCOME_TYPE": "Working",
            "NAME_EDUCATION_TYPE": "Secondary / secondary special",
            "OCCUPATION_TYPE": "Drivers",
            "AGE": 24,
            "YEARS_EMPLOYED": 0.7,
            "EXT_SOURCE_2": 0.18,
            "EXT_SOURCE_3": 0.15,
            "BUREAU_ACTIVE_LOANS": 5.0,
            "PREV_APP_REFUSED_RATE": 0.60
        }
    }
}

class RiskService:
    """Singleton service wrapping model scoring and SHAP explainability."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RiskService, cls).__new__(cls)
            cls._instance._init_service()
        return cls._instance

    def _init_service(self):
        logger.info("Initializing RiskService with LightGBM and SHAP...")
        self.predictor = RiskPredictor()
        self.explainer = CreditRiskExplainer()
        logger.info("RiskService initialization complete.")

    def get_presets(self) -> List[Dict[str, Any]]:
        return list(PRESET_APPLICANTS.values())

    def evaluate_applicant(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates an applicant and returns risk prediction + SHAP feature attributions."""
        income = float(input_data.get("AMT_INCOME_TOTAL", 150000.0))
        credit = float(input_data.get("AMT_CREDIT", 500000.0))
        annuity = float(input_data.get("AMT_ANNUITY", 25000.0))
        goods_price = float(input_data.get("AMT_GOODS_PRICE", credit))
        years_employed = float(input_data.get("YEARS_EMPLOYED", 3.0))
        age = float(input_data.get("AGE", 35.0))
        ext2 = float(input_data.get("EXT_SOURCE_2", 0.50))
        ext3 = float(input_data.get("EXT_SOURCE_3", 0.50))
        active_loans = float(input_data.get("BUREAU_ACTIVE_LOANS", 1.0))
        refused_rate = float(input_data.get("PREV_APP_REFUSED_RATE", 0.0))

        # Build full payload required by CreditRiskPreprocessor
        applicant_payload = {
            "AMT_INCOME_TOTAL": income,
            "AMT_CREDIT": credit,
            "AMT_ANNUITY": annuity,
            "AMT_GOODS_PRICE": goods_price,
            "NAME_CONTRACT_TYPE": input_data.get("NAME_CONTRACT_TYPE", "Cash loans"),
            "CODE_GENDER": input_data.get("CODE_GENDER", "M"),
            "FLAG_OWN_CAR": "Y" if years_employed > 3 else "N",
            "FLAG_OWN_REALTY": "Y",
            "CNT_CHILDREN": 0,
            "NAME_INCOME_TYPE": input_data.get("NAME_INCOME_TYPE", "Working"),
            "NAME_EDUCATION_TYPE": input_data.get("NAME_EDUCATION_TYPE", "Higher education"),
            "NAME_FAMILY_STATUS": "Married",
            "NAME_HOUSING_TYPE": "House / apartment",
            "REGION_POPULATION_RELATIVE": 0.02,
            "DAYS_BIRTH": -int(age * 365),
            "DAYS_EMPLOYED": -int(years_employed * 365),
            "DAYS_REGISTRATION": -2500,
            "DAYS_ID_PUBLISH": -1500,
            "OWN_CAR_AGE": 4.0,
            "OCCUPATION_TYPE": input_data.get("OCCUPATION_TYPE", "Laborers"),
            "CNT_FAM_MEMBERS": 2.0,
            "REGION_RATING_CLIENT": 2,
            "REGION_RATING_CLIENT_W_CITY": 2,
            "ORGANIZATION_TYPE": "Business Entity Type 3",
            "EXT_SOURCE_1": (ext2 + ext3) / 2.0,
            "EXT_SOURCE_2": ext2,
            "EXT_SOURCE_3": ext3,
            "BUREAU_ACTIVE_LOANS": active_loans,
            "PREV_APP_REFUSED_RATE": refused_rate
        }

        # 1. Run prediction
        prediction = self.predictor.predict_single(applicant_payload)
        prob = float(prediction["default_probability"])
        band = prediction["risk_band"]
        score = prediction["credit_score_proxy"]
        proc_features = pd.Series(prediction["processed_features"])

        # 2. Underwriting Policy Recommendation
        if band == "Low":
            decision = "APPROVED"
            policy_action = "Fast-track automated approval with standard prime pricing tier."
            badge_type = "low"
        elif band == "Medium":
            decision = "CONDITIONAL REVIEW"
            policy_action = "Require secondary proof of income, debt consolidation check, and maximum 3-year term."
            badge_type = "medium"
        else:
            decision = "DECLINED"
            policy_action = "Escalate to Special Assets & Risk Committee due to high default probability; request guarantor."
            badge_type = "high"

        # 3. Compute SHAP Top Drivers
        drivers = self.explainer.get_local_top_drivers(proc_features, top_k=10)
        
        risk_reducing = [d for d in drivers if d["shap_impact"] < 0]
        risk_increasing = [d for d in drivers if d["shap_impact"] > 0]

        # 4. Generate AI Business Explanation from real SHAP attributions
        top_increasing_names = [d["feature"].replace("_", " ") for d in risk_increasing[:2]]
        top_reducing_names = [d["feature"].replace("_", " ") for d in risk_reducing[:2]]

        narrative_parts = []
        if band == "Low":
            reducing_str = ", ".join(top_reducing_names) if top_reducing_names else "strong bureau ratings and solid repayment capacity"
            narrative_parts.append(f"This applicant demonstrates favorable credit quality with an estimated default probability of {prob*100:.1f}%.")
            narrative_parts.append(f"The primary positive drivers are {reducing_str}, keeping default risk well within prime underwriting thresholds.")
        elif band == "Medium":
            inc_str = ", ".join(top_increasing_names) if top_increasing_names else "moderate debt leverage"
            red_str = ", ".join(top_reducing_names) if top_reducing_names else "acceptable credit bureau score"
            narrative_parts.append(f"This applicant is classified as borderline/medium risk ({prob*100:.1f}% default probability).")
            narrative_parts.append(f"While {red_str} provides support, risk is elevated by {inc_str}. Secondary review is warranted.")
        else:
            inc_str = ", ".join(top_increasing_names) if top_increasing_names else "low external scores and high debt burden"
            narrative_parts.append(f"This applicant is classified as high default risk ({prob*100:.1f}% probability of delinquency).")
            narrative_parts.append(f"The primary adverse risk factors driving this assessment are {inc_str}, which severely breach standard lending risk appetite.")

        ai_explanation = " ".join(narrative_parts)

        return {
            "default_probability": round(prob, 4),
            "default_probability_pct": round(prob * 100, 2),
            "risk_band": band,
            "risk_badge": badge_type,
            "credit_score_proxy": score,
            "decision": decision,
            "policy_recommendation": policy_action,
            "credit_income_ratio": round(credit / max(income, 1), 2),
            "payment_rate_pct": round((annuity / max(credit, 1)) * 100, 2),
            "shap_drivers": drivers,
            "risk_increasing_factors": risk_increasing,
            "risk_reducing_factors": risk_reducing,
            "ai_explanation": ai_explanation
        }

    def lookup_applicant(self, sk_id: int) -> Optional[Dict[str, Any]]:
        """Looks up a real historical applicant record by SK_ID_CURR from SQLite analytics DB."""
        import sqlite3
        from src.utils.helpers import resolve_data_file
        db_path = resolve_data_file("credit_risk.db")
        if not db_path.exists():
            return None

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM applications WHERE SK_ID_CURR = ?", (sk_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return None

        # Count active bureau loans
        cur.execute("SELECT COUNT(*) FROM bureau WHERE SK_ID_CURR = ? AND CREDIT_ACTIVE = 'Active'", (sk_id,))
        active_loans = cur.fetchone()[0] or 0

        # Calculate previous application refusal rate
        cur.execute("SELECT COUNT(*), SUM(CASE WHEN NAME_CONTRACT_STATUS = 'Refused' THEN 1 ELSE 0 END) FROM previous_applications WHERE SK_ID_CURR = ?", (sk_id,))
        prev_row = cur.fetchone()
        total_prev = prev_row[0] or 0
        refused_prev = prev_row[1] or 0
        refused_rate = round(refused_prev / total_prev, 2) if total_prev > 0 else 0.0

        conn.close()

        days_birth = row["DAYS_BIRTH"] if row["DAYS_BIRTH"] is not None else -12000
        days_employed = row["DAYS_EMPLOYED"] if row["DAYS_EMPLOYED"] is not None else -1000
        age = round(abs(days_birth) / 365.25, 1)
        years_employed = round(abs(days_employed) / 365.25, 1) if days_employed < 0 else 0.0

        ext2 = float(row["EXT_SOURCE_2"]) if row["EXT_SOURCE_2"] is not None else 0.50
        ext3 = float(row["EXT_SOURCE_3"]) if row["EXT_SOURCE_3"] is not None else 0.50

        target = int(row["TARGET"]) if row["TARGET"] is not None else None
        target_label = "Defaulter (TARGET=1)" if target == 1 else "Non-Defaulter / Repaid (TARGET=0)"

        return {
            "sk_id_curr": sk_id,
            "actual_target": target,
            "actual_outcome": target_label,
            "data": {
                "AMT_INCOME_TOTAL": float(row["AMT_INCOME_TOTAL"] or 150000.0),
                "AMT_CREDIT": float(row["AMT_CREDIT"] or 500000.0),
                "AMT_ANNUITY": float(row["AMT_ANNUITY"] or 25000.0),
                "AMT_GOODS_PRICE": float(row["AMT_GOODS_PRICE"] or row["AMT_CREDIT"] or 500000.0),
                "NAME_CONTRACT_TYPE": str(row["NAME_CONTRACT_TYPE"] or "Cash loans"),
                "CODE_GENDER": str(row["CODE_GENDER"] or "M"),
                "NAME_INCOME_TYPE": str(row["NAME_INCOME_TYPE"] or "Working"),
                "NAME_EDUCATION_TYPE": str(row["NAME_EDUCATION_TYPE"] or "Secondary / secondary special"),
                "OCCUPATION_TYPE": str(row["OCCUPATION_TYPE"] or "Laborers"),
                "AGE": age,
                "YEARS_EMPLOYED": years_employed,
                "EXT_SOURCE_2": round(ext2, 4),
                "EXT_SOURCE_3": round(ext3, 4),
                "BUREAU_ACTIVE_LOANS": float(active_loans),
                "PREV_APP_REFUSED_RATE": float(refused_rate)
            }
        }

    def get_sample_applicant_ids(self) -> List[Dict[str, Any]]:
        """Returns verified sample applicant IDs representing both defaulters and solvent borrowers."""
        return [
            {"sk_id": 100002, "label": "SK 100002 (Defaulter)", "target": 1, "desc": "Laborer, high debt, Ext2 0.26"},
            {"sk_id": 100003, "label": "SK 100003 (Repaid)", "target": 0, "desc": "Core staff, higher education"},
            {"sk_id": 100004, "label": "SK 100004 (Repaid)", "target": 0, "desc": "Laborer, revolving loan"},
            {"sk_id": 100031, "label": "SK 100031 (Defaulter)", "target": 1, "desc": "Cooking staff, low bureau score"},
            {"sk_id": 100040, "label": "SK 100040 (Repaid)", "target": 0, "desc": "Core staff, commercial associate"}
        ]

