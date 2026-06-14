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
            database=os.getenv("DB_NAME", "currency_exchange"),
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
        "BASE_CURRENCY": os.getenv("BASE_CURRENCY", "EUR"),
        "TARGET_CURRENCIES": os.getenv("TARGET_CURRENCIES", "USD,UZS,RUB,GBP").split(
            ","
        ),
        "SCHEDULE_TIME": os.getenv("SCHEDULE_TIME", "09:00"),
    }
