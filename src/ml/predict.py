import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, Any, Union, Optional
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

from src.data.preprocessor import CreditRiskPreprocessor
from src.utils.config import MODEL_DIR
from src.utils.helpers import get_risk_band, get_risk_badge
from src.utils.logger import logger

class RiskPredictor:
    """Predictor for credit default probability and risk tiering."""

    def __init__(self, model_path: Optional[Path] = None, preprocessor_path: Optional[Path] = None):
        self.model_path = model_path or (MODEL_DIR / "lgbm_model.pkl")
        self.preprocessor_path = preprocessor_path or (MODEL_DIR / "preprocessor.pkl")
        self.model = None
        self.preprocessor = None
        self._load_artifacts()

    def _load_artifacts(self):
        """Loads serialized model and preprocessor."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {self.model_path}. Run training first.")
        if not self.preprocessor_path.exists():
            raise FileNotFoundError(f"Preprocessor artifact not found at {self.preprocessor_path}.")

        self.model = joblib.load(self.model_path)
        self.preprocessor = CreditRiskPreprocessor.load(self.preprocessor_path)
        logger.info("Successfully loaded model and preprocessor artifacts into RiskPredictor.")

    def predict_single(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs end-to-end inference on a single applicant payload."""
        df_single = pd.DataFrame([applicant_data])
        return self.predict_dataframe(df_single)[0]

    def predict_dataframe(self, df: pd.DataFrame) -> list:
        """Runs inference on a batch of applicants."""
        # Preprocess features
        X_proc = self.preprocessor.transform(df)

        # Predict probabilities
        probabilities = self.model.predict_proba(X_proc)[:, 1]

        results = []
        for i, prob in enumerate(probabilities):
            prob_float = float(prob)
            band = get_risk_band(prob_float)
            badge = get_risk_badge(band)

            # Credit score proxy: Inverse scaling (1000 - prob * 700) -> 300 to 850 range
            credit_score_proxy = int(np.clip(850 - (prob_float * 550), 300, 850))

            results.append({
                "default_probability": round(prob_float, 4),
                "risk_band": band,
                "risk_badge": badge,
                "credit_score_proxy": credit_score_proxy,
                "processed_features": X_proc.iloc[i].to_dict()
            })

        return results

# Convenience singleton
_predictor = None

def get_risk_prediction(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to get risk prediction for a single applicant."""
    global _predictor
    if _predictor is None:
        _predictor = RiskPredictor()
    return _predictor.predict_single(applicant_data)
