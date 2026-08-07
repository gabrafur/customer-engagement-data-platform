"""Feature engineering implemented independently for synthetic records."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from engagement_platform.models import Customer, CustomerFeatures, Transaction


def build_customer_features(
    customers: list[Customer], transactions: list[Transaction], as_of: date
) -> list[CustomerFeatures]:
    grouped: dict[str, list[Transaction]] = defaultdict(list)
    for transaction in transactions:
        if transaction.transaction_date > as_of:
            continue
        grouped[transaction.customer_id].append(transaction)

    result: list[CustomerFeatures] = []
    for customer in customers:
        history = grouped[customer.customer_id]
        last_date = max((item.transaction_date for item in history), default=None)
        days_since = (as_of - last_date).days if last_date else 365
        average_value = sum(item.amount for item in history) / len(history) if history else 0.0
        result.append(
            CustomerFeatures(
                customer_id=customer.customer_id,
                region=customer.region,
                segment=customer.segment,
                customer_age_days=max((as_of - customer.registration_date).days, 0),
                days_since_last_transaction=days_since,
                purchase_frequency=len(history),
                average_order_value=round(average_value, 2),
                engagement_score=customer.engagement_score,
            )
        )
    return result
