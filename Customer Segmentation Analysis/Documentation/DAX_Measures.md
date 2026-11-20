# 🛍️ Customer Segmentation & RFM Analysis — DAX Measures Reference Guide

This document catalogs the verified DAX calculations used in the **Customer Segmentation and RFM Analysis Dashboard** (`Customer Segmentation and RFM Analysis Dashboard.pbix`).

---

## 📐 Measure Catalog

### 1. Total Revenue
* **DAX Formula:**
  ```dax
  Total Revenue = SUM(cleaned_transactions[TotalPrice])
  ```
* **Business Definition:** Cumulative sales revenue across all completed online retail transactions.
* **Calculation Logic:** Sum of `TotalPrice` (`Quantity * UnitPrice`) for positive sales lines.
* **Interpretation:** Total transaction volume across the dataset period is **£17.74M** (Cleaned transaction sample: **£8.91M** in 2011).
* **Use Case:** Top-level revenue benchmark and monetary segmentation baseline.

---

### 2. Total Customers
* **DAX Formula:**
  ```dax
  Total Customers = DISTINCTCOUNT(customer_segments[CustomerID])
  ```
* **Business Definition:** Total distinct transacting customer accounts classified into the RFM model.
* **Calculation Logic:** Distinct count of unique customer IDs.
* **Interpretation:** **5,878 total segmented accounts** (4,372 active in single-year window).
* **Use Case:** Customer base sizing, cohort tracking, and market penetration analysis.

---

### 3. Total Orders
* **DAX Formula:**
  ```dax
  Total Orders = DISTINCTCOUNT(cleaned_transactions[InvoiceNo])
  ```
* **Business Definition:** Total distinct retail invoice transactions processed.
* **Calculation Logic:** Distinct count of invoice reference codes.
* **Interpretation:** Over **805,549 transaction line items** consolidated into distinct order baskets.
* **Use Case:** Basket frequency modeling and operational transaction volume.

---

### 4. Average Order Value (AOV)
* **DAX Formula:**
  ```dax
  Average Order Value = DIVIDE([Total Revenue], [Total Orders], 0)
  ```
* **Business Definition:** Mean sales value generated per customer order.
* **Calculation Logic:** Total Revenue divided by Total distinct Orders.
* **Interpretation:** Mean basket size across all customer segments is **£11.06** (Unit level: £280+ per invoice aggregate).
* **Use Case:** Promotional threshold design (e.g. "Free shipping on orders above £50").

---

### 5. Average Recency (Days)
* **DAX Formula:**
  ```dax
  Average Recency = AVERAGE(customer_segments[Recency])
  ```
* **Business Definition:** Mean elapsed calendar days since customers' latest transaction relative to the analysis snapshot date.
* **Interpretation:** Champions average **19.7 days**, while At Risk customers average **467 days**.
* **Use Case:** Win-back campaign timing and churn risk thresholds.
