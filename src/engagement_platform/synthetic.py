"""Deterministic synthetic data generation with no external data sources."""

from __future__ import annotations

import csv
import random
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path

from engagement_platform.models import Customer, Transaction


def generate_customers(count: int, seed: int, as_of: date) -> list[Customer]:
    if count < 1:
        raise ValueError("count must be positive")
    randomizer = random.Random(seed)
    regions = ("north", "south")
    segments = ("starter", "standard", "premium")
    return [
        Customer(
            customer_id=f"customer_{index:06d}",
            region=regions[index % len(regions)],
            segment=randomizer.choice(segments),
            registration_date=as_of - timedelta(days=randomizer.randint(1, 900)),
            engagement_score=round(randomizer.random(), 4),
        )
        for index in range(1, count + 1)
    ]


def generate_transactions(
    customers: list[Customer], seed: int, as_of: date, maximum_per_customer: int = 8
) -> list[Transaction]:
    if maximum_per_customer < 0:
        raise ValueError("maximum_per_customer cannot be negative")
    randomizer = random.Random(seed + 1)
    transactions: list[Transaction] = []
    sequence = 1
    for customer in customers:
        transaction_count = randomizer.randint(0, maximum_per_customer)
        for _ in range(transaction_count):
            transactions.append(
                Transaction(
                    transaction_id=f"transaction_{sequence:08d}",
                    customer_id=customer.customer_id,
                    product_id=f"item_{randomizer.randint(1, 40):03d}",
                    transaction_date=as_of - timedelta(days=randomizer.randint(0, 240)),
                    amount=round(randomizer.uniform(8.0, 280.0), 2),
                )
            )
            sequence += 1
    return transactions


def write_csv(records: list[Customer] | list[Transaction], path: Path) -> None:
    """Write generated dataclass records to a local CSV file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        raise ValueError("records cannot be empty")
    fieldnames = list(asdict(records[0]).keys())
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))
