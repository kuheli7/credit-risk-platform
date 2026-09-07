"""Configuration settings and environment variable management."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load .env file from project root or current working dir
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# API Keys
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# Directory configurations
DATA_DIR: Path = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data")).resolve()
MODEL_DIR: Path = Path(os.getenv("MODEL_DIR", PROJECT_ROOT / "models")).resolve()
DB_PATH: Path = Path(os.getenv("DB_PATH", DATA_DIR / "credit_risk.db")).resolve()

# Fallback dataset directory (raw Kaggle directory)
RAW_DATA_DIR: Path = (PROJECT_ROOT.parent / "home-credit-default-risk").resolve()

# Model parameters
RANDOM_STATE: int = 42
TEST_SIZE: float = 0.20
CV_FOLDS: int = 5
SCALE_POS_WEIGHT: float = 11.5  # ~92% class 0 / ~8% class 1

# Risk thresholds
RISK_THRESHOLD_LOW: float = 0.20
RISK_THRESHOLD_HIGH: float = 0.50

# Ensure essential directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
(MODEL_DIR / "eval_plots").mkdir(parents=True, exist_ok=True)
(PROJECT_ROOT / "documents").mkdir(parents=True, exist_ok=True)
(PROJECT_ROOT / "notebooks").mkdir(parents=True, exist_ok=True)
