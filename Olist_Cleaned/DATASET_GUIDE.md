# 📦 Olist Brazilian E-Commerce — Dataset Acquisition & Architecture Guide

## 1. Dataset Overview
This project utilizes the **Brazilian E-Commerce Public Dataset by Olist**, available on Kaggle. It contains real commercial data from 100,000 orders made at Olist Store between 2016 and 2018 in Brazil.

* **Source:** [Kaggle - Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
* **Architecture:** 8 Normalized Relational Tables (Star Schema)
* **Volume:** 500,000+ total rows across all relational tables.

---

## 2. Relational Schema Architecture

```
                    ┌─────────────────────────┐
                    │    cleaned_customers    │
                    └────────────┬────────────┘
                                 │ 1
                                 │
                                 │ N
┌──────────────────┐ 1       N ┌─┴────────────────────────┐ 1       N ┌──────────────────┐
│ cleaned_products ├───────────┤   cleaned_order_items    ├───────────┤ cleaned_sellers  │
└──────────────────┘           └───────────┬──────────────┘           └──────────────────┘
                                           │ N
                                           │
                                           │ 1
┌──────────────────┐ N       1 ┌───────────┴──────────────┐ 1       N ┌──────────────────┐
│ cleaned_payments ├───────────┤      cleaned_orders      ├───────────┤ cleaned_reviews  │
└──────────────────┘           └──────────────────────────┘           └──────────────────┘
```

---

## 3. Table Catalog & Primary Keys

| Table Name | Primary Key | Foreign Keys | Row Count | Description |
|:---|:---|:---|:---:|:---|
| `cleaned_orders.csv` | `order_id` | `customer_id` | 98,666 | Order lifecycle timestamps, status, delivery SLA days |
| `cleaned_order_items.csv` | `(order_id, order_item_id)` | `product_id`, `seller_id` | 112,650 | Product SKU, price, freight value, item sequence |
| `cleaned_customers.csv` | `customer_id` | None | 99,441 | Customer unique identifier, zip code, city, state, geo |
| `cleaned_products.csv` | `product_id` | None | 32,951 | Dimensions, weight, photos, English category name |
| `cleaned_payments.csv` | `(order_id, payment_sequential)` | None | 103,056 | Payment type, installments, payment value |
| `cleaned_reviews.csv` | `(review_id, order_id)` | None | 98,465 | Review score (1-5), comment title, message, date |
| `cleaned_sellers.csv` | `seller_id` | None | 3,095 | Seller zip code, city, state, latitude, longitude |
| `cleaned_geolocation.csv` | None | None | 19,015 | Deduplicated Brazilian postal code coordinates |

---

## 4. Running the ETL Pipeline
To execute the automated Python ETL and validation pipeline:

```bash
# From repository root:
python "Olist_Cleaned/Python/process_olist_data.py"
```

The script will:
1. Parse ISO timestamps into standard datetime formats.
2. Validate delivery transit calculations and SLA flags.
3. Clean review comment whitespace and newline shifts.
4. Verify referential integrity between orders, order items, and customers.
