"""
Definitions for the Dagster project.
"""
from dagster import Definitions
from .assets import telegram_channel_data, raw_telegram_messages, dbt_project_assets, yolo_enrichment
from .jobs import full_telegram_pipeline
from .sensors import telegram_directory_sensor
from .resources import dbt_resource

all_assets = [telegram_channel_data, raw_telegram_messages, dbt_project_assets, yolo_enrichment]
all_jobs = [full_telegram_pipeline]
all_sensors = [telegram_directory_sensor]
all_resources = {"dbt": dbt_resource}

defs = Definitions(
    assets=all_assets,
    jobs=all_jobs,
    sensors=all_sensors,
    resources=all_resources,
)
