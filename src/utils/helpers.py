"""Common helper utilities for risk calculations, formatting, and database setup."""

from typing import Tuple, Dict, Any
from pathlib import Path
from src.utils.config import (
    RISK_THRESHOLD_LOW,
    RISK_THRESHOLD_HIGH,
    DATA_DIR,
    RAW_DATA_DIR,
    DB_PATH
)
from src.utils.logger import logger
import pandas as pd
import sqlite3

def get_risk_band(probability: float) -> str:
    """Classifies default probability into Low, Medium, or High risk bands."""
    if probability < RISK_THRESHOLD_LOW:
        return "Low"
    elif probability <= RISK_THRESHOLD_HIGH:
        return "Medium"
    else:
        return "High"

def get_risk_badge(band: str) -> str:
    """Returns an emoji/color badge for a risk band."""
    badges = {
        "Low": "🟢 Low Risk",
        "Medium": "🟡 Medium Risk",
        "High": "🔴 High Risk"
    }
    return badges.get(band, "⚪ Unknown")

def resolve_data_file(filename: str) -> Path:
    """Finds the dataset file in either project data/ directory or raw dataset folder."""
    local_path = DATA_DIR / filename
    if local_path.exists():
        return local_path
    
    raw_path = RAW_DATA_DIR / filename
    if raw_path.exists():
        return raw_path
        
    raise FileNotFoundError(f"Cannot locate dataset file: {filename} in {DATA_DIR} or {RAW_DATA_DIR}")

def initialize_sqlite_db(max_rows: int = 50000, force_reload: bool = False) -> Path:
    """Initializes SQLite database with application, bureau, and previous_application tables."""
    if DB_PATH.exists() and not force_reload:
        logger.info(f"Database already exists at {DB_PATH}. Skipping initialization.")
        return DB_PATH

    logger.info(f"Initializing SQLite database at {DB_PATH} with sample limit {max_rows}...")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # 1. Load application_train
    app_path = resolve_data_file("application_train.csv")
    logger.info(f"Loading {app_path.name} into applications table...")
    df_app = pd.read_csv(app_path, nrows=max_rows)
    df_app.to_sql("applications", conn, if_exists="replace", index=False)

    # 2. Load bureau
    bureau_path = resolve_data_file("bureau.csv")
    logger.info(f"Loading {bureau_path.name} into bureau table...")
    df_bureau = pd.read_csv(bureau_path, nrows=max_rows)
    df_bureau.to_sql("bureau", conn, if_exists="replace", index=False)

    # 3. Load previous_application
    prev_path = resolve_data_file("previous_application.csv")
    logger.info(f"Loading {prev_path.name} into previous_applications table...")
    df_prev = pd.read_csv(prev_path, nrows=max_rows)
    df_prev.to_sql("previous_applications", conn, if_exists="replace", index=False)

    # Create primary indices for fast querying
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_sk_id ON applications(SK_ID_CURR);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bureau_sk_id ON bureau(SK_ID_CURR);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prev_sk_id ON previous_applications(SK_ID_CURR);")
    conn.commit()
    conn.close()

    logger.info(f"SQLite database successfully populated at {DB_PATH}")
    return DB_PATH
