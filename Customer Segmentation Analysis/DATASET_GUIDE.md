# 🛍️ Customer Segmentation — Dataset Acquisition & Architecture Guide

## 1. Dataset Overview
This project uses the **Online Retail II Data Set** from the **UCI Machine Learning Repository**, containing real transactions from a UK-based registered non-store online retail business selling gifts and homeware between 01/12/2009 and 09/12/2011.

* **Source:** [UCI Machine Learning Repository - Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
* **Alternative Source:** [Kaggle - Online Retail II Dataset](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci)
* **Raw Size:** ~805,000 transactions across two years.
* **Cleaned Analytical Records:** 805,549 transactions across 5,878 unique customer accounts.

---

## 2. Table Schemas & Fields

### `cleaned_transactions.csv` (73.6 MB)
* `InvoiceNo` (string): 6-digit invoice identifier (numbers starting with 'C' indicate cancellations).
* `StockCode` (string): 5-digit product code.
* `Description` (string): Product title/description.
* `Quantity` (integer): Quantity of each item per transaction.
* `InvoiceDate` (datetime): Timestamp of transaction execution.
* `UnitPrice` (float): Product price per unit in Sterling (£).
* `CustomerID` (integer): 5-digit unique customer account ID.
* `Country` (string): Country of customer domicile.
* `TotalPrice` (float): Line item revenue (`Quantity * UnitPrice`).

### `customer_segments.csv` (520 KB)
* `CustomerID`, `Recency`, `Frequency`, `Monetary`, `Country`
* `Recency_Score`, `Frequency_Score`, `Monetary_Score`, `RFM_Score`
* `Segment`, `Segment_Tier`

---

## 3. Large File Handling & Git LFS
Because `cleaned_transactions.csv` is **73.6 MB**, it exceeds standard GitHub 50 MB warnings.
* Tracked via **Git LFS** in `.gitattributes`:
  ```
  Customer Segmentation Analysis/cleaned_transactions.csv filter=lfs diff=lfs merge=lfs -text
  ```

---

## 4. Running the RFM Segmentation Pipeline
To re-execute the complete RFM engine and generate updated segmentation summaries:

```bash
# From repository root:
python "Customer Segmentation Analysis/Python/rfm_analysis.py"
```
Outputs produced:
- `customer_segments_generated.csv`: Full customer-level RFM scores and segment assignments.
- `segment_summary_statistics.csv`: Segment-level headcount, average metrics, and revenue share.
