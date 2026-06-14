import argparse
import sys
import time
from datetime import datetime, timedelta

import schedule
from load_bronze import load_to_bronze
from transform_gold import transform_silver_to_gold
from transform_silver import transform_bronze_to_silver
from utils import get_config, get_latest_date_in_db, logger, run_sql_file


def run_pipeline(start_date=None, end_date=None):
    """
    Orchestrates the full ETL pipeline execution.
    1. Bronze: Extract RAW data from API to DB.
    2. Silver: Transform RAW JSON to structured relational data.
    3. Gold: Populate analytical fact and dimension tables.
    """
    logger.info("--- Starting Pipeline Execution ---")
    config = get_config()

    try:
        run_sql_file("schema.sql")
        if not start_date:
            last_date = get_latest_date_in_db()
            if not last_date:
                last_date = (datetime.now() - timedelta(days=30)).date()
                logger.info(
                    f"No existing data found. Starting from 30 days ago: {last_date}"
                )

            start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        if start_date > end_date:
            logger.info(
                f"Data is already up to date. (Start: {start_date}, End: {end_date})"
            )
            return

        logger.info(f"Syncing range: {start_date} to {end_date}")

        load_to_bronze(
            config["BASE_CURRENCY"], config["TARGET_CURRENCIES"], start_date, end_date
        )
        transform_bronze_to_silver()
        transform_silver_to_gold()

        logger.info("--- Pipeline Completed Successfully ---")

    except Exception as e:
        logger.error(f"Pipeline Execution Failed: {e}")


def start_scheduler():
    """
    Initializes a persistent background loop that runs the pipeline daily.
    """
    config = get_config()
    target_time = config["SCHEDULE_TIME"]

    logger.info(f"Scheduler active. Pipeline will run daily at {target_time}.")

    schedule.every().day.at(target_time).do(run_pipeline)

    run_pipeline()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Currency Exchange Data Pipeline Scheduler"
    )
    parser.add_argument("--backfill", action="store_true", help="Run a manual backfill")
    parser.add_argument(
        "--start-date", type=str, help="Start date for backfill (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date", type=str, help="End date for backfill (YYYY-MM-DD)"
    )

    args = parser.parse_args()

    if args.backfill:
        if not args.start_date:
            print("Error: --start-date is required for backfill.")
            sys.exit(1)
        run_pipeline(args.start_date, args.end_date)
    else:
        start_scheduler()
