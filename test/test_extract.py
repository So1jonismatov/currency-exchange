from unittest.mock import MagicMock, patch

import requests

from pipeline.extract import fetch_rates


@patch("pipeline.extract.requests.get")
def test_fetch_rates_success(mock_get):
    """Test successful API fetch (v2 format)."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"date": "2024-01-01", "base": "EUR", "quote": "USD", "rate": 1.1}
    ]
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = fetch_rates("EUR", ["USD"], "2024-01-01")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["rate"] == 1.1
    mock_get.assert_called_once()


@patch("pipeline.extract.requests.get")
def test_fetch_rates_404(mock_get):
    """Test handling of 404 (Not Found) from API."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response
    )
    mock_get.return_value = mock_response

    result = fetch_rates("EUR", ["USD"], "2024-01-01")

    assert result is None


@patch("pipeline.extract.requests.get")
def test_fetch_rates_retry_on_error(mock_get):
    """Test that it retries on connection error."""
    mock_get.side_effect = [
        requests.exceptions.ConnectionError(),
        MagicMock(status_code=200, json=lambda: [{"date": "2024-01-01", "rate": 1.1}]),
    ]

    result = fetch_rates("EUR", ["USD"], "2024-01-01")
    assert result[0]["rate"] == 1.1
    assert mock_get.call_count == 2
