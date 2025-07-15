"""
Dagster repository for the Telegram data pipeline.
"""
from dagster import repository
from .jobs import full_telegram_pipeline
from .sensors import telegram_directory_sensor

@repository
def telegram_dagster():
    """
    The repository definition for the telegram_dagster project.
    """
    return [full_telegram_pipeline, telegram_directory_sensor]
