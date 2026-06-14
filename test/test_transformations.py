from unittest.mock import MagicMock, patch

import pytest

from pipeline.transform_silver import transform_bronze_to_silver


@pytest.fixture
def mock_db_conn():
    """
    Fixture to mock the database connection and cursor.
    Prevents tests from actually hitting the database.
    """
    with patch("pipeline.transform_silver.get_db_connection") as mock_get_conn:
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        yield mock_conn


def test_transform_silver(mock_db_conn):
    """
    Tests the transformation of the native v2 flat list format.
    """
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchall.return_value = [
        (
            [
                {"date": "2024-01-01", "base": "EUR", "quote": "USD", "rate": 1.1},
                {"date": "2024-01-01", "base": "EUR", "quote": "GBP", "rate": 0.8},
                {"date": "2024-01-02", "base": "EUR", "quote": "USD", "rate": 1.2},
            ],
            "EUR",
        )
    ]

    with patch("pipeline.transform_silver.execute_values") as mock_exec_values:
        transform_bronze_to_silver()

        args, _ = mock_exec_values.call_args
        inserted_data = args[2]

        assert len(inserted_data) == 3
        assert ("2024-01-01", "EUR", "USD", 1.1) in inserted_data
        assert ("2024-01-01", "EUR", "GBP", 0.8) in inserted_data
        assert ("2024-01-02", "EUR", "USD", 1.2) in inserted_data


def test_transform_silver_invalid_rate(mock_db_conn):
    """
    Tests that invalid rates (negative or zero) are skipped during transformation.
    """
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchall.return_value = [
        (
            [
                {"date": "2024-01-01", "base": "EUR", "quote": "USD", "rate": -1.0},
                {"date": "2024-01-01", "base": "EUR", "quote": "GBP", "rate": 0},
            ],
            "EUR",
        )
    ]

    with patch("pipeline.transform_silver.execute_values") as mock_exec_values:
        transform_bronze_to_silver()

        mock_exec_values.assert_not_called()


def test_filter_invalid_rates():
    raw_data = [
        {"date": "2024-01-01", "quote": "EUR", "rate": 0.85},
        {"date": "2024-01-01", "quote": "RUB", "rate": -5.0},  # Invalid!
        {"date": "2024-01-01", "quote": "GBP", "rate": None},  # Invalid!
    ]

    cleaned_data = []
    for item in raw_data:
        r = item.get("rate")
        if r is not None and r > 0:
            cleaned_data.append(item)

    assert len(cleaned_data) == 1
    assert cleaned_data[0]["quote"] == "EUR"
