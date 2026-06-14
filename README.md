# Currency Exchange Data Pipeline

A robust data pipeline following the Medallion architecture (Bronze, Silver, Gold) to extract currency exchange rates from the Frankfurter API and provide aggregated financial metrics.

## Architecture

1.  **Bronze (Raw)**: Stores raw JSON responses from the Frankfurter API.
2.  **Silver (Cleaned)**: Parsed, validated, and deduplicated records.
3.  **Gold (Aggregated)**: Daily exchange rates with added business metrics:
    - `rate_change_pct`: Percentage change compared to the previous day.
    - `seven_day_avg`: 7-day moving average of the exchange rate.

## Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Docker (optional, for DB)

### Installation
1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd currency-exchange
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Copy `.env.example` to `.env` and fill in your database credentials and pipeline settings.
    ```bash
    cp .env.example .env
    ```

5.  **Initialize Database**:
    Run the SQL schema:
    ```bash
    psql -h localhost -U admin -d currency_exchange -f sql/schema.sql
    ```

## Usage

### Running the Daily Schedule
The scheduler runs the pipeline incrementally every day at the configured `SCHEDULE_TIME`.
```bash
python pipeline/scheduler.py
```

### Running a Historical Backfill
You can manually trigger a backfill for a specific date range:
```bash
python pipeline/scheduler.py --backfill --start-date 2024-01-01 --end-date 2024-01-31
```

### Running Tests
```bash
$env:PYTHONPATH=".;pipeline"
python -m pytest test/
```

## Features
- **Centralized Logging**: Consistent logging across all pipeline steps.
- **Robust Error Handling**: Automatic retries for API extraction using `tenacity`.
- **Incremental Loading**: Only fetches missing data by default.
- **Unit Tested**: Core transformation logic is verified with `pytest`.
