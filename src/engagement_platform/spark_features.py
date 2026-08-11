"""Optional PySpark transformations mirroring the public feature contract."""

from __future__ import annotations

from typing import Any


def build_customer_features_spark(customers: Any, transactions: Any, as_of_date: str) -> Any:
    """Build features with the PySpark DataFrame API and Spark SQL expressions."""

    from pyspark.sql import functions as sf

    eligible = transactions.where(sf.col("transaction_date") <= sf.lit(as_of_date).cast("date"))
    aggregates = eligible.groupBy("customer_id").agg(
        sf.max("transaction_date").alias("last_transaction_date"),
        sf.countDistinct("transaction_id").alias("purchase_frequency"),
        sf.round(sf.avg("amount"), 2).alias("average_order_value"),
    )
    return (
        customers.join(aggregates, "customer_id", "left")
        .withColumn(
            "customer_age_days",
            sf.greatest(
                sf.datediff(sf.lit(as_of_date).cast("date"), sf.col("registration_date")),
                sf.lit(0),
            ),
        )
        .withColumn(
            "days_since_last_transaction",
            sf.coalesce(
                sf.datediff(
                    sf.lit(as_of_date).cast("date"), sf.col("last_transaction_date")
                ),
                sf.lit(365),
            ),
        )
        .fillna({"purchase_frequency": 0, "average_order_value": 0.0})
        .select(
            "customer_id",
            "region",
            "segment",
            "customer_age_days",
            "days_since_last_transaction",
            "purchase_frequency",
            "average_order_value",
            "engagement_score",
        )
    )
