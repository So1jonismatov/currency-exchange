create schema if not exists bronze;
create schema if not exists silver;
create schema if not exists gold;


-- bronze layer

create table if not exists bronze.raw_rates(
    id Serial primary key,
    fetch_date Date not null,
    base_currency Text not null default 'USD',
    raw_json Jsonb not null,
    inserted_at Timestamp with time zone default CURRENT_TIMESTAMP
);


-- silver layer

create table if not exists silver.cleaned_rates(
    date Date not null,
    base_currency Text not null,
    target_currency Text not null,
    exchange_rate Numeric(18, 6) not null,
    load_timestamp Timestamp with time zone default CURRENT_TIMESTAMP,

    primary key (date, base_currency, target_currency)
);

-- gold layer

create table if not exists gold.dim_currencies (
    currency_code Text primary key,
    currency_name Text,
    symbol Text,
    country Text
);

create table if not exists gold.dim_dates(
    date Date primary key,
    year Int,
    month Int,
    day Int,
    day_name Text,
    is_weekday Boolean
);

create table if not exists gold.fact_aggregated_rates(
    date Date references gold.dim_dates(date),
    target_currency Text references gold.dim_currencies(currency_code),
    exchange_rate Numeric(18,6),
    rate_change_pct Numeric(10,4),
    seven_day_avg Numeric(18,6),
    load_timestamp Timestamp with time zone default CURRENT_TIMESTAMP,

    primary key (date, target_currency)
);
