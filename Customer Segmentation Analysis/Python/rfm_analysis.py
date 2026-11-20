"""
Customer Segmentation & RFM Analysis Engine
Processes retail transaction logs, validates data integrity, computes Recency,
Frequency, Monetary (RFM) metrics, calculates quantile-based scores (1-5),
and assigns actionable behavioral segments and value tiers.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np


def compute_rfm_analysis(transactions_csv=None, output_dir=None):
    base_dir = Path(__file__).resolve().parent.parent
    if transactions_csv is None:
        transactions_csv = base_dir / "cleaned_transactions.csv"
    if output_dir is None:
        output_dir = base_dir

    print("=" * 70)
    print("CUSTOMER SEGMENTATION & RFM ANALYTICS ENGINE")
    print("=" * 70)
    print(f"Transactions source: {transactions_csv}")

    if not Path(transactions_csv).exists():
        raise FileNotFoundError(
            f"Transactions file not found at: {transactions_csv}\n"
            "Please ensure 'cleaned_transactions.csv' is present in the project directory."
        )

    print("\nStep 1: Ingesting transaction records...")
    df = pd.read_csv(transactions_csv)
    print(f"  Loaded {df.shape[0]:,} transaction rows across {df.shape[1]} columns.")

    # 1. Validation & Hygiene
    print("\nStep 2: Validating transactions and handling data hygiene...")
    # Drop rows without CustomerID
    df = df.dropna(subset=['CustomerID']).copy()
    df['CustomerID'] = df['CustomerID'].astype(int)

    # Ensure InvoiceDate is datetime
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    df = df.dropna(subset=['InvoiceDate']).copy()

    # Calculate TotalPrice if not present
    if 'TotalPrice' not in df.columns:
        df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

    # Filter out cancellation transactions / non-positive amounts
    valid_df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0) & (df['TotalPrice'] > 0)].copy()
    print(f"  Valid analytical transactions: {valid_df.shape[0]:,} records.")
    print(f"  Unique customers: {valid_df['CustomerID'].nunique():,}")

    # 2. RFM Metric Computations
    print("\nStep 3: Calculating customer-level RFM metrics...")
    # Reference snapshot date: 1 day after the latest transaction date
    snapshot_date = valid_df['InvoiceDate'].max() + pd.Timedelta(days=1)
    print(f"  Analysis Snapshot Date: {snapshot_date.strftime('%Y-%m-%d %H:%M:%S')}")

    rfm = valid_df.groupby('CustomerID').agg({
        'InvoiceDate': [
            lambda x: (snapshot_date - x.max()).days,  # Recency
            lambda x: x.max(),                          # Last Purchase Date
            lambda x: (snapshot_date - x.min()).days   # Customer Tenure Days
        ],
        'InvoiceNo': 'nunique',                        # Frequency (distinct orders)
        'TotalPrice': 'sum',                           # Monetary Value
        'Country': 'first'                             # Primary Country
    }).reset_index()

    # Flatten multi-level column names
    rfm.columns = [
        'CustomerID', 'Recency', 'Last_Purchase_Date', 'Customer_Tenure_Days',
        'Frequency', 'Monetary', 'Country'
    ]
    rfm['Monetary'] = rfm['Monetary'].round(2)

    print(f"  Aggregated RFM table shape: {rfm.shape}")

    # 3. Quantile Scoring (1 to 5)
    print("\nStep 4: Computing transparent quantile scores (1 to 5)...")
    # For Recency: lower days = higher score (5 is best)
    # Using rank method='first' to reliably break ties at quantile boundaries
    rfm['Recency_Score'] = pd.qcut(
        rfm['Recency'].rank(method='first', ascending=True),
        q=5, labels=[5, 4, 3, 2, 1]
    ).astype(int)

    # For Frequency: higher frequency = higher score (5 is best)
    rfm['Frequency_Score'] = pd.qcut(
        rfm['Frequency'].rank(method='first', ascending=True),
        q=5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # For Monetary: higher spend = higher score (5 is best)
    rfm['Monetary_Score'] = pd.qcut(
        rfm['Monetary'].rank(method='first', ascending=True),
        q=5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # Combined composite RFM string code
    rfm['RFM_Score'] = (
        rfm['Recency_Score'].astype(str) +
        rfm['Frequency_Score'].astype(str) +
        rfm['Monetary_Score'].astype(str)
    ).astype(int)

    # 4. Behavioral Customer Segmentation Logic
    print("Step 5: Assigning behavioral segments based on RFM profile...")
    def assign_segment(row):
        r = row['Recency_Score']
        f = row['Frequency_Score']
        m = row['Monetary_Score']

        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal'
        elif r >= 4 and f <= 2:
            return 'New Customers' if m <= 2 else 'Potential'
        elif r == 3 and f <= 2:
            return 'Need Attention'
        elif r == 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2:
            return 'About to Sleep' if r == 2 else 'At Risk'
        else:
            return 'At Risk'

    rfm['Segment'] = rfm.apply(assign_segment, axis=1)

    # 5. Value Tier Mapping
    def assign_tier(segment):
        if segment in ['Champions', 'Loyal']:
            return 'High Value'
        elif segment in ['Potential', 'Need Attention', 'New Customers']:
            return 'Medium Value'
        else:
            return 'Low Value/At Risk'

    rfm['Segment_Tier'] = rfm['Segment'].apply(assign_tier)

    # 6. Reorder and export results
    cols_order = [
        'CustomerID', 'Recency', 'Frequency', 'Monetary', 'Country',
        'Last_Purchase_Date', 'Customer_Tenure_Days',
        'Recency_Score', 'Frequency_Score', 'Monetary_Score',
        'RFM_Score', 'Segment', 'Segment_Tier'
    ]
    rfm = rfm[cols_order]

    # Segment Summary Statistics
    summary = rfm.groupby('Segment').agg(
        Customer_Count=('CustomerID', 'count'),
        Avg_Recency_Days=('Recency', 'mean'),
        Avg_Frequency=('Frequency', 'mean'),
        Avg_Monetary=('Monetary', 'mean'),
        Total_Revenue=('Monetary', 'sum')
    ).round(2).reset_index()

    summary['Customer_Share_%'] = (summary['Customer_Count'] * 100.0 / len(rfm)).round(2)
    summary['Revenue_Share_%'] = (summary['Total_Revenue'] * 100.0 / rfm['Monetary'].sum()).round(2)
    summary = summary.sort_values(by='Total_Revenue', ascending=False)

    print("\nSegment Performance Summary:")
    print(summary.to_string(index=False))

    output_csv = Path(output_dir) / "customer_segments_generated.csv"
    rfm.to_csv(output_csv, index=False)
    print(f"\n[SUCCESS] Generated customer segments saved: {output_csv.name}")

    summary_csv = Path(output_dir) / "segment_summary_statistics.csv"
    summary.to_csv(summary_csv, index=False)
    print(f"[SUCCESS] Segment summary table saved: {summary_csv.name}")

    return rfm, summary


if __name__ == "__main__":
    compute_rfm_analysis()
