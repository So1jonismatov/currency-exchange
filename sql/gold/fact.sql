INSERT INTO gold.fact_aggregated_rates (date, target_currency, exchange_rate, rate_change_pct, seven_day_avg)
WITH base_rates AS (
    SELECT
        date,
        target_currency,
        exchange_rate
    FROM silver.cleaned_rates
),
calculated_metrics AS (
    SELECT
        date,
        target_currency,
        exchange_rate,
        (exchange_rate - LAG(exchange_rate) OVER (PARTITION BY target_currency ORDER BY date))
            / NULLIF(LAG(exchange_rate) OVER (PARTITION BY target_currency ORDER BY date), 0) * 100 as rate_change_pct,
        AVG(exchange_rate) OVER (
            PARTITION BY target_currency
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as seven_day_avg
    FROM base_rates
)
SELECT
    date,
    target_currency,
    exchange_rate,
    rate_change_pct,
    seven_day_avg
FROM calculated_metrics
ON CONFLICT (date, target_currency)
DO UPDATE SET
    exchange_rate = EXCLUDED.exchange_rate,
    rate_change_pct = EXCLUDED.rate_change_pct,
    seven_day_avg = EXCLUDED.seven_day_avg,
    load_timestamp = CURRENT_TIMESTAMP;
