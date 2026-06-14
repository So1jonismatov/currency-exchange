import logging
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("CurrencyExchangePipeline")


logger = setup_logging()


def get_db_connection():
    """Returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "db"),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "secret123"),
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        raise


def get_config():
    """Returns configuration from environment variables."""
    return {
        "BASE_CURRENCY": os.getenv("BASE_CURRENCY", "USD"),
        "TARGET_CURRENCIES": os.getenv("TARGET_CURRENCIES", "UZS,RUB,EUR,GBP").split(
            ","
        ),
        "SCHEDULE_TIME": os.getenv(
            "SCHEDULE_TIME", "03:00"
        ),  # 03:00 UTC = 08:00 AM Tashkent
    }


def get_latest_date_in_db():
    """
    Fetches the most recent date processed in the Silver layer.
    Used for incremental loading (starting from where we left off).
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT MAX(date) FROM silver.cleaned_rates")
        row = cur.fetchone()

        result = row[0] if row else None

        cur.close()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error fetching latest date from DB: {e}")
        return None


def run_sql_file(filename):
    """
    Reads a SQL file and executes its content against the database.
    """
    file_path = os.path.join(os.path.dirname(__file__), "..", "sql", filename)

    with open(file_path, "r") as f:
        sql = f.read()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        logger.info(f"Successfully executed: {filename}")
    except Exception as e:
        logger.error(f"Error executing {filename}: {e}")
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
