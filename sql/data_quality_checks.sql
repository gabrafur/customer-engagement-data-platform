-- Generic expectations for the synthetic demonstration tables.
SELECT
  COUNT_IF(customer_id IS NULL) AS missing_customer_ids,
  COUNT_IF(engagement_score NOT BETWEEN 0.0 AND 1.0) AS invalid_engagement_scores
FROM demo.bronze.customers;

SELECT
  customer_id,
  recommendation_type,
  COUNT(*) AS duplicate_count
FROM demo.gold.customer_recommendations
GROUP BY customer_id, recommendation_type
HAVING COUNT(*) > 1;
