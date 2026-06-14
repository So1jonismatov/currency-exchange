from psycopg2.extras import execute_values
from utils import get_db_connection, logger

def transform_bronze_to_silver():
    logger.info("Starting Silver transformation...")
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # --- 1. Transform Rates ---
        cur.execute("SELECT raw_json, base_currency FROM bronze.raw_rates")
        rows = cur.fetchall()
        cleaned_rates = []

        for raw_payload, base_curr in rows:
            for item in raw_payload:
                date_str = item.get("date")
                b = item.get("base", base_curr)
                q = item.get("quote")
                r = item.get("rate")

                if r is not None and r > 0:
                    cleaned_rates.append((date_str, b, q, r))

        if cleaned_rates:
            insert_rates_query = """
                INSERT INTO silver.cleaned_rates (date, base_currency, target_currency, exchange_rate)
                VALUES %s
                ON CONFLICT (date, base_currency, target_currency) DO NOTHING;
            """
            execute_values(cur, insert_rates_query, cleaned_rates)
            logger.info(f"Silver Transformation: Processed {len(cleaned_rates)} rate records.")

        # --- 2. Transform Currencies ---
        cur.execute("SELECT raw_json FROM bronze.raw_currencies")
        curr_rows = cur.fetchall()
        cleaned_currencies = {} # Using a dict to deduplicate

        for (raw_payload,) in curr_rows:
            if isinstance(raw_payload, list):
                for item in raw_payload:
                    code = item.get("iso_code")
                    if code:
                        cleaned_currencies[code] = (code, item.get("name", "Unknown"), item.get("symbol"))
            elif isinstance(raw_payload, dict):
                for code, name in raw_payload.items():
                    cleaned_currencies[code] = (code, name, None)

        if cleaned_currencies:
            insert_curr_query = """
                INSERT INTO silver.cleaned_currencies (currency_code, currency_name, symbol)
                VALUES %s
                ON CONFLICT (currency_code) DO UPDATE SET
                    currency_name = EXCLUDED.currency_name,
                    symbol = EXCLUDED.symbol;
            """
            execute_values(cur, insert_curr_query, list(cleaned_currencies.values()))
            logger.info(f"Silver Transformation: Processed {len(cleaned_currencies)} currency records.")

        conn.commit()
    except Exception as e:
        logger.error(f"Silver Transformation Error: {e}")
        conn.rollback()
        raise
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    transform_bronze_to_silver()
