--first it is necessary to identify wich are the values previous of the current
WITH price_drops AS (
    SELECT 
        coin,
        date,
        price,
        json,
        LAG(price, 1) OVER (PARTITION BY coin ORDER BY date) as previous_price
    FROM 
        coin_data
), consecutive_days AS ( 
    -- In this part, it is determined whether the price of a specific day is 
    -- lower than that of the previous day. This is done using a CASE statement 
    -- that returns 1 if there is a price drop (that is, if the price is less than
    -- the previous price) and 0 otherwise.
    SELECT 
        coin,
        date,
        price,
        json,
        previous_price,
        CASE 
            WHEN price < previous_price THEN 1
            ELSE 0
        END as is_drop
    FROM 
        price_drops
), the_groups AS (
    -- Here, consecutive days of price declines are grouped together. SUM is used 
    -- with the OVER window function to accumulate the number of consecutive drops.
    SELECT 
        coin,
        date,
        price,
        json,
        SUM(is_drop) OVER (PARTITION BY coin ORDER BY date) as drop_group
    FROM 
        consecutive_days
) -- In the final query, the average price increase after periods of decline is calculated. 
  -- The the_groups table is JOIN'd with itself to match each drop group with its respective 
  -- next day, and then the average gain (AVG(a.price - b.price)) is calculated. Additionally, 
  -- the market_cap_usd value is extracted from the JSON field, which represents the market 
  -- capitalization in US dollars.
SELECT 
    a.coin,
    AVG(a.price - b.price) as average_increase,
    MAX((a.json->'market_data'->'market_cap'->>'usd')::numeric) as market_cap_usd

FROM 
    the_groups a
JOIN 
    the_groups b ON a.coin = b.coin AND a.drop_group = b.drop_group + 1
GROUP BY 
    a.coin;
