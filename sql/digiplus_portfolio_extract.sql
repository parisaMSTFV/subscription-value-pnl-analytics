-- Daily activity contract
SELECT
    customer_id,
    CAST(order_date AS date) AS day,
    rfm_segment,
    membership_active,
    orders,
    items,
    nmv,
    pc1,
    shipping_contribution,
    benefit_cost,
    service_cost
FROM {{customer_daily_activity}}
WHERE order_date >= {{history_start}}
  AND order_date < {{analysis_end}};

-- Subscription-plan contract
SELECT
    subscription_id,
    customer_id,
    start_date,
    duration_days,
    paid_price,
    plan_name
FROM {{subscription_plans}}
WHERE start_date < {{as_of_date}};
