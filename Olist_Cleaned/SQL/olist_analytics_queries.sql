-- ==============================================================================
-- OLIST BRAZILIAN E-COMMERCE MARKETPLACE DATABASE QUERIES
-- Database Dialect: ANSI SQL / PostgreSQL / MySQL / SQL Server
-- Architecture: 8 Relational Tables (Star Schema)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. SCHEMA DEFINITIONS (DDL)
-- ------------------------------------------------------------------------------

CREATE TABLE olist_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(100),
    customer_state VARCHAR(5),
    first_purchase_date DATE,
    customer_order_count INT,
    customer_lat DECIMAL(10,6),
    customer_lng DECIMAL(10,6)
);

CREATE TABLE olist_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_status VARCHAR(30),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    actual_delivery_days DECIMAL(6,2),
    estimated_delivery_days DECIMAL(6,2),
    delivery_delay_days DECIMAL(6,2),
    on_time_delivery VARCHAR(20),          -- 'On-Time' or 'Delayed'
    FOREIGN KEY (customer_id) REFERENCES olist_customers(customer_id)
);

CREATE TABLE olist_order_items (
    order_id VARCHAR(50),
    order_item_id INT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date TIMESTAMP,
    price DECIMAL(10,2),
    freight_value DECIMAL(10,2),
    total_item_value DECIMAL(10,2),
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) REFERENCES olist_orders(order_id)
);

CREATE TABLE olist_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT,
    product_category_name_english VARCHAR(100)
);

CREATE TABLE olist_payments (
    order_id VARCHAR(50),
    payment_sequential INT,
    payment_type VARCHAR(30),              -- 'credit_card', 'boleto', 'voucher', 'debit_card'
    payment_installments INT,
    payment_value DECIMAL(10,2),
    PRIMARY KEY (order_id, payment_sequential),
    FOREIGN KEY (order_id) REFERENCES olist_orders(order_id)
);

CREATE TABLE olist_reviews (
    review_id VARCHAR(50),
    order_id VARCHAR(50),
    review_score INT,                      -- 1 to 5 scale
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,
    review_category VARCHAR(50),
    PRIMARY KEY (review_id, order_id),
    FOREIGN KEY (order_id) REFERENCES olist_orders(order_id)
);

CREATE TABLE olist_sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(10),
    seller_city VARCHAR(100),
    seller_state VARCHAR(5),
    seller_lat DECIMAL(10,6),
    seller_lng DECIMAL(10,6)
);

-- ------------------------------------------------------------------------------
-- 2. EXECUTIVE REVENUE & ORDER KPIS
-- ------------------------------------------------------------------------------

-- Total Marketplace GMV, Orders, Average Order Value (AOV), and Customers
SELECT 
    ROUND(SUM(p.payment_value), 2) AS total_revenue_brl,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    ROUND(SUM(p.payment_value) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2) AS average_order_value_brl,
    ROUND(AVG(r.review_score), 2) AS avg_csat_score
FROM olist_orders o
JOIN olist_payments p ON o.order_id = p.order_id
LEFT JOIN olist_customers c ON o.customer_id = c.customer_id
LEFT JOIN olist_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered';

-- ------------------------------------------------------------------------------
-- 3. LOGISTICS SLA & DELIVERY PERFORMANCE
-- ------------------------------------------------------------------------------

