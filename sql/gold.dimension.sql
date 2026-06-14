-- Populate dim_currencies from the Silver layer
INSERT INTO gold.dim_currencies (currency_code, currency_name, symbol, country)
SELECT
    currency_code,
    currency_name,
    symbol,
    NULL AS country -- API doesn't provide this
FROM silver.cleaned_currencies
ON CONFLICT (currency_code) DO UPDATE SET
    currency_name = EXCLUDED.currency_name,
    symbol = EXCLUDED.symbol,
    country = EXCLUDED.country;

-- Populate dim_dates automatically using date extraction from Silver rates
INSERT INTO gold.dim_dates (date, year, month, day, day_name, is_weekday)
SELECT DISTINCT
    date,
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    EXTRACT(DAY FROM date) AS day,
    TRIM(TO_CHAR(date, 'Day')) AS day_name,
    EXTRACT(ISODOW FROM date) < 6 AS is_weekday  -- ISODOW 1-5 is Monday-Friday
FROM silver.cleaned_rates
ON CONFLICT (date) DO NOTHING;
