import json

from extract import fetch_rates
from utils import get_config, get_db_connection, logger


def load_to_bronze(base, targets, date, end_date=None):
    """
    Extracts data from API and loads it as-is into the bronze layer.
    """
    logger.info(f"Starting Bronze load for {date} (end_date: {end_date})...")

    try:
        data = fetch_rates(base, targets, date, end_date)

        if not data:
            logger.warning("No data extracted. Skipping load.")
            return

        conn = get_db_connection()
        try:
            cur = conn.cursor()

            query = """
                INSERT INTO bronze.raw_rates (fetch_date, base_currency, raw_json)
                VALUES (%s, %s, %s)
            """

            reference_date = (
                data.get("date", date)
                if date != "latest"
                else data.get("date", "now()")
            )

            cur.execute(query, (reference_date, base, json.dumps(data)))

            conn.commit()
            logger.info(
                f"Successfully loaded records into bronze.raw_rates for {reference_date}"
            )

            cur.close()
        except Exception as e:
            logger.error(f"Database Error during Bronze load: {e}")
            conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    except Exception as e:
        logger.error(f"Failed to complete Bronze load: {e}")
        raise


if __name__ == "__main__":
    config = get_config()
    BASE = config["BASE_CURRENCY"]
    TARGETS = config["TARGET_CURRENCIES"]

    # Test loading a specific date
    load_to_bronze(BASE, TARGETS, "2024-01-15")
