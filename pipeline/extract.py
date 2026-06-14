import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from utils import logger


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True,
)
def fetch_rates(base_currency, target_currencies, start_date, end_date=None):
    url = "https://api.frankfurter.dev/v2/rates"
    quotes_str = ",".join(target_currencies)
    params = {"base": base_currency, "quotes": quotes_str}
    if end_date:
        params["from"] = start_date
        params["to"] = end_date
    else:
        if start_date != "latest":
            params["date"] = start_date
    try:
        logger.info(
            f"Fetching rates: {base_currency} -> {quotes_str} for {start_date} to {end_date or start_date}"
        )
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json() or None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"Rates not found for the requested date(s): {e}")
            return None
        raise
    except Exception as e:
        logger.error(f"API Extraction Error: {e}")
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True,
)
def fetch_currencies():
    """Extracts the currency metadata from the API."""
    url = "https://api.frankfurter.dev/v2/currencies"
    try:
        logger.info("Fetching currency metadata from API...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"Currencies not found: {e}")
            return None
        raise
    except Exception as e:
        logger.error(f"API Extraction Error (Currencies): {e}")
        raise
