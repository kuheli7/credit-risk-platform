"""Preprocessor for cleaning, feature engineering, encoding, and imputation."""

from typing import List, Dict, Any, Optional
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from src.utils.logger import logger
from src.utils.config import MODEL_DIR

class CreditRiskPreprocessor(BaseEstimator, TransformerMixin):
    """Robust preprocessor for Home Credit Default Risk pipeline."""

    def __init__(self):
        self.numeric_imputations: Dict[str, float] = {}
        self.categorical_imputations: Dict[str, str] = {}
        self.categorical_encodings: Dict[str, Dict[str, int]] = {}
        self.feature_names: List[str] = []
        self.numeric_cols: List[str] = []
        self.categorical_cols: List[str] = []

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Derives domain-specific credit risk ratios and interaction features."""
        df = df.copy()

        # Handle anomalous 365243 values in DAYS_EMPLOYED
        if "DAYS_EMPLOYED" in df.columns:
            df["DAYS_EMPLOYED_ANOM"] = (df["DAYS_EMPLOYED"] == 365243).astype(int)
            df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace({365243: np.nan})

        # Credit & Income ratios
        if "AMT_CREDIT" in df.columns and "AMT_INCOME_TOTAL" in df.columns:
            df["CREDIT_INCOME_RATIO"] = df["AMT_CREDIT"] / np.maximum(df["AMT_INCOME_TOTAL"], 1.0)
            
        if "AMT_ANNUITY" in df.columns and "AMT_INCOME_TOTAL" in df.columns:
            df["ANNUITY_INCOME_RATIO"] = df["AMT_ANNUITY"] / np.maximum(df["AMT_INCOME_TOTAL"], 1.0)

        if "AMT_ANNUITY" in df.columns and "AMT_CREDIT" in df.columns:
            df["PAYMENT_RATE"] = df["AMT_ANNUITY"] / np.maximum(df["AMT_CREDIT"], 1.0)

        if "AMT_GOODS_PRICE" in df.columns and "AMT_CREDIT" in df.columns:
            df["GOODS_PRICE_CREDIT_RATIO"] = df["AMT_GOODS_PRICE"] / np.maximum(df["AMT_CREDIT"], 1.0)

        # Age and Employment ratios (DAYS_BIRTH and DAYS_EMPLOYED are negative in raw data)
        if "DAYS_EMPLOYED" in df.columns and "DAYS_BIRTH" in df.columns:
            df["EMPLOYED_TO_AGE_RATIO"] = df["DAYS_EMPLOYED"] / np.minimum(df["DAYS_BIRTH"], -1.0)

        # External sources composite indicators
        ext_cols = [col for col in ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"] if col in df.columns]
        if ext_cols:
            df["EXT_SOURCES_MEAN"] = df[ext_cols].mean(axis=1)
            df["EXT_SOURCES_STD"] = df[ext_cols].std(axis=1).fillna(0)
            df["EXT_SOURCES_MIN"] = df[ext_cols].min(axis=1)
            df["EXT_SOURCES_MAX"] = df[ext_cols].max(axis=1)

        # Ensure default bureau/prev aggregates exist if missing
        if "BUREAU_ACTIVE_LOANS" not in df.columns:
            df["BUREAU_ACTIVE_LOANS"] = 0.0
        if "PREV_APP_REFUSED_RATE" not in df.columns:
            df["PREV_APP_REFUSED_RATE"] = 0.0

        return df

    def fit(self, X: pd.DataFrame, y=None):
        """Fits imputation statistics and label mappings on training data."""
        logger.info("Fitting CreditRiskPreprocessor on training data...")
        X_eng = self._engineer_features(X)

        # Drop identifier if present
        cols_to_drop = [c for c in ["SK_ID_CURR", "SK_ID_BUREAU", "SK_ID_PREV", "TARGET"] if c in X_eng.columns]
        X_eng = X_eng.drop(columns=cols_to_drop)

        # Identify numeric vs categorical
        self.numeric_cols = X_eng.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = X_eng.select_dtypes(include=["object", "category"]).columns.tolist()

        # Fit numeric medians
        for col in self.numeric_cols:
            median_val = X_eng[col].median()
            self.numeric_imputations[col] = float(0.0 if np.isnan(median_val) else median_val)

        # Fit categorical modes and integer mappings
        for col in self.categorical_cols:
            mode_series = X_eng[col].mode()
            mode_val = str(mode_series.iloc[0]) if not mode_series.empty else "Missing"
            self.categorical_imputations[col] = mode_val

            # Build label mapping (0 = Unknown/Missing, 1..N = classes)
            unique_vals = X_eng[col].dropna().unique().tolist()
            mapping = {str(val): i + 1 for i, val in enumerate(unique_vals)}
            mapping["Missing"] = 0
            mapping["Unknown"] = 0
            self.categorical_encodings[col] = mapping

        # Final ordered feature list
        self.feature_names = self.numeric_cols + self.categorical_cols
        logger.info(
            f"Preprocessor fit complete. Features: {len(self.feature_names)} "
            f"({len(self.numeric_cols)} numeric, {len(self.categorical_cols)} categorical)"
        )
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Applies feature engineering, imputation, and encoding."""
        X_eng = self._engineer_features(X)

        # Drop identifiers
        cols_to_drop = [c for c in ["SK_ID_CURR", "SK_ID_BUREAU", "SK_ID_PREV", "TARGET"] if c in X_eng.columns]
        X_eng = X_eng.drop(columns=cols_to_drop, errors="ignore")

        data_dict = {}

        # Numeric transform
        for col in self.numeric_cols:
            if col in X_eng.columns:
                val = pd.to_numeric(X_eng[col], errors="coerce")
                data_dict[col] = val.fillna(self.numeric_imputations[col]).values
            else:
                data_dict[col] = np.full(len(X_eng), self.numeric_imputations[col])

        # Categorical transform
        for col in self.categorical_cols:
            mapping = self.categorical_encodings.get(col, {})
            impute_val = self.categorical_imputations.get(col, "Missing")
            if col in X_eng.columns:
                series = X_eng[col].fillna(impute_val).astype(str)
                data_dict[col] = series.map(mapping).fillna(0).astype(int).values
            else:
                data_dict[col] = np.zeros(len(X_eng), dtype=int)

        out_df = pd.DataFrame(data_dict, index=X_eng.index)
        return out_df[self.feature_names]

    def save(self, path: Optional[Path] = None) -> Path:
        """Serializes fitted preprocessor to disk."""
        save_path = path or (MODEL_DIR / "preprocessor.pkl")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, save_path)
        logger.info(f"Saved preprocessor artifact to {save_path}")
        return save_path

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "CreditRiskPreprocessor":
        """Loads fitted preprocessor from disk."""
        load_path = path or (MODEL_DIR / "preprocessor.pkl")
        if not load_path.exists():
            raise FileNotFoundError(f"Preprocessor artifact not found at {load_path}")
        obj = joblib.load(load_path)
        logger.info(f"Loaded preprocessor artifact from {load_path}")
        return obj
