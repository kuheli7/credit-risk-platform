"""Data loader module for Home Credit Default Risk tables."""

from typing import Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from src.utils.config import RANDOM_STATE, TEST_SIZE
from src.utils.helpers import resolve_data_file
from src.utils.logger import logger

def aggregate_bureau(nrows: Optional[int] = None) -> pd.DataFrame:
    """Aggregates bureau table features at SK_ID_CURR level."""
    file_path = resolve_data_file("bureau.csv")
    logger.info(f"Loading and aggregating {file_path.name}...")
    
    use_cols = [
        "SK_ID_CURR", "SK_ID_BUREAU", "CREDIT_ACTIVE", 
        "DAYS_CREDIT", "AMT_CREDIT_SUM", "AMT_CREDIT_SUM_DEBT", "AMT_CREDIT_SUM_OVERDUE"
    ]
    df = pd.read_csv(file_path, usecols=use_cols, nrows=nrows)
    
    # Flags & active counts
    df["IS_ACTIVE"] = (df["CREDIT_ACTIVE"] == "Active").astype(int)
    
    agg = df.groupby("SK_ID_CURR").agg(
        BUREAU_LOAN_COUNT=("SK_ID_BUREAU", "count"),
        BUREAU_ACTIVE_LOANS=("IS_ACTIVE", "sum"),
        BUREAU_DAYS_CREDIT_MAX=("DAYS_CREDIT", "max"),
        BUREAU_DAYS_CREDIT_MEAN=("DAYS_CREDIT", "mean"),
        BUREAU_AMT_CREDIT_SUM_MEAN=("AMT_CREDIT_SUM", "mean"),
        BUREAU_AMT_CREDIT_SUM_DEBT_MEAN=("AMT_CREDIT_SUM_DEBT", "mean"),
        BUREAU_AMT_CREDIT_SUM_OVERDUE_MEAN=("AMT_CREDIT_SUM_OVERDUE", "mean"),
    ).reset_index()
    
    logger.info(f"Bureau aggregated for {len(agg):,} unique clients.")
    return agg

def aggregate_previous_applications(nrows: Optional[int] = None) -> pd.DataFrame:
    """Aggregates previous_application table features at SK_ID_CURR level."""
    file_path = resolve_data_file("previous_application.csv")
    logger.info(f"Loading and aggregating {file_path.name}...")
    
    use_cols = [
        "SK_ID_CURR", "SK_ID_PREV", "NAME_CONTRACT_STATUS", 
        "AMT_APPLICATION", "AMT_CREDIT", "DAYS_DECISION"
    ]
    df = pd.read_csv(file_path, usecols=use_cols, nrows=nrows)
    
    df["IS_REFUSED"] = (df["NAME_CONTRACT_STATUS"] == "Refused").astype(int)
    df["IS_APPROVED"] = (df["NAME_CONTRACT_STATUS"] == "Approved").astype(int)
    
    agg = df.groupby("SK_ID_CURR").agg(
        PREV_APP_COUNT=("SK_ID_PREV", "count"),
        PREV_APP_REFUSED_COUNT=("IS_REFUSED", "sum"),
        PREV_APP_APPROVED_COUNT=("IS_APPROVED", "sum"),
        PREV_AMT_APPLICATION_MEAN=("AMT_APPLICATION", "mean"),
        PREV_AMT_CREDIT_MEAN=("AMT_CREDIT", "mean"),
        PREV_DAYS_DECISION_MAX=("DAYS_DECISION", "max"),
    ).reset_index()
    
    agg["PREV_APP_REFUSED_RATE"] = agg["PREV_APP_REFUSED_COUNT"] / np.maximum(agg["PREV_APP_COUNT"], 1)
    
    logger.info(f"Previous applications aggregated for {len(agg):,} unique clients.")
    return agg

def load_merged_dataset(
    app_nrows: Optional[int] = None,
    bureau_nrows: Optional[int] = None,
    prev_nrows: Optional[int] = None,
) -> pd.DataFrame:
    """Loads application_train and left-joins aggregated bureau and previous_applications."""
    app_path = resolve_data_file("application_train.csv")
    logger.info(f"Loading {app_path.name} (limit: {app_nrows})...")
    df_app = pd.read_csv(app_path, nrows=app_nrows)
    logger.info(f"Loaded {len(df_app):,} application records.")

    # Aggregate supplementary tables
    df_bureau = aggregate_bureau(nrows=bureau_nrows)
    df_prev = aggregate_previous_applications(nrows=prev_nrows)

    # Merge
    logger.info("Merging application data with bureau and previous applications...")
    df_merged = df_app.merge(df_bureau, on="SK_ID_CURR", how="left")
    df_merged = df_merged.merge(df_prev, on="SK_ID_CURR", how="left")

    # Fill default aggregates for clients with no bureau / prev records
    df_merged["BUREAU_LOAN_COUNT"] = df_merged["BUREAU_LOAN_COUNT"].fillna(0)
    df_merged["BUREAU_ACTIVE_LOANS"] = df_merged["BUREAU_ACTIVE_LOANS"].fillna(0)
    df_merged["PREV_APP_COUNT"] = df_merged["PREV_APP_COUNT"].fillna(0)
    df_merged["PREV_APP_REFUSED_COUNT"] = df_merged["PREV_APP_REFUSED_COUNT"].fillna(0)
    df_merged["PREV_APP_REFUSED_RATE"] = df_merged["PREV_APP_REFUSED_RATE"].fillna(0)

    logger.info(f"Merged master dataset shape: {df_merged.shape}")
    return df_merged

def get_train_test_data(
    nrows: Optional[int] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Splits merged dataset into stratified train and test sets."""
    df = load_merged_dataset(app_nrows=nrows)
    
    target_col = "TARGET"
    if target_col not in df.columns:
        raise ValueError("TARGET column not found in dataset.")
        
    y = df[target_col]
    X = df.drop(columns=[target_col])
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )
    
    logger.info(
        f"Train split: {X_train.shape[0]:,} samples | "
        f"Test split: {X_test.shape[0]:,} samples | "
        f"Default rate: {y.mean()*100:.2f}%"
    )
    return X_train, X_test, y_train, y_test
