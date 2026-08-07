import sys
from datetime import date

import pytest

from engagement_platform.spark_features import build_customer_features_spark


@pytest.mark.spark
def test_spark_feature_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    pyspark = pytest.importorskip("pyspark.sql")
    monkeypatch.setenv("PYSPARK_PYTHON", sys.executable)
    monkeypatch.setenv("PYSPARK_DRIVER_PYTHON", sys.executable)
    spark = pyspark.SparkSession.builder.master("local[1]").appName("portfolio-test").getOrCreate()
    try:
        customers = spark.createDataFrame(
            [("c1", "north", "standard", date(2026, 1, 1), 0.6)],
            "customer_id string, region string, segment string, registration_date date, "
            "engagement_score double",
        )
        transactions = spark.createDataFrame(
            [
                ("t1", "c1", "i1", date(2026, 7, 1), 100.0),
                ("t2", "c1", "i2", date(2026, 7, 22), 200.0),
            ],
            "transaction_id string, customer_id string, product_id string, "
            "transaction_date date, amount double",
        )

        row = build_customer_features_spark(customers, transactions, "2026-08-01").first()

        assert row.purchase_frequency == 2
        assert row.average_order_value == 150.0
        assert row.days_since_last_transaction == 10
    finally:
        spark.stop()
