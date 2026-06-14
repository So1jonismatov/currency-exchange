from unittest.mock import MagicMock, mock_open, patch

from pipeline.transform_gold import run_sql_file, transform_silver_to_gold


@patch("pipeline.transform_gold.get_db_connection")
@patch("builtins.open", new_callable=mock_open, read_data="SELECT 1;")
def test_run_sql_file(mock_file, mock_get_conn):
    """Test executing a SQL file."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_get_conn.return_value = mock_conn

    run_sql_file("test.sql")

    mock_file.assert_called_once()
    mock_cursor.execute.assert_called_with("SELECT 1;")
    mock_conn.commit.assert_called_once()


@patch("pipeline.transform_gold.run_sql_file")
def test_transform_silver_to_gold(mock_run_sql):
    """Test that all gold layer transformations are triggered."""
    transform_silver_to_gold()

    assert mock_run_sql.call_count == 2
    mock_run_sql.assert_any_call("dimension.sql")
    mock_run_sql.assert_any_call("fact.sql")
