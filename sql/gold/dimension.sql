-- Update dim_dates
insert into gold.dim_dates (date, year, month, day, day_name, is_weekday)
select
    distinct date,
    extract(year from date) as year,
    extract(month from date) as month,
    extract(day from date) as day,
    trim(to_char(date, 'Day')) as day_name,
    case
        when extract(isodow from date) in (6,7) then false
        else true
    end as is_weekday
from silver.cleaned_rates
on conflict (date) do nothing;

-- Update dim_currencies
INSERT INTO gold.dim_currencies (currency_code, currency_name)
VALUES
    ('USD', 'United States Dollar'),
    ('EUR', 'Euro'),
    ('UZS', 'Uzbekistani Som'),
    ('RUB', 'Russian Ruble'),
    ('GBP', 'British Pound Sterling')
ON CONFLICT (currency_code) DO NOTHING;
