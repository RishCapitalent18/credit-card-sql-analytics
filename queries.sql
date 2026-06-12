-- =============================================================================
-- Credit Card Transaction Analytics — SQL Queries
-- Dataset: Synthetic credit card transactions with fraud labels
-- Tool: DuckDB
-- =============================================================================


-- =============================================================================
-- Q1: Spending by category
-- Business question: Which categories drive the most spend and fraud?
-- =============================================================================
SELECT
    category,
    COUNT(*)                                            AS transaction_count,
    ROUND(SUM(amt), 2)                                 AS total_spend,
    ROUND(AVG(amt), 2)                                 AS avg_transaction,
    SUM(is_fraud)                                      AS fraud_count,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2)        AS fraud_rate_pct
FROM transactions
GROUP BY category
ORDER BY total_spend DESC;


-- =============================================================================
-- Q2: Monthly transaction trends
-- Business question: How does transaction volume and fraud evolve over time?
-- =============================================================================
SELECT
    DATE_TRUNC('month', trans_date_trans_time)         AS month,
    COUNT(*)                                            AS transaction_count,
    ROUND(SUM(amt), 2)                                 AS total_spend,
    SUM(is_fraud)                                      AS fraud_count,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2)        AS fraud_rate_pct
FROM transactions
GROUP BY 1
ORDER BY 1;


-- =============================================================================
-- Q3: Anomaly detection — transactions > 2x a customer's average spend
-- Business question: Which transactions are unusually large for that customer?
-- =============================================================================
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
LIMIT 50;


-- =============================================================================
-- Q4: Fraud rate by state
-- Business question: Which states have the highest fraud concentration?
-- =============================================================================
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
LIMIT 15;


-- =============================================================================
-- Q5: Customer risk segmentation
-- Business question: How do we tier customers by fraud exposure?
-- =============================================================================
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
ORDER BY fraud_count DESC, total_spend DESC;


-- =============================================================================
-- Q6: Top merchants by fraud rate
-- Business question: Which merchants are most associated with fraud?
-- =============================================================================
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
LIMIT 20;


-- =============================================================================
-- Q7: Fraud by hour of day
-- Business question: When are fraudulent transactions most likely to occur?
-- =============================================================================
SELECT
    EXTRACT(HOUR FROM trans_date_trans_time)::INT       AS hour_of_day,
    COUNT(*)                                            AS total_transactions,
    SUM(is_fraud)                                       AS fraud_count,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2)         AS fraud_rate_pct,
    ROUND(AVG(amt), 2)                                  AS avg_amount
FROM transactions
GROUP BY 1
ORDER BY 1;
