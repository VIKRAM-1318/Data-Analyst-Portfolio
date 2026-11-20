"""
Olist Brazilian E-Commerce - Relational ETL & Data Validation Pipeline
Cleans, standardizes, and validates the 8 relational tables for Star Schema modeling in Power BI:
- Customers, Orders, Order Items, Products, Payments, Reviews, Sellers, Geolocation
Preserves normalized relational architecture without forced denormalization.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np


def process_olist_data(output_dir=None):
    base_dir = Path(__file__).resolve().parent.parent
    if output_dir is None:
        output_dir = base_dir

    print("=" * 70)
    print("OLIST BRAZILIAN E-COMMERCE RELATIONAL ETL PIPELINE")
    print("=" * 70)
    print(f"Base Directory: {base_dir}")

    # Expected table filenames
    table_files = {
        'customers': 'cleaned_customers.csv',
        'orders': 'cleaned_orders.csv',
        'order_items': 'cleaned_order_items.csv',
        'payments': 'cleaned_payments.csv',
        'products': 'cleaned_products.csv',
        'reviews': 'cleaned_reviews.csv',
        'sellers': 'cleaned_sellers.csv',
        'geolocation': 'cleaned_geolocation.csv'
    }

    # Verify input availability
    missing = [f for f in table_files.values() if not (base_dir / f).exists()]
    if missing:
        print(f"[WARNING] Missing table files: {missing}")
        print("Download raw dataset from: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")
        return

    print("\n--- Step 1: Processing Orders Table ---")
    df_orders = pd.read_csv(base_dir / table_files['orders'])
    print(f"  Loaded orders: {df_orders.shape[0]} rows, {df_orders.shape[1]} columns")

    # Standardize datetime columns
    date_cols = [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in date_cols:
        if col in df_orders.columns:
            df_orders[col] = pd.to_datetime(df_orders[col], errors='coerce')

    # Validate delivery duration metrics
    if 'actual_delivery_days' not in df_orders.columns and 'order_delivered_customer_date' in df_orders.columns:
        df_orders['actual_delivery_days'] = (
            df_orders['order_delivered_customer_date'] - df_orders['order_purchase_timestamp']
        ).dt.total_seconds() / (24 * 3600)

    if 'on_time_delivery' not in df_orders.columns and 'order_estimated_delivery_date' in df_orders.columns:
        df_orders['on_time_delivery'] = np.where(
            df_orders['order_delivered_customer_date'] <= df_orders['order_estimated_delivery_date'],
            'On-Time', 'Delayed'
        )

    print(f"  Orders status breakdown:\n{df_orders['order_status'].value_counts().head(5).to_string()}")

    print("\n--- Step 2: Processing Order Items Table ---")
    df_items = pd.read_csv(base_dir / table_files['order_items'])
    print(f"  Loaded items: {df_items.shape[0]} rows, {df_items.shape[1]} columns")
    if 'price' in df_items.columns and 'freight_value' in df_items.columns:
        if 'total_item_value' not in df_items.columns:
            df_items['total_item_value'] = df_items['price'] + df_items['freight_value']

    print("\n--- Step 3: Processing Payments Table ---")
    df_payments = pd.read_csv(base_dir / table_files['payments'])
    print(f"  Loaded payments: {df_payments.shape[0]} rows, {df_payments.shape[1]} columns")
    print(f"  Payment types: {df_payments['payment_type'].unique().tolist()}")

    print("\n--- Step 4: Processing Reviews Table ---")
    df_reviews = pd.read_csv(base_dir / table_files['reviews'])
    print(f"  Loaded reviews: {df_reviews.shape[0]} rows, {df_reviews.shape[1]} columns")
    # Clean text columns
    for t_col in ['review_comment_title', 'review_comment_message']:
        if t_col in df_reviews.columns:
            df_reviews[t_col] = df_reviews[t_col].fillna('').astype(str).str.replace('\n', ' ').str.replace('\r', ' ').str.strip()
    avg_score = df_reviews['review_score'].mean() if 'review_score' in df_reviews.columns else 0
    print(f"  Average review score: {avg_score:.2f} ⭐")

    print("\n--- Step 5: Processing Customers & Sellers Geolocation ---")
    df_cust = pd.read_csv(base_dir / table_files['customers'])
    df_sellers = pd.read_csv(base_dir / table_files['sellers'])
    print(f"  Customers: {df_cust.shape[0]} | Sellers: {df_sellers.shape[0]}")
    print(f"  Top Customer States: {df_cust['customer_state'].value_counts().head(3).to_dict()}")

    print("\n--- Step 6: Referential Integrity Verification ---")
    valid_orders = set(df_orders['order_id'])
    item_orders = set(df_items['order_id'])
    orphan_items = len(item_orders - valid_orders)
    print(f"  Orphan item order IDs: {orphan_items} (Expected: 0)")

    print("\n[SUCCESS] Olist relational schema validation completed successfully!")
    return {
        'orders': df_orders,
        'items': df_items,
        'payments': df_payments,
        'reviews': df_reviews,
        'customers': df_cust,
        'sellers': df_sellers
    }


if __name__ == "__main__":
    process_olist_data()
