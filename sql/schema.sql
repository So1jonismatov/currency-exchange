CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- BRONZE LAYER
CREATE TABLE IF NOT EXISTS bronze.raw_rates (
    id SERIAL PRIMARY KEY,
    fetch_date DATE NOT NULL,
    base_currency TEXT NOT NULL DEFAULT 'USD',
    raw_json JSONB NOT NULL,
    inserted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bronze.raw_currencies (
    id SERIAL PRIMARY KEY,
    fetch_date DATE NOT NULL,
    raw_json JSONB NOT NULL,
    inserted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- SILVER LAYER
CREATE TABLE IF NOT EXISTS silver.cleaned_rates (
    date DATE NOT NULL,
    base_currency TEXT NOT NULL,
    target_currency TEXT NOT NULL,
    exchange_rate NUMERIC(18, 6) NOT NULL,
    load_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (date, base_currency, target_currency)
);

CREATE TABLE IF NOT EXISTS silver.cleaned_currencies (
    currency_code TEXT PRIMARY KEY,
    currency_name TEXT,
    symbol TEXT,
    load_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- GOLD LAYER
CREATE TABLE IF NOT EXISTS gold.dim_currencies (
    currency_code CHAR(3) PRIMARY KEY,
    currency_name VARCHAR(100),
    symbol VARCHAR(10),
    country VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS gold.dim_dates (
    date DATE PRIMARY KEY,
    year INT,
    month INT,
    day INT,
    day_name VARCHAR(20),
    is_weekday BOOLEAN
);

CREATE TABLE IF NOT EXISTS gold.aggregated_rates (
    date DATE REFERENCES gold.dim_dates(date),
    target_currency CHAR(3) REFERENCES gold.dim_currencies(currency_code),
    exchange_rate NUMERIC(18, 6),
    rate_change_pct NUMERIC(10, 4),
    seven_day_avg NUMERIC(18, 6),
    load_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (date, target_currency)
);
