"""
Credit Card Transaction Analytics
----------------------------------
Fraud detection and spending analysis using DuckDB + SQL.

Run with:  python analysis.py
Outputs:   results/ folder (CSV files, one per analysis)
"""

import os
import duckdb
import pandas as pd

CSV_PATH = "C:/projects/credit_card_transactions.csv"
RESULTS_DIR = "results"

os.makedirs(RESULTS_DIR, exist_ok=True)

print("Loading data...")
con = duckdb.connect()
con.execute(f"""
    CREATE TABLE transactions AS
    SELECT * FROM read_csv_auto('{CSV_PATH}')
""")

total = con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
fraud = con.execute("SELECT SUM(is_fraud) FROM transactions").fetchone()[0]
print(f"Loaded {total:,} transactions | {int(fraud):,} fraudulent ({100*fraud/total:.2f}%)\n")


# ---------------------------------------------------------------------------
# Q1: Spending by category
# ---------------------------------------------------------------------------
print("Q1: Spending by category...")
q1 = con.execute("""
    SELECT
        category,
        COUNT(*)                                            AS transaction_count,
        ROUND(SUM(amt), 2)                                 AS total_spend,
        ROUND(AVG(amt), 2)                                 AS avg_transaction,
        SUM(is_fraud)                                      AS fraud_count,
        ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2)        AS fraud_rate_pct
    FROM transactions
    GROUP BY category
    ORDER BY total_spend DESC
""").fetchdf()
q1.to_csv(f"{RESULTS_DIR}/01_spending_by_category.csv", index=False)
print(q1.to_string(index=False))
print()


# ---------------------------------------------------------------------------
# Q2: Monthly transaction trends
# ---------------------------------------------------------------------------
print("Q2: Monthly trends...")
q2 = con.execute("""
    SELECT
        DATE_TRUNC('month', trans_date_trans_time)         AS month,
        COUNT(*)                                            AS transaction_count,
        ROUND(SUM(amt), 2)                                 AS total_spend,
        SUM(is_fraud)                                      AS fraud_count,
        ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2)        AS fraud_rate_pct
    FROM transactions
    GROUP BY 1
    ORDER BY 1
""").fetchdf()
q2.to_csv(f"{RESULTS_DIR}/02_monthly_trends.csv", index=False)
print(q2.to_string(index=False))
print()


# ---------------------------------------------------------------------------
# Q3: Anomaly detection — transactions > 2x customer average
# ---------------------------------------------------------------------------
print("Q3: Anomaly detection (spend > 2x customer average)...")
q3 = con.execute("""
    WITH customer_avg AS (
        SELECT
            cc_num,
            AVG(amt)    AS avg_spend
        FROM transactions
        GROUP BY cc_num
    )
    SELECT
        t.trans_num,
        t.cc_num,
        t.first || ' ' || t.last         AS customer_name,
        t.trans_date_trans_time,
        t.merchant,
        t.category,
        ROUND(t.amt, 2)                  AS amount,
        ROUND(ca.avg_spend, 2)           AS customer_avg,
        ROUND(t.amt / ca.avg_spend, 2)   AS spend_ratio,
        t.is_fraud
    FROM transactions t
    JOIN customer_avg ca ON t.cc_num = ca.cc_num
    WHERE t.amt > 2 * ca.avg_spend
      AND t.amt > 50
    ORDER BY spend_ratio DESC
    LIMIT 50
""").fetchdf()
q3.to_csv(f"{RESULTS_DIR}/03_anomalies.csv", index=False)
print(f"  Found {len(q3)} anomalous transactions (top 50 shown)")
print(q3.head(10).to_string(index=False))
print()


# ---------------------------------------------------------------------------
# Q4: Fraud rate by state
# ---------------------------------------------------------------------------
print("Q4: Fraud by state...")
q4 = con.execute("""
    SELECT
        state,
        COUNT(*)                                            AS total_transactions,
        SUM(is_fraud)                                      AS fraud_count,
        ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2)        AS fraud_rate_pct,
        ROUND(SUM(CASE WHEN is_fraud = 1 THEN amt ELSE 0 END), 2) AS fraud_amount
    FROM transactions
    GROUP BY state
    HAVING COUNT(*) > 100
    ORDER BY fraud_rate_pct DESC
    LIMIT 15
""").fetchdf()
q4.to_csv(f"{RESULTS_DIR}/04_fraud_by_state.csv", index=False)
print(q4.to_string(index=False))
print()


# ---------------------------------------------------------------------------
# Q5: Customer risk segmentation
# ---------------------------------------------------------------------------
print("Q5: Customer risk segmentation...")
q5 = con.execute("""
    WITH customer_stats AS (
        SELECT
            cc_num,
            first || ' ' || last                            AS customer_name,
            COUNT(*)                                        AS total_transactions,
            ROUND(SUM(amt), 2)                              AS total_spend,
            SUM(is_fraud)                                   AS fraud_count,
            ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2)     AS fraud_rate_pct
        FROM transactions
        GROUP BY cc_num, first, last
    )
    SELECT
        *,
        CASE
            WHEN fraud_count >= 3 OR fraud_rate_pct >= 10 THEN 'HIGH RISK'
            WHEN fraud_count >= 1 OR fraud_rate_pct >= 5  THEN 'MEDIUM RISK'
            ELSE 'LOW RISK'
        END AS risk_tier
    FROM customer_stats
    ORDER BY fraud_count DESC, total_spend DESC
""").fetchdf()
q5.to_csv(f"{RESULTS_DIR}/05_customer_risk_segments.csv", index=False)

risk_summary = q5.groupby("risk_tier").agg(
    customers=("cc_num", "count"),
    total_fraud=("fraud_count", "sum")
).reset_index()
print(risk_summary.to_string(index=False))
print(f"  Full customer risk table saved to results/")
print()


# ---------------------------------------------------------------------------
# Q6: Top merchants by fraud
# ---------------------------------------------------------------------------
print("Q6: Top merchants by fraud rate...")
q6 = con.execute("""
    SELECT
        merchant,
        category,
        COUNT(*)                                            AS total_transactions,
        SUM(is_fraud)                                      AS fraud_count,
        ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2)        AS fraud_rate_pct,
        ROUND(SUM(CASE WHEN is_fraud = 1 THEN amt ELSE 0 END), 2) AS fraud_amount
    FROM transactions
    GROUP BY merchant, category
    HAVING SUM(is_fraud) >= 3
    ORDER BY fraud_rate_pct DESC
    LIMIT 20
""").fetchdf()
q6.to_csv(f"{RESULTS_DIR}/06_top_fraud_merchants.csv", index=False)
print(q6.to_string(index=False))
print()


# ---------------------------------------------------------------------------
# Q7: Fraud by hour of day
# ---------------------------------------------------------------------------
print("Q7: Fraud by hour of day...")
q7 = con.execute("""
    SELECT
        EXTRACT(HOUR FROM trans_date_trans_time)::INT       AS hour_of_day,
        COUNT(*)                                            AS total_transactions,
        SUM(is_fraud)                                       AS fraud_count,
        ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2)         AS fraud_rate_pct,
        ROUND(AVG(amt), 2)                                  AS avg_amount
    FROM transactions
    GROUP BY 1
    ORDER BY 1
""").fetchdf()
q7.to_csv(f"{RESULTS_DIR}/07_fraud_by_hour.csv", index=False)
print(q7.to_string(index=False))
print()


print("=" * 60)
print(f"All results saved to ./{RESULTS_DIR}/")
print("=" * 60)
