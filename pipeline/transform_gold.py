import os

from utils import get_db_connection, logger


def run_sql_script(filename, conn):
    """
    Reads a SQL file from the sql/gold/ directory and executes it.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(base_dir, "..", "sql", "gold", filename)

    try:
        with open(sql_path, "r") as f:
            sql_command = f.read()

        cur = conn.cursor()
        cur.execute(sql_command)
        conn.commit()
        cur.close()
        logger.info(f"Successfully executed: {filename}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error executing {filename}: {e}")
        raise


def transform_silver_to_gold():
    """Orchestrates the Gold layer update process."""
    logger.info("Starting Gold Layer Transformation...")
    conn = None
    try:
        conn = get_db_connection()

        run_sql_script("dimension.sql", conn)

        run_sql_script("fact.sql", conn)

        logger.info("Gold Layer Refresh Complete.")

    except Exception as e:
        logger.error(f"Critical Gold Transformation Failure: {e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    transform_silver_to_gold()
