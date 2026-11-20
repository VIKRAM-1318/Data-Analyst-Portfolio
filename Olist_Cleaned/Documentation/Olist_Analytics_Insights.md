# 🇧🇷 Olist Brazilian E-Commerce — Marketplace Insights & Findings

## Executive Summary
Analysis of Brazil's largest online marketplace ecosystem across 98,666 orders, 3,095 sellers, and 8 relational operational tables reveals critical insights into cross-state fulfillment logistics, category profitability, and customer sentiment drivers.

---

## 1. Top-Line Marketplace Scale
* **Gross Merchandise Value (GMV):** **R$ 15.44M** ($3.1M USD) in processed payments.
* **Order Throughput:** 98,666 orders placed between 2016 and 2018.
* **Average Order Value (AOV):** **R$ 156.50** with ~1.14 items per order.
* **Payment Preferences:**
  * *Credit Card:* 73.9% of GMV (Average 3.5 installments).
  * *Boleto Bancário:* 19.0% of GMV (Standard cash voucher in Brazil).
  * *Voucher / Debit Card:* 7.1% combined.

---

## 2. Logistics & Delivery Lead-Time Challenges
* **Continental Transit Times:** Average delivery lead time across Brazil is **12.56 days**.
* **Regional Delivery Disparity:**
  * *Southeast Region (SP, RJ, MG):* 8.2 to 11.5 days.
  * *North & Northeast Regions (AM, PA, MA):* 22.0 to 28.5 days due to complex Amazonian river transport and road infrastructure.
* **On-Time Performance:** **91.88%** on-time delivery rate; **8.12%** of orders suffer SLA breaches.

---

## 3. Customer Satisfaction (CSAT) & Root Cause of 1-Star Reviews
* **Overall Rating:** **4.09 ⭐** average review score across 98,465 reviews.
  * *5-Star Ratings:* 57.8% of reviews
  * *4-Star Ratings:* 19.3% of reviews
  * *1-Star Ratings:* 11.8% of reviews
* **The Delivery Delay Penalty:**
  * Orders arriving within 5 days achieve an average rating of **4.48 ⭐** (Only 4.2% 1-star reviews).
  * Orders delayed past the estimated SLA date collapse to an average rating of **1.62 ⭐** (**over 68% 1-star reviews**).
* **Finding:** Delivery punctuality is the single most dominant factor dictating customer review scores in Brazilian e-commerce, outweighing product price or packaging quality.

---

## 4. Geographic Concentration & Seller Hubs
* **Demand Concentration:** The state of São Paulo (`SP`) represents **41.7% of all customers** and **42.2% of total marketplace revenue**, followed by Rio de Janeiro (`RJ`, 12.8%) and Minas Gerais (`MG`, 11.6%).
* **Seller Concentration:** Over **70.4% of active sellers** are geographically located within São Paulo state, creating an asymmetric logistics model where goods travel outward from SP across the country.

---

## 5. Strategic Recommendations
1. **Regional Fulfillment Centers:** Establish micro-warehousing partnerships in Northeast Brazil (Recife/Salvador) to slash transit times from 24 days to under 8 days.
2. **Dynamic SLA Buffers:** Automatically expand estimated delivery windows for Northern states by +5 days during rainy seasons to protect customer expectations.
3. **Seller Quality Enforcement:** Implement minimum 4.0 ⭐ rating thresholds for featured seller promotion to reduce order disputes.
