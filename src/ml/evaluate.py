import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, Any
import json
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    roc_curve,
    precision_recall_curve,
    confusion_matrix,
    classification_report,
    f1_score
)

from src.utils.config import MODEL_DIR
from src.utils.logger import logger

def evaluate_model() -> Dict[str, Any]:
    """Generates comprehensive evaluation metrics and saves diagnostic plots."""
    logger.info("Running model evaluation pipeline...")
    
    holdout_path = MODEL_DIR / "test_holdout.pkl"
    if not holdout_path.exists():
        raise FileNotFoundError(f"Holdout data not found at {holdout_path}. Please train the model first.")

    X_test_proc, y_test, test_preds = joblib.load(holdout_path)
    eval_plots_dir = MODEL_DIR / "eval_plots"
    eval_plots_dir.mkdir(parents=True, exist_ok=True)

    # 1. Compute core metrics
    roc_auc = float(roc_auc_score(y_test, test_preds))
    pr_auc = float(average_precision_score(y_test, test_preds))

    # Precision-Recall trade-off & optimal F1 threshold
    precisions, recalls, thresholds = precision_recall_curve(y_test, test_preds)
    f1_scores = 2 * (precisions * recalls) / np.maximum(precisions + recalls, 1e-8)
    best_idx = np.argmax(f1_scores)
    optimal_threshold = float(thresholds[min(best_idx, len(thresholds) - 1)])
    best_f1 = float(f1_scores[best_idx])

    # Confusion matrix at optimal threshold
    binary_preds_opt = (test_preds >= optimal_threshold).astype(int)
    cm_opt = confusion_matrix(y_test, binary_preds_opt)

    # Confusion matrix at standard 0.5 threshold
    binary_preds_std = (test_preds >= 0.5).astype(int)
    cm_std = confusion_matrix(y_test, binary_preds_std)

    logger.info(f"Evaluation Metrics on Test Holdout:")
    logger.info(f" - ROC-AUC:           {roc_auc:.4f}")
    logger.info(f" - PR-AUC:            {pr_auc:.4f}")
    logger.info(f" - Optimal Threshold: {optimal_threshold:.4f} (Max F1: {best_f1:.4f})")

    # 2. Save ROC Curve Plot
    fpr, tpr, _ = roc_curve(y_test, test_preds)
    plt.figure(figsize=(7, 6))
    plt.plot(fpr, tpr, color="#2563EB", lw=2.5, label=f"LightGBM (ROC-AUC = {roc_auc:.4f})")
    plt.plot([0, 1], [0, 1], color="gray", lw=1.5, linestyle="--", label="Random Classifier (0.50)")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate", fontsize=11)
    plt.ylabel("True Positive Rate", fontsize=11)
    plt.title("Receiver Operating Characteristic (ROC) Curve", fontsize=13, fontweight="bold")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(eval_plots_dir / "roc_curve.png", dpi=200)
    plt.close()

    # 3. Save Precision-Recall Curve Plot
    plt.figure(figsize=(7, 6))
    plt.plot(recalls, precisions, color="#10B981", lw=2.5, label=f"PR Curve (PR-AUC = {pr_auc:.4f})")
    baseline_rate = float(np.mean(y_test))
    plt.axhline(baseline_rate, color="crimson", linestyle="--", lw=1.5, label=f"No-skill Baseline ({baseline_rate*100:.1f}%)")
    plt.scatter([recalls[best_idx]], [precisions[best_idx]], color="red", zorder=5, s=60, label=f"Optimal F1 ({best_f1:.3f})")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Recall", fontsize=11)
    plt.ylabel("Precision", fontsize=11)
    plt.title("Precision-Recall Curve (Severe Imbalance Handling)", fontsize=13, fontweight="bold")
    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(eval_plots_dir / "pr_curve.png", dpi=200)
    plt.close()

    # 4. Save Confusion Matrix Heatmap
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_opt, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Predicted Non-Default", "Predicted Default"],
                yticklabels=["Actual Non-Default", "Actual Default"])
    plt.title(f"Confusion Matrix (Optimal Threshold = {optimal_threshold:.2f})", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(eval_plots_dir / "confusion_matrix.png", dpi=200)
    plt.close()

    metrics = {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "optimal_threshold": optimal_threshold,
        "best_f1": best_f1,
        "confusion_matrix_optimal": cm_opt.tolist(),
        "confusion_matrix_standard": cm_std.tolist(),
        "test_sample_count": len(y_test),
        "test_default_count": int(np.sum(y_test))
    }

    with open(MODEL_DIR / "evaluation_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info("Evaluation plots and metrics saved successfully.")
    return metrics

if __name__ == "__main__":
    evaluate_model()
