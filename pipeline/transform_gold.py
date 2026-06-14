from utils import logger, run_sql_file


def transform_silver_to_gold():
    """
    Refreshes the Gold Layer by executing SQL that purely maps from the Silver Layer.
    """
    logger.info("Starting Gold Layer Transformation...")

    run_sql_file("gold.dimension.sql")
    run_sql_file("gold.fact.sql")

    logger.info("Gold Layer Refresh Complete.")


if __name__ == "__main__":
    transform_silver_to_gold()