-- On-Time Delivery Rate, SLA Breach %, Average Delivery Lead Time
SELECT 
    COUNT(*) AS total_delivered_orders,
    ROUND(AVG(actual_delivery_days), 2) AS avg_delivery_days,
    ROUND(AVG(estimated_delivery_days), 2) AS avg_estimated_days,
    SUM(CASE WHEN on_time_delivery = 'On-Time' THEN 1 ELSE 0 END) AS on_time_orders,
    ROUND(SUM(CASE WHEN on_time_delivery = 'On-Time' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS on_time_rate_pct,
    ROUND(SUM(CASE WHEN on_time_delivery = 'Delayed' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS sla_breach_rate_pct
FROM olist_orders
WHERE order_status = 'delivered' AND actual_delivery_days IS NOT NULL;

-- Correlation Between Delivery Delay and Review Score
SELECT 
    CASE 
        WHEN o.actual_delivery_days <= 5 THEN '0-5 Days (Express)'
        WHEN o.actual_delivery_days <= 10 THEN '6-10 Days (Fast)'
        WHEN o.actual_delivery_days <= 20 THEN '11-20 Days (Standard)'
        WHEN o.actual_delivery_days <= 30 THEN '21-30 Days (Delayed)'
        ELSE '30+ Days (Severe Delay)'
    END AS delivery_bucket,
    COUNT(*) AS order_volume,
    ROUND(AVG(r.review_score), 2) AS avg_customer_rating,
    ROUND(SUM(CASE WHEN r.review_score = 1 THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS one_star_pct
FROM olist_orders o
JOIN olist_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered' AND o.actual_delivery_days IS NOT NULL
GROUP BY 
    CASE 
        WHEN o.actual_delivery_days <= 5 THEN '0-5 Days (Express)'
        WHEN o.actual_delivery_days <= 10 THEN '6-10 Days (Fast)'
        WHEN o.actual_delivery_days <= 20 THEN '11-20 Days (Standard)'
        WHEN o.actual_delivery_days <= 30 THEN '21-30 Days (Delayed)'
        ELSE '30+ Days (Severe Delay)'
    END
ORDER BY avg_customer_rating DESC;

-- ------------------------------------------------------------------------------
-- 4. PRODUCT CATEGORY & SELLER REVENUE CONTRIBUTION
-- ------------------------------------------------------------------------------

-- Top 15 Product Categories by GMV & Volume
SELECT 
    pr.product_category_name_english AS category,
    COUNT(oi.order_item_id) AS items_sold,
    ROUND(SUM(oi.price), 2) AS total_merchandise_sales_brl,
    ROUND(SUM(oi.freight_value), 2) AS total_freight_revenue_brl,
    ROUND(AVG(oi.price), 2) AS avg_item_price_brl
FROM olist_order_items oi
JOIN olist_products pr ON oi.product_id = pr.product_id
GROUP BY pr.product_category_name_english
ORDER BY total_merchandise_sales_brl DESC
LIMIT 15;

-- Seller Revenue Concentration & Origin State Performance
SELECT 
    s.seller_state,
    COUNT(DISTINCT s.seller_id) AS active_sellers,
    COUNT(oi.order_item_id) AS items_sold,
    ROUND(SUM(oi.price), 2) AS total_sales_brl,
    ROUND(SUM(oi.price) * 100.0 / (SELECT SUM(price) FROM olist_order_items), 2) AS revenue_share_pct
FROM olist_sellers s
JOIN olist_order_items oi ON s.seller_id = oi.seller_id
GROUP BY s.seller_state
ORDER BY total_sales_brl DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 5. PAYMENT METHODS & GEOGRAPHIC DEMAND
-- ------------------------------------------------------------------------------

-- Payment Method Volume, Value, and Installment Behavior
SELECT 
    payment_type,
    COUNT(order_id) AS transaction_count,
    ROUND(SUM(payment_value), 2) AS total_value_brl,
    ROUND(AVG(payment_value), 2) AS avg_transaction_value_brl,
    ROUND(AVG(payment_installments), 1) AS avg_installments
FROM olist_payments
GROUP BY payment_type
ORDER BY total_value_brl DESC;

-- Top 10 Customer Destination States
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    ROUND(SUM(p.payment_value), 2) AS state_gmv_brl,
    ROUND(AVG(o.actual_delivery_days), 1) AS avg_state_delivery_days
FROM olist_orders o
JOIN olist_customers c ON o.customer_id = c.customer_id
JOIN olist_payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY state_gmv_brl DESC
LIMIT 10;
