import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from pathlib import Path
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import StratifiedKFold

from src.data.loader import get_train_test_data
from src.data.preprocessor import CreditRiskPreprocessor
from src.utils.config import (
    MODEL_DIR,
    RANDOM_STATE,
    CV_FOLDS,
    SCALE_POS_WEIGHT,
)
from src.utils.logger import logger

def train_credit_risk_model(nrows: int = None) -> Dict[str, Any]:
    """Runs full data loading, preprocessing, 5-fold CV, and saves final model artifact."""
    logger.info("Starting Credit Risk Model Training Pipeline...")
    
    # 1. Load data
    X_train_raw, X_test_raw, y_train, y_test = get_train_test_data(nrows=nrows)

    # 2. Fit and transform preprocessor
    preprocessor = CreditRiskPreprocessor()
    X_train_proc = preprocessor.fit_transform(X_train_raw)
    X_test_proc = preprocessor.transform(X_test_raw)
    
    # Save preprocessor artifact
    preprocessor.save(MODEL_DIR / "preprocessor.pkl")
    
    feature_names = preprocessor.feature_names
    with open(MODEL_DIR / "feature_list.json", "w") as f:
        json.dump(feature_names, f, indent=2)
    logger.info(f"Saved feature list ({len(feature_names)} features) to {MODEL_DIR / 'feature_list.json'}")

    # 3. K-Fold Cross Validation
    logger.info(f"Beginning {CV_FOLDS}-Fold Stratified Cross-Validation...")
    skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    
    fold_roc_aucs: List[float] = []
    fold_pr_aucs: List[float] = []
    
    # Base LightGBM parameters tuned for credit default risk tabular data
    lgb_params = {
        "objective": "binary",
        "boosting_type": "gbdt",
        "n_estimators": 800,
        "learning_rate": 0.05,
        "num_leaves": 45,
        "max_depth": 7,
        "min_child_samples": 50,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "scale_pos_weight": SCALE_POS_WEIGHT,
        "random_state": RANDOM_STATE,
        "n_jobs": -1,
        "verbose": -1
    }

    # Cross-validation loop
    for fold, (train_idx, val_idx) in enumerate(skf.split(X_train_proc, y_train), 1):
        X_tr, y_tr = X_train_proc.iloc[train_idx], y_train.iloc[train_idx]
        X_val, y_val = X_train_proc.iloc[val_idx], y_train.iloc[val_idx]

        clf = LGBMClassifier(**lgb_params)
        clf.fit(
            X_tr, y_tr,
            eval_set=[(X_val, y_val)],
            eval_names=["valid"],
            eval_metric="average_precision",
            callbacks=[]
        )

        val_preds = clf.predict_proba(X_val)[:, 1]
        roc = roc_auc_score(y_val, val_preds)
        pr = average_precision_score(y_val, val_preds)
        
        fold_roc_aucs.append(roc)
        fold_pr_aucs.append(pr)
        logger.info(f"Fold {fold}/{CV_FOLDS} - ROC-AUC: {roc:.4f} | PR-AUC: {pr:.4f}")

    mean_roc_auc = float(np.mean(fold_roc_aucs))
    mean_pr_auc = float(np.mean(fold_pr_aucs))
    logger.info(f"==> Cross-Validation Mean ROC-AUC: {mean_roc_auc:.4f} (+/- {np.std(fold_roc_aucs):.4f})")
    logger.info(f"==> Cross-Validation Mean PR-AUC:  {mean_pr_auc:.4f} (+/- {np.std(fold_pr_aucs):.4f})")

    # 4. Train final champion model on entire training partition
    logger.info("Training final champion model on entire training dataset...")
    final_model = LGBMClassifier(**lgb_params)
    final_model.fit(
        X_train_proc, y_train,
        eval_set=[(X_test_proc, y_test)],
        eval_names=["test_holdout"],
        eval_metric="average_precision",
        callbacks=[]
    )

    # 5. Evaluate on holdout test partition
    test_preds = final_model.predict_proba(X_test_proc)[:, 1]
    test_roc_auc = float(roc_auc_score(y_test, test_preds))
    test_pr_auc = float(average_precision_score(y_test, test_preds))
    logger.info(f"==> Final Holdout Test ROC-AUC: {test_roc_auc:.4f} | PR-AUC: {test_pr_auc:.4f}")

    # 6. Save model artifact and test set for evaluation
    model_path = MODEL_DIR / "lgbm_model.pkl"
    joblib.dump(final_model, model_path)
    logger.info(f"Saved champion model artifact to {model_path}")

    # Cache test holdout for evaluate.py and explainability
    joblib.dump((X_test_proc, y_test, test_preds), MODEL_DIR / "test_holdout.pkl")
    joblib.dump(X_train_proc.sample(min(2000, len(X_train_proc)), random_state=RANDOM_STATE), MODEL_DIR / "background_sample.pkl")

    metrics_summary = {
        "cv_folds": CV_FOLDS,
        "cv_mean_roc_auc": mean_roc_auc,
        "cv_mean_pr_auc": mean_pr_auc,
        "test_roc_auc": test_roc_auc,
        "test_pr_auc": test_pr_auc,
        "n_features": len(feature_names),
        "scale_pos_weight": SCALE_POS_WEIGHT,
    }
    
    with open(MODEL_DIR / "metrics.json", "w") as f:
        json.dump(metrics_summary, f, indent=2)

    logger.info("Training pipeline completed successfully.")
    return metrics_summary

if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 60000
    train_credit_risk_model(nrows=limit)
