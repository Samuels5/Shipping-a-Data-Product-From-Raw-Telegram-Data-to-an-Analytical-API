"""
Dagster jobs for the Telegram data pipeline.
"""
from dagster import define_asset_job, AssetSelection

# Define a job that materializes all assets
full_telegram_pipeline = define_asset_job(
    name="full_telegram_pipeline",
    selection=AssetSelection.all(),
    description="A job that runs the full Telegram data pipeline: scraping, loading, dbt models, and enrichment.",
)
