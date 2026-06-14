from unittest.mock import MagicMock, patch

import pytest

from pipeline.transform_silver import transform_bronze_to_silver


@pytest.fixture
def mock_db_conn():
    with patch("pipeline.transform_silver.get_db_connection") as mock_get_conn:
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        yield mock_conn


def test_transform_silver_single_date(mock_db_conn):
    # Setup mock data from Bronze
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchall.return_value = [
        (
            {"date": "2024-01-01", "base": "EUR", "rates": {"USD": 1.1, "GBP": 0.8}},
            "EUR",
        )
    ]

    # Mock execute_values to capture what's being inserted
    with patch("pipeline.transform_silver.execute_values") as mock_exec_values:
        transform_bronze_to_silver()

        # Check if execute_values was called with correct data
        args, _ = mock_exec_values.call_args
        inserted_data = args[2]

        assert len(inserted_data) == 2
        assert ("2024-01-01", "EUR", "USD", 1.1) in inserted_data
        assert ("2024-01-01", "EUR", "GBP", 0.8) in inserted_data


def test_transform_silver_range(mock_db_conn):
    # Setup mock data from Bronze for a range
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchall.return_value = [
        (
            {
                "start_date": "2024-01-01",
                "end_date": "2024-01-02",
                "base": "EUR",
                "rates": {"2024-01-01": {"USD": 1.1}, "2024-01-02": {"USD": 1.2}},
            },
            "EUR",
        )
    ]

    with patch("pipeline.transform_silver.execute_values") as mock_exec_values:
        transform_bronze_to_silver()

        args, _ = mock_exec_values.call_args
        inserted_data = args[2]

        assert len(inserted_data) == 2
        assert ("2024-01-01", "EUR", "USD", 1.1) in inserted_data
        assert ("2024-01-02", "EUR", "USD", 1.2) in inserted_data


def test_transform_silver_invalid_rate(mock_db_conn):
    # Setup mock data with invalid rate
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchall.return_value = [
        ({"date": "2024-01-01", "base": "EUR", "rates": {"USD": -1.0, "GBP": 0}}, "EUR")
    ]

    with patch("pipeline.transform_silver.execute_values") as mock_exec_values:
        transform_bronze_to_silver()

        # Should not have called execute_values because no valid data
        mock_exec_values.assert_not_called()
