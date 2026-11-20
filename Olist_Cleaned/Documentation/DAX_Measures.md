# 🇧🇷 Olist E-Commerce Marketplace — DAX Measures Reference Guide

This document catalogs the verified DAX calculations used in the **Enterprise-Grade E-Commerce Marketplace Dashboard** (`Enterprise-Grade E-Commerce Marketplace Dashboard.pbix`).

---

## 📐 Measure Catalog

### 1. Total Revenue (GMV)
* **DAX Formula:**
  ```dax
  Total Revenue = SUM(cleaned_payments[payment_value])
  ```
* **Business Definition:** Total Gross Merchandise Value (GMV) transacted through the Olist marketplace.
* **Calculation Logic:** Sum of all payment transaction values in the payments table.
* **Interpretation:** Total processed revenue is **R$ 15.44M** (~$3.1M USD).
* **Use Case:** Executive top-line financial scorecard and growth tracking.

---

### 2. Total Orders
* **DAX Formula:**
  ```dax
  Total Orders = DISTINCTCOUNT(cleaned_orders[order_id])
  ```
* **Business Definition:** Count of unique completed and processed purchase orders.
* **Calculation Logic:** Distinct count of primary keys (`order_id`) in the Orders table.
* **Interpretation:** Total transaction volume is **98,666 orders** across Brazil.
* **Use Case:** Marketplace throughput, logistics capacity, and order frequency.

---

### 3. Average Order Value (AOV)
* **DAX Formula:**
  ```dax
  Average Order Value = DIVIDE([Total Revenue], [Total Orders], 0)
  ```
* **Business Definition:** Mean customer basket expenditure per placed order.
* **Calculation Logic:** Total payment revenue divided by unique order count.
* **Interpretation:** Average order size across the platform is **R$ 156.50**.
* **Use Case:** Cross-selling optimization, checkout bundle thresholds, and seller pricing tiers.

---

### 4. Unique Customers
* **DAX Formula:**
  ```dax
  Unique Customers = DISTINCTCOUNT(cleaned_customers[customer_unique_id])
  ```
* **Business Definition:** Total distinct individuals transacting on the marketplace.
* **Calculation Logic:** Distinct count of `customer_unique_id` (accounting for repeat purchasers who receive new `customer_id` keys per order).
* **Interpretation:** Marketplace served **99,441 unique individuals** (~3% repeat purchase rate).
* **Use Case:** Customer acquisition monitoring and retention cohort analysis.

---

### 5. On-Time Delivery Rate %
* **DAX Formula:**
  ```dax
  On-Time Delivery Rate = 
  DIVIDE(
      CALCULATE(COUNTROWS(cleaned_orders), cleaned_orders[on_time_delivery] = "On-Time"),
      CALCULATE(COUNTROWS(cleaned_orders), cleaned_orders[order_status] = "delivered"),
      0
  )
  ```
* **Business Definition:** Percentage of delivered customer orders that arrived on or before the estimated delivery SLA date.
* **Calculation Logic:** Delivered orders where actual date <= estimated date divided by all delivered orders.
* **Interpretation:** Current delivery reliability is **91.88%** on-time.
* **Use Case:** Logistics carrier performance evaluation and SLA compliance.

---

### 6. Average Delivery Days
* **DAX Formula:**
  ```dax
  Average Delivery Days = AVERAGE(cleaned_orders[actual_delivery_days])
  ```
* **Business Definition:** Mean elapsed transit days from customer purchase timestamp to doorstep delivery.
* **Calculation Logic:** Mathematical mean of `actual_delivery_days`.
* **Interpretation:** Average delivery lead time across continental Brazil is **12.56 days**.
* **Use Case:** Freight carrier optimization, regional fulfillment hub placement, and customer promise delivery date calibration.

---

### 7. SLA Breach Rate %
* **DAX Formula:**
  ```dax
  SLA Breach Rate = 
  DIVIDE(
      CALCULATE(COUNTROWS(cleaned_orders), cleaned_orders[on_time_delivery] = "Delayed"),
      CALCULATE(COUNTROWS(cleaned_orders), cleaned_orders[order_status] = "delivered"),
      0
  )
  ```
* **Business Definition:** Percentage of completed shipments that missed the committed customer SLA window.
* **Interpretation:** **8.12% of shipments** arrive late.
* **Use Case:** Customer churn mitigation, refund risk analysis, and carrier penalty enforcement.

---

### 8. Cancellation Rate %
* **DAX Formula:**
  ```dax
  Cancellation Rate = 
  DIVIDE(
      CALCULATE(COUNTROWS(cleaned_orders), cleaned_orders[order_status] = "canceled"),
      COUNTROWS(cleaned_orders),
      0
  )
  ```
* **Business Definition:** Percentage of initiated orders that were canceled prior to fulfillment.
* **Interpretation:** Cancellation rate is **0.63%** (625 orders).
* **Use Case:** Inventory stock-out detection, fraud prevention, and payment failure analysis.

---

### 9. Seller Rating Score
* **DAX Formula:**
  ```dax
  Seller Rating Score = AVERAGE(cleaned_reviews[review_score])
  ```
* **Business Definition:** Aggregate customer satisfaction rating awarded out of 5 stars.
* **Interpretation:** Marketplace average review score is **4.09 ⭐**.
* **Use Case:** Seller badge ranking, algorithm placement, and vendor quality governance.
