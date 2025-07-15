"""
Software-Defined Assets for the Telegram data pipeline.
"""
import os
import subprocess
import json
from dagster import asset, AssetExecutionContext, MaterializeResult, MetadataValue
from dagster_dbt import DbtCliResource, dbt_assets, DagsterDbtTranslator
from dagster.utils import file_relative_path
from sqlalchemy import create_engine
import pandas as pd

from .constants import DBT_PROJECT_DIR, RAW_DATA_DIR, SCRAPING_DIR, ENRICHMENT_DIR
from src.utils import get_db_connection, bulk_insert_df
from src.config import Config

# Load configuration
config = Config()

@asset(group_name="scraping", compute_kind="python")
def telegram_channel_data(context: AssetExecutionContext) -> MaterializeResult:
    """
    An asset representing the raw JSON data scraped from Telegram channels.
    This asset runs the telegram_scraper.py script.
    """
    context.log.info("Starting Telegram scraping process.")
    
    scraper_script_path = SCRAPING_DIR / "telegram_scraper.py"
    
    # Ensure the script is executable
    if not os.access(scraper_script_path, os.X_OK):
        os.chmod(scraper_script_path, 0o755)

    process = subprocess.Popen(
        ["python", str(scraper_script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=PROJECT_ROOT_DIR,
    )
    
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        context.log.error(f"Telegram scraping script failed:\n{stderr}")
        raise Exception(f"Telegram scraping failed. See logs for details. Stderr: {stderr}")

    context.log.info(f"Telegram scraping script finished successfully.\n{stdout}")

    # Find the output files
    output_files = list(RAW_DATA_DIR.glob("*.json"))
    if not output_files:
        raise Exception("Scraping script ran but produced no output JSON files.")

    return MaterializeResult(
        metadata={
            "num_files": len(output_files),
            "preview": MetadataValue.json(json.loads(output_files[0].read_text(encoding='utf-8'))),
            "output_directory": str(RAW_DATA_DIR)
        }
    )

@asset(group_name="loading", compute_kind="python", deps=[telegram_channel_data])
def raw_telegram_messages(context: AssetExecutionContext) -> None:
    """
    Loads the scraped JSON data from the `data/raw` directory into the
    `raw.telegram_messages` table in PostgreSQL.
    """
    context.log.info("Starting to load raw telegram messages to database.")
    
    loader_script_path = SCRAPING_DIR / "data_loader.py"
    
    # Ensure the script is executable
    if not os.access(loader_script_path, os.X_OK):
        os.chmod(loader_script_path, 0o755)

    process = subprocess.Popen(
        ["python", str(loader_script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=PROJECT_ROOT_DIR,
    )
    
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        context.log.error(f"Data loading script failed:\n{stderr}")
        raise Exception(f"Data loading failed. See logs for details. Stderr: {stderr}")

    context.log.info(f"Data loading script finished successfully.\n{stdout}")

    # Verify data was loaded
    with get_db_connection() as conn:
        count = pd.read_sql("SELECT COUNT(*) FROM raw.telegram_messages", conn).iloc[0,0]
        context.add_output_metadata({"num_rows_inserted": count})


class CustomDagsterDbtTranslator(DagsterDbtTranslator):
    def get_group_name(self, dbt_resource_props):
        return "dbt_models"

@dbt_assets(
    manifest=file_relative_path(__file__, "../dbt_project/target/manifest.json"),
    dagster_dbt_translator=CustomDagsterDbtTranslator(),
)
def dbt_project_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """
    An asset that represents the dbt models.
    """
    yield from dbt.cli(["build"], context=context).stream()


@asset(group_name="enrichment", compute_kind="python", deps=[dbt_project_assets])
def yolo_enrichment(context: AssetExecutionContext) -> None:
    """
    Runs the YOLO enrichment script to detect objects in images and
    populates the `raw.image_detections` and `marts.fct_image_detections` tables.
    """
    context.log.info("Starting YOLO enrichment process.")
    
    enrichment_script_path = ENRICHMENT_DIR / "yolo_enrichment.py"
    
    # Ensure the script is executable
    if not os.access(enrichment_script_path, os.X_OK):
        os.chmod(enrichment_script_path, 0o755)

    process = subprocess.Popen(
        ["python", str(enrichment_script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=PROJECT_ROOT_DIR,
    )
    
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        context.log.error(f"YOLO enrichment script failed:\n{stderr}")
        raise Exception(f"YOLO enrichment failed. See logs for details. Stderr: {stderr}")

    context.log.info(f"YOLO enrichment script finished successfully.\n{stdout}")

    # Verify data was loaded
    with get_db_connection() as conn:
        count = pd.read_sql("SELECT COUNT(*) FROM raw.image_detections", conn).iloc[0,0]
        context.add_output_metadata({"num_detections": count})
