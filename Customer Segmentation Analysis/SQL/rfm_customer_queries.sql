-- ==============================================================================
-- CUSTOMER SEGMENTATION & RFM ANALYTICS DATABASE QUERIES
-- Database Dialect: ANSI SQL / PostgreSQL / MySQL / SQL Server
-- Dataset: Online Retail II (Cleaned Transactions & RFM Segments)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. TABLE DEFINITIONS (DDL)
-- ------------------------------------------------------------------------------

CREATE TABLE retail_transactions (
    InvoiceNo VARCHAR(30),
    StockCode VARCHAR(30),
    Description VARCHAR(255),
    Quantity INT,
    InvoiceDate TIMESTAMP,
    UnitPrice DECIMAL(10,2),
    CustomerID INT,
    Country VARCHAR(100),
    TotalPrice DECIMAL(10,2)
);

CREATE TABLE customer_rfm_segments (
    CustomerID INT PRIMARY KEY,
    Recency INT,                           -- Days since latest purchase
    Frequency INT,                         -- Total distinct orders
    Monetary DECIMAL(12,2),                -- Lifetime spend
    Country VARCHAR(100),
    Last_Purchase_Date TIMESTAMP,
    Customer_Tenure_Days INT,
    Recency_Score INT,                     -- 1 to 5
    Frequency_Score INT,                   -- 1 to 5
    Monetary_Score INT,                    -- 1 to 5
    RFM_Score INT,                         -- Composite integer code e.g. 555, 111
    Segment VARCHAR(50),                   -- 'Champions', 'Loyal', 'At Risk', etc.
    Segment_Tier VARCHAR(50)               -- 'High Value', 'Medium Value', 'Low Value/At Risk'
);

-- ------------------------------------------------------------------------------
-- 2. RFM METRICS COMPUTATION ENGINE (PURE SQL IMPLEMENTATION)
-- ------------------------------------------------------------------------------

-- Pure SQL implementation to derive Recency, Frequency, and Monetary directly from raw logs
WITH customer_aggregations AS (
    SELECT 
        CustomerID,
        Country,
        MAX(InvoiceDate) AS last_purchase,
        MIN(InvoiceDate) AS first_purchase,
        COUNT(DISTINCT InvoiceNo) AS order_frequency,
        ROUND(SUM(Quantity * UnitPrice), 2) AS total_monetary
    FROM retail_transactions
    WHERE CustomerID IS NOT NULL 
      AND Quantity > 0 
      AND UnitPrice > 0
    GROUP BY CustomerID, Country
),
rfm_raw_metrics AS (
    SELECT 
        CustomerID,
        Country,
        -- Snapshot anchor: 1 day past max dataset transaction date
        DATEDIFF(day, last_purchase, (SELECT MAX(InvoiceDate) + INTERVAL '1 day' FROM retail_transactions)) AS recency_days,
        order_frequency,
        total_monetary,
        DATEDIFF(day, first_purchase, (SELECT MAX(InvoiceDate) + INTERVAL '1 day' FROM retail_transactions)) AS tenure_days
    FROM customer_aggregations
),
rfm_ntile_scores AS (
    SELECT 
        CustomerID,
        Country,
        recency_days,
        order_frequency,
        total_monetary,
        -- Recency: Inverted (lowest recency days = highest score 5)
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        -- Frequency & Monetary: Standard (highest count/spend = highest score 5)
        NTILE(5) OVER (ORDER BY order_frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY total_monetary ASC) AS m_score
    FROM rfm_raw_metrics
)
SELECT 
    CustomerID,
    Country,
    recency_days,
    order_frequency,
    total_monetary,
    r_score,
    f_score,
    m_score,
    (r_score * 100 + f_score * 10 + m_score) AS composite_rfm_score
FROM rfm_ntile_scores
ORDER BY total_monetary DESC
LIMIT 20;

-- ------------------------------------------------------------------------------
-- 3. SEGMENT PERFORMANCE & REVENUE CONCENTRATION (PARETO ANALYSIS)
-- ------------------------------------------------------------------------------

-- Revenue, Headcount, and Value Contribution by Customer Segment
SELECT 
    Segment,
    Segment_Tier,
    COUNT(CustomerID) AS customer_count,
    ROUND(COUNT(CustomerID) * 100.0 / (SELECT COUNT(*) FROM customer_rfm_segments), 2) AS pct_of_customers,
    ROUND(SUM(Monetary), 2) AS total_revenue,
    ROUND(SUM(Monetary) * 100.0 / (SELECT SUM(Monetary) FROM customer_rfm_segments), 2) AS pct_of_revenue,
    ROUND(AVG(Monetary), 2) AS avg_monetary_spend,
    ROUND(AVG(Recency), 1) AS avg_recency_days,
    ROUND(AVG(Frequency), 1) AS avg_order_frequency
FROM customer_rfm_segments
GROUP BY Segment, Segment_Tier
ORDER BY total_revenue DESC;

-- Segment Tier Breakdown (High vs Medium vs Low Value/At Risk)
SELECT 
    Segment_Tier,
    COUNT(CustomerID) AS customers_in_tier,
    ROUND(SUM(Monetary), 2) AS tier_revenue,
    ROUND(SUM(Monetary) * 100.0 / (SELECT SUM(Monetary) FROM customer_rfm_segments), 2) AS revenue_share_pct,
    ROUND(AVG(Monetary), 2) AS avg_customer_value
FROM customer_rfm_segments
GROUP BY Segment_Tier
ORDER BY tier_revenue DESC;

-- ------------------------------------------------------------------------------
-- 4. PRODUCT AFFINITY BY SEGMENT (WHAT DO CHAMPIONS BUY?)
-- ------------------------------------------------------------------------------

-- Top 10 Products Purchased by 'Champions' Segment
SELECT 
    t.Description AS product_name,
    COUNT(DISTINCT t.CustomerID) AS champion_buyers,
    SUM(t.Quantity) AS units_purchased,
    ROUND(SUM(t.TotalPrice), 2) AS revenue_from_champions
FROM retail_transactions t
JOIN customer_rfm_segments s ON t.CustomerID = s.CustomerID
WHERE s.Segment = 'Champions'
GROUP BY t.Description
ORDER BY revenue_from_champions DESC
LIMIT 10;

-- Top Products Purchased by 'At Risk' Customers (Candidates for Win-Back Campaigns)
SELECT 
    t.Description AS product_name,
    COUNT(DISTINCT t.CustomerID) AS at_risk_buyers,
    ROUND(SUM(t.TotalPrice), 2) AS past_revenue_at_risk
FROM retail_transactions t
JOIN customer_rfm_segments s ON t.CustomerID = s.CustomerID
WHERE s.Segment = 'At Risk'
GROUP BY t.Description
ORDER BY past_revenue_at_risk DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 5. GEOGRAPHIC SEGMENT DISTRIBUTION
-- ------------------------------------------------------------------------------

-- Champions & Loyal Customers by Country
SELECT 
    Country,
    COUNT(CustomerID) AS total_customers,
    SUM(CASE WHEN Segment = 'Champions' THEN 1 ELSE 0 END) AS champions_count,
    SUM(CASE WHEN Segment = 'Loyal' THEN 1 ELSE 0 END) AS loyal_count,
    ROUND(SUM(Monetary), 2) AS country_revenue
FROM customer_rfm_segments
GROUP BY Country
ORDER BY country_revenue DESC
LIMIT 10;
