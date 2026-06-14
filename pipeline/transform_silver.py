from psycopg2.extras import execute_values
from utils import get_db_connection, logger


def transform_bronze_to_silver():
    """
    Transforms raw JSON data from the Bronze layer into structured records in the Silver layer.
    Correctly handles Frankfurter API's single-date and date-range response formats.
    """
    logger.info("Starting Silver transformation...")
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT raw_json, base_currency FROM bronze.raw_rates")
        rows = cur.fetchall()

        cleaned_data = []

        for raw_payload, base_curr in rows:
            rates = raw_payload.get("rates", {})

            if "start_date" in raw_payload:
                for date_str, quotes in rates.items():
                    for target_curr, rate in quotes.items():
                        if rate is not None and rate > 0:
                            cleaned_data.append(
                                (date_str, base_curr, target_curr, rate)
                            )

            elif "date" in raw_payload:
                date_str = raw_payload.get("date")
                for target_curr, rate in rates.items():
                    if rate is not None and rate > 0:
                        cleaned_data.append((date_str, base_curr, target_curr, rate))

            else:
                logger.warning(
                    f"Unexpected JSON structure in Bronze record. Base: {base_curr}"
                )

        upsert_query = """
            INSERT INTO silver.cleaned_rates (date, base_currency, target_currency, exchange_rate)
            VALUES %s
            ON CONFLICT (date, base_currency, target_currency)
            DO NOTHING;
        """

        if cleaned_data:
            execute_values(cur, upsert_query, cleaned_data)
            conn.commit()
            logger.info(
                f"Silver Transformation Complete: Processed {len(cleaned_data)} records."
            )
        else:
            logger.info("No valid data found to transform to Silver.")

    except Exception as e:
        logger.error(f"Silver Transformation Error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            cur.close()
            conn.close()


if __name__ == "__main__":
    transform_bronze_to_silver()
