import json
from unittest.mock import MagicMock, patch

from pipeline.load_bronze import load_to_bronze


@patch("pipeline.load_bronze.fetch_rates")
@patch("pipeline.load_bronze.get_db_connection")
def test_load_to_bronze_success(mock_get_conn, mock_fetch):
    """Test successful load to bronze layer."""
    mock_fetch.return_value = [
        {"date": "2024-01-01", "base": "EUR", "quote": "USD", "rate": 1.1}
    ]

    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_get_conn.return_value = mock_conn

    load_to_bronze("EUR", ["USD"], "2024-01-01")

    mock_fetch.assert_called_once_with("EUR", ["USD"], "2024-01-01", None)

    mock_cursor.execute.assert_called_once()
    args, _ = mock_cursor.execute.call_args
    query, params = args

    assert "INSERT INTO bronze.raw_rates" in query
    assert params[0] == "2024-01-01"
    assert params[1] == "EUR"
    assert json.loads(params[2]) == mock_fetch.return_value

    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("pipeline.load_bronze.fetch_rates")
@patch("pipeline.load_bronze.get_db_connection")
def test_load_to_bronze_no_data(mock_get_conn, mock_fetch):
    """Test that it skips loading when fetch returns None."""
    mock_fetch.return_value = None

    load_to_bronze("EUR", ["USD"], "2024-01-01")

    mock_get_conn.assert_not_called()
