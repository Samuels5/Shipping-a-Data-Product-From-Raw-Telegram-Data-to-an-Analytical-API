"""
Dagster sensors for the Telegram data pipeline.
"""
import os
from dagster import sensor, RunRequest, SkipReason, DefaultSensorStatus
from .constants import RAW_DATA_DIR
from .jobs import full_telegram_pipeline

@sensor(
    job=full_telegram_pipeline,
    minimum_interval_seconds=60,
    default_status=DefaultSensorStatus.RUNNING
)
def telegram_directory_sensor(context):
    """
    A sensor that monitors the `data/raw` directory for new JSON files
    and triggers the full pipeline if new files are found.
    """
    last_mtime = float(context.cursor) if context.cursor else 0
    max_mtime = last_mtime
    
    # Check for new or modified files in the raw data directory
    for filename in os.listdir(RAW_DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(RAW_DATA_DIR, filename)
            if os.path.isfile(filepath):
                mtime = os.path.getmtime(filepath)
                if mtime > last_mtime:
                    max_mtime = max(max_mtime, mtime)

    if max_mtime > last_mtime:
        context.update_cursor(str(max_mtime))
        return RunRequest(
            run_key=f"new_file_{max_mtime}",
            run_config={},
        )
    
    return SkipReason(f"No new files found since last check (cursor: {last_mtime}).")
