INSERT INTO gold.aggregated_rates (date, target_currency, exchange_rate, rate_change_pct, seven_day_avg)
WITH metrics AS (
    SELECT
        date,
        target_currency,
        exchange_rate,
        ((exchange_rate - LAG(exchange_rate) OVER (PARTITION BY target_currency ORDER BY date)) /
         NULLIF(LAG(exchange_rate) OVER (PARTITION BY target_currency ORDER BY date), 0)) * 100 AS rate_change_pct,
        AVG(exchange_rate) OVER (PARTITION BY target_currency ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS seven_day_avg
    FROM silver.cleaned_rates
)

SELECT date, target_currency, exchange_rate, rate_change_pct, seven_day_avg
FROM metrics
ON CONFLICT (date, target_currency)
DO UPDATE SET
    exchange_rate = EXCLUDED.exchange_rate,
    rate_change_pct = EXCLUDED.rate_change_pct,
    seven_day_avg = EXCLUDED.seven_day_avg,
    load_timestamp = CURRENT_TIMESTAMP;
