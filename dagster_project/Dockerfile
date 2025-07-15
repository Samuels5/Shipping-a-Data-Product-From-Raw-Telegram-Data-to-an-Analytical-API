# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the project files into the container
COPY . .

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# We copy only the requirements file first to leverage Docker layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install dbt-core and dbt-postgres
RUN pip install dbt-core dbt-postgres

# Copy the entire project
COPY . .

# Set environment variables for Dagster
ENV DAGSTER_HOME=/usr/src/app/dagster_home

# Expose the port the app runs on
EXPOSE 3000

# Command to run the Dagster webserver
CMD ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000", "-w", "dagster_project/workspace.yaml"]
