"""
Application configuration and path settings.
"""

import os
from pydantic import BaseModel

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ML_DIR = os.path.join(BASE_DIR, "ml")
ARTIFACTS_DIR = os.path.join(ML_DIR, "artifacts")
REPORTS_DIR = os.path.join(ML_DIR, "reports")
DB_PATH = os.path.join(BACKEND_DIR, "app", "database", "cyberbullying.db")


class Settings(BaseModel):
    app_title: str = "Cyberbullying Detection & Severity Analysis API"
    app_version: str = "1.0.0"
    db_path: str = DB_PATH
    artifacts_dir: str = ARTIFACTS_DIR
    reports_dir: str = REPORTS_DIR
    cors_origins: list = ["*"]
    max_batch_size: int = 1000
    retention_days: int = 30


settings = Settings()
