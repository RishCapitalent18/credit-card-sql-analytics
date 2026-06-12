# 💳 Credit Card Fraud & Spending Analytics

> SQL-driven fraud detection and spending analysis on 1M+ synthetic credit card transactions using DuckDB.

---

## Business Questions Answered

1. **Which categories drive the most spend — and the most fraud?**
2. **How does fraud rate change month over month?**
3. **Which individual transactions are anomalously large for that customer?**
4. **Which states have the highest fraud concentration?**
5. **How do we tier customers by risk exposure?**
6. **Which merchants are most associated with fraud?**
7. **What time of day do fraudulent transactions peak?**

---

## Key Findings

- Fraud is concentrated in **specific hours** (late night / early morning), not spread evenly across the day
- Anomaly detection via customer-baseline comparison (`amt > 2× customer avg`) surfaces a disproportionate share of fraud
- A small number of merchants account for a large fraction of total fraud dollar value
- State-level fraud rates vary significantly — geographic clustering suggests coordinated fraud patterns

---

## Tech Stack

- **DuckDB** — in-process SQL engine, no server required
- **Python + pandas** — orchestration and CSV export
- **SQL** — window functions, CTEs, aggregations, date truncation

---

## How to Run

```bash
# Install dependency
pip install duckdb pandas

# Run all analyses (outputs saved to results/)
python analysis.py
```

Results are exported as CSVs to the `results/` folder, one file per analysis.

---

## Project Structure

```
credit-card-sql-analytics/
├── analysis.py        # Runs all 7 queries, prints results, exports CSVs
├── queries.sql        # Raw SQL queries with business question comments
├── requirements.txt
└── README.md
```

---

## Dataset

Synthetic credit card transactions dataset from [Kaggle](https://www.kaggle.com/datasets/priyamchoksi/credit-card-transactions-dataset).

- 1M+ transactions across real US merchant categories
- Labeled fraud column (`is_fraud`) for ground truth validation
- Covers cardholder demographics, merchant location, and transaction metadata

---

## SQL Techniques Used

- `WITH` (CTEs) for multi-step logic
- `DATE_TRUNC` for time-series bucketing
- `EXTRACT` for hour-of-day analysis
- `CASE WHEN` for risk tier classification
- Window-style self-join for per-customer anomaly baseline
- `HAVING` for post-aggregation filtering

---

## Author

**Rishabh Karthik Ramesh** — MS Computer Engineering, Virginia Tech  
[LinkedIn](https://www.linkedin.com/in/rishabh-karthik-ramesh/) · [GitHub](https://github.com/RishCapitalent18) · rishabhkramesh@gmail.com
