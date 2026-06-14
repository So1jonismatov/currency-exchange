import json
from datetime import datetime
from extract import fetch_rates, fetch_currencies
from utils import get_config, get_db_connection, logger

def load_to_bronze(base, targets, date, end_date=None):
    logger.info(f"Starting Bronze load for {date} (end_date: {end_date})...")

    rates_data = fetch_rates(base, targets, date, end_date)
    currencies_data = fetch_currencies()

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # 1. Load Rates JSON
        if rates_data:
            query_rates = """
                INSERT INTO bronze.raw_rates (fetch_date, base_currency, raw_json)
                VALUES (%s, %s, %s)
            """
            ref_date = rates_data[0].get("date", date) if isinstance(rates_data, list) else date
            if ref_date == "latest":
                ref_date = datetime.now().strftime("%Y-%m-%d")

            cur.execute(query_rates, (ref_date, base, json.dumps(rates_data)))
            logger.info(f"Successfully loaded records into bronze.raw_rates for {ref_date}")

        # 2. Load Currencies JSON
        if currencies_data:
            query_curr = """
                INSERT INTO bronze.raw_currencies (fetch_date, raw_json)
                VALUES (%s, %s)
            """
            cur.execute(query_curr, (datetime.now().strftime("%Y-%m-%d"), json.dumps(currencies_data)))
            logger.info("Successfully loaded records into bronze.raw_currencies")

        conn.commit()
    except Exception as e:
        logger.error(f"Database Error during Bronze load: {e}")
        conn.rollback()
        raise
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    config = get_config()
    load_to_bronze(config["BASE_CURRENCY"], config["TARGET_CURRENCIES"], "2024-01-15")
