"""
Dagster resources for the Telegram data pipeline.
"""
from dagster_dbt import DbtCliResource
from .constants import DBT_PROJECT_DIR, DBT_PROFILES_DIR

# Define the dbt resource
dbt_resource = DbtCliResource(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROFILES_DIR,
    target="production",  # This should match the target in profiles.yml
)
