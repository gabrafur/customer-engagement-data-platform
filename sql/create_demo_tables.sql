CREATE SCHEMA IF NOT EXISTS demo.bronze;
CREATE SCHEMA IF NOT EXISTS demo.silver;
CREATE SCHEMA IF NOT EXISTS demo.gold;

CREATE TABLE IF NOT EXISTS demo.bronze.customers (
  customer_id STRING NOT NULL,
  region STRING NOT NULL,
  segment STRING NOT NULL,
  registration_date DATE NOT NULL,
  engagement_score DOUBLE NOT NULL
) USING DELTA;

CREATE TABLE IF NOT EXISTS demo.gold.customer_recommendations (
  recommendation_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  region STRING NOT NULL,
  recommendation_type STRING NOT NULL,
  score DOUBLE NOT NULL,
  regional_rank INT NOT NULL,
  idempotency_key STRING NOT NULL,
  created_at TIMESTAMP NOT NULL
) USING DELTA;
