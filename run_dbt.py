#!/usr/bin/env python3
"""
Script to run dbt transformations.
This script sets up the environment and runs dbt commands.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent))

from src.config import Config
from src.utils import DatabaseManager

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/dbt.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def setup_dbt_environment():
    """Setup dbt environment variables."""
    config = Config()
    
    # Set environment variables for dbt
    os.environ['POSTGRES_HOST'] = config.POSTGRES_HOST
    os.environ['POSTGRES_DB'] = config.POSTGRES_DB
    os.environ['POSTGRES_USER'] = config.POSTGRES_USER
    os.environ['POSTGRES_PASSWORD'] = config.POSTGRES_PASSWORD
    os.environ['POSTGRES_PORT'] = str(config.POSTGRES_PORT)
    
    # Set dbt project directory
    os.environ['DBT_PROFILES_DIR'] = str(Path(__file__).parent / 'dbt_project')
    
    return config

def run_dbt_command(command, project_dir):
    """Run a dbt command and return the result."""
    logger = logging.getLogger(__name__)
    
    full_command = f"dbt {command} --project-dir {project_dir}"
    logger.info(f"Running: {full_command}")
    
    try:
        result = subprocess.run(
            full_command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=project_dir
        )
        
        logger.info(f"Command output: {result.stdout}")
        if result.stderr:
            logger.warning(f"Command stderr: {result.stderr}")
            
        return True, result.stdout
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with return code {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        return False, e.stderr

def main():
    """Main function to run dbt transformations."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting dbt transformation process...")
    
    try:
        # Setup environment
        config = setup_dbt_environment()
        
        # Test database connection
        db_manager = DatabaseManager(config)
        if not db_manager.test_connection():
            logger.error("Database connection failed. Exiting.")
            return False
        
        # Set project directory
        project_dir = Path(__file__).parent / 'dbt_project'
        
        if not project_dir.exists():
            logger.error(f"dbt project directory not found: {project_dir}")
            return False
        
        logger.info(f"Using dbt project directory: {project_dir}")
        
        # Install dbt packages
        logger.info("Installing dbt packages...")
        success, output = run_dbt_command("deps", project_dir)
        if not success:
            logger.error("Failed to install dbt packages")
            return False
        
        # Debug connection
        logger.info("Testing dbt connection...")
        success, output = run_dbt_command("debug", project_dir)
        if not success:
            logger.warning("dbt debug failed, but continuing...")
        
        # Run dbt models
        logger.info("Running dbt models...")
        success, output = run_dbt_command("run", project_dir)
        if not success:
            logger.error("Failed to run dbt models")
            return False
        
        # Run dbt tests
        logger.info("Running dbt tests...")
        success, output = run_dbt_command("test", project_dir)
        if not success:
            logger.warning("Some dbt tests failed, but continuing...")
        
        # Generate documentation
        logger.info("Generating dbt documentation...")
        success, output = run_dbt_command("docs generate", project_dir)
        if not success:
            logger.warning("Failed to generate documentation, but continuing...")
        
        logger.info("dbt transformation process completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"dbt transformation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
