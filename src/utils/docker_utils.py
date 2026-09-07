"""Docker and environment utility helpers."""

import os
from pathlib import Path

def is_running_in_docker() -> bool:
    """Detects whether the code is currently running inside a Docker container."""
    return Path("/.dockerenv").exists() or os.getenv("IS_DOCKER", "false").lower() == "true"

def get_base_data_path() -> Path:
    """Returns the effective data directory based on execution environment."""
    if is_running_in_docker():
        return Path("/app/data")
    return Path(__file__).resolve().parent.parent.parent / "data"
