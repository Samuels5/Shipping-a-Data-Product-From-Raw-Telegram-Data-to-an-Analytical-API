"""Constants for the Dagster project."""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent

# dbt project directory
DBT_PROJECT_DIR = PROJECT_ROOT_DIR / "dbt_project"
DBT_PROFILES_DIR = DBT_PROJECT_DIR / "profiles"

# Data directories
DATA_DIR = PROJECT_ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Other paths
SQL_DIR = PROJECT_ROOT_DIR / "sql"
SRC_DIR = PROJECT_ROOT_DIR / "src"
SCRAPING_DIR = SRC_DIR / "scraping"
ENRICHMENT_DIR = SRC_DIR / "enrichment"
