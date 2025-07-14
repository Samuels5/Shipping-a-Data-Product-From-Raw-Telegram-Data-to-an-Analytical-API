# Shipping a Data Product: From Raw Telegram Data to an Analytical API

An end-to-end data pipeline for Telegram data, leveraging dbt for transformation, Dagster for orchestration, and YOLOv8 for data enrichment.

## Project Overview

This project builds a robust data platform to generate insights about Ethiopian medical businesses using data scraped from public Telegram channels. The pipeline implements a modern ELT (Extract, Load, Transform) framework with the following components:

- **Data Scraping**: Extract data from Telegram channels using Telethon
- **Data Lake**: Store raw data in organized JSON files
- **Data Warehouse**: PostgreSQL database with star schema design
- **Data Transformation**: Clean and transform data using dbt
- **Data Enrichment**: Object detection on images using YOLOv8
- **Analytical API**: FastAPI endpoints for data analysis
- **Pipeline Orchestration**: Automated workflows using Dagster

## Architecture

```
Telegram Channels → Data Scraper → Data Lake (JSON) → PostgreSQL (Raw) → dbt (Transform) → Data Marts → FastAPI
                                        ↓
                                  YOLO Enrichment
```

## Project Structure

```
├── src/
│   ├── scraping/           # Telegram scraping modules
│   ├── api/               # FastAPI application
│   ├── enrichment/        # YOLO object detection
│   ├── pipeline/          # Dagster pipeline definitions
│   ├── config.py          # Configuration management
│   └── utils.py           # Database utilities
├── dbt_project/           # dbt models and transformations
├── data/                  # Data lake storage
├── sql/                   # Database initialization scripts
├── logs/                  # Application logs
├── docker-compose.yml     # Docker services
├── Dockerfile            # Application container
└── requirements.txt      # Python dependencies
```

## Setup Instructions

### 1. Environment Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd Shipping-a-Data-Product-From-Raw-Telegram-Data-to-an-Analytical-API
```

2. Create and configure the `.env` file:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

3. Required environment variables:

```
POSTGRES_PASSWORD=your_secure_password
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
```

### 2. Docker Setup

1. Start the services:

```bash
docker-compose up -d
```

This will start:

- PostgreSQL database (port 5432)
- Application container (port 8000)
- Dagster UI (port 3000)

### 3. Local Development Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Initialize the database:

```bash
python -c "from src.utils import DatabaseManager; from src.config import Config; db = DatabaseManager(Config()); db.execute_sql_file('sql/init.sql')"
```

## Usage

### Data Scraping

#### Option 1: Use Real Telegram Data

1. Set up Telegram API credentials in `.env`
2. Run the scraper:

```bash
python run_scraper.py --action scrape
```

#### Option 2: Use Sample Data (for testing)

1. Generate sample data:

```bash
python generate_sample_data.py
```

2. Load sample data into database:

```bash
python run_scraper.py --action load
```

### Data Pipeline Status

✅ **Task 0: Project Setup** - Complete

- ✅ Git repository initialized
- ✅ Requirements.txt created
- ✅ Docker configuration ready
- ✅ Environment management set up
- ✅ Secrets management implemented

✅ **Task 1: Data Scraping** - Complete

- ✅ Telegram scraper implemented
- ✅ Data lake structure created
- ✅ Raw data extraction working
- ✅ Database loading functionality
- ✅ Sample data generator for testing

🔄 **Task 2: Data Modeling (dbt)** - In Progress
🔄 **Task 3: Object Detection (YOLO)** - Pending
🔄 **Task 4: Analytical API** - Pending  
🔄 **Task 5: Pipeline Orchestration** - Pending

## Data Sources

The pipeline scrapes data from Ethiopian medical business Telegram channels:

- Chemed Telegram Channel
- https://t.me/lobelia4cosmetics
- https://t.me/tikvahpharma
- Additional channels from https://et.tgstat.com/medicine

## Database Schema

### Raw Layer (`raw` schema)

- `telegram_messages`: Raw message data from Telegram channels

### Staging Layer (`staging` schema) - Coming in Task 2

- `stg_telegram_messages`: Cleaned and standardized messages
- `stg_channels`: Channel information
- `stg_images`: Image metadata

### Data Marts (`marts` schema) - Coming in Task 2

- `dim_channels`: Channel dimension table
- `dim_dates`: Date dimension table
- `fct_messages`: Message fact table
- `fct_image_detections`: Object detection results

## Development Commands

```bash
# Run scraper with different options
python run_scraper.py --action scrape     # Scrape new data
python run_scraper.py --action load       # Load existing data
python run_scraper.py --action both       # Both scrape and load

# Generate sample data for testing
python generate_sample_data.py

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app
docker-compose logs -f postgres

# Stop services
docker-compose down
```

## Next Steps

1. **Task 2**: Implement dbt models for data transformation
2. **Task 3**: Add YOLOv8 object detection for image analysis
3. **Task 4**: Build FastAPI analytical endpoints
4. **Task 5**: Set up Dagster pipeline orchestration

## Contributing

1. Create feature branches for each task
2. Follow the existing code structure
3. Add appropriate logging and error handling
4. Test with sample data before using real Telegram data

## License

This project is for educational purposes as part of the 10 Academy KAIM Week 7 challenge.
