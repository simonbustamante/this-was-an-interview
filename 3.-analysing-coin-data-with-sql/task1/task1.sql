--SQL Query to get average price for each coin by month.
SELECT coin,
       DATE_TRUNC('month', date) AS month,
       AVG(price) AS average_price
FROM coin_data
GROUP BY coin, DATE_TRUNC('month', date)
ORDER BY coin, month;