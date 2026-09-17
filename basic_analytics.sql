-- ============================================================
-- Ecommerce Data Warehouse - Basic Analytics
-- Database: ecommerce_dw
-- Layers: DWD -> DWS -> ADS
-- ============================================================

USE ecommerce_dw;

-- 1. DWD: Check order data
SELECT
    order_id,
    user_id,
    product_category,
    amount,
    order_time
FROM dwd_orders
LIMIT 10;

-- 2. DWD: Sales by product category
SELECT
    product_category,
    COUNT(*) AS order_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS avg_amount
FROM dwd_orders
GROUP BY product_category
ORDER BY total_amount DESC;

-- 3. DWD: Monthly sales trend
SELECT
    DATE_FORMAT(order_time, 'yyyy-MM') AS order_month,
    COUNT(*) AS order_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM dwd_orders
GROUP BY DATE_FORMAT(order_time, 'yyyy-MM')
ORDER BY order_month;

-- 4. DWD: City-level order statistics
SELECT
    u.city,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.amount), 2) AS total_amount,
    ROUND(AVG(o.amount), 2) AS avg_amount
FROM dwd_orders o
JOIN dwd_users u
    ON o.user_id = u.user_id
GROUP BY u.city
ORDER BY total_amount DESC
LIMIT 10;

-- 5. DWS: Query city order statistics
SELECT
    city,
    order_count,
    total_amount,
    avg_amount
FROM dws_city_order_stats
ORDER BY total_amount DESC
LIMIT 10;

-- 6. ADS: City sales ranking
SELECT
    city,
    order_count,
    total_amount,
    avg_amount,
    sales_rank
FROM ads_city_sales_rank
ORDER BY sales_rank
LIMIT 10;
