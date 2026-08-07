"""Composable data-quality checks for synthetic pipeline records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from engagement_platform.models import Customer, Recommendation, Transaction


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    passed: bool
    failed_records: int
    description: str


@dataclass(frozen=True, slots=True)
class DataQualityReport:
    checks: tuple[CheckResult, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def failure_count(self) -> int:
        return sum(check.failed_records for check in self.checks)

    def require_pass(self) -> None:
        failed = [check.name for check in self.checks if not check.passed]
        if failed:
            raise DataQualityError(f"Data quality checks failed: {', '.join(failed)}")


class DataQualityError(ValueError):
    """Raised when a required quality gate fails."""


def _result(name: str, failures: int, description: str) -> CheckResult:
    return CheckResult(name, failures == 0, failures, description)


def validate_inputs(
    customers: list[Customer], transactions: list[Transaction], as_of: date
) -> DataQualityReport:
    customer_ids = [customer.customer_id for customer in customers]
    transaction_ids = [transaction.transaction_id for transaction in transactions]
    known_customers = set(customer_ids)
    checks = (
        _result(
            "unique_customer_id",
            len(customer_ids) - len(set(customer_ids)),
            "Customer identifiers must be unique.",
        ),
        _result(
            "unique_transaction_id",
            len(transaction_ids) - len(set(transaction_ids)),
            "Transaction identifiers must be unique.",
        ),
        _result(
            "valid_engagement_score",
            sum(not 0.0 <= customer.engagement_score <= 1.0 for customer in customers),
            "Engagement scores must be between zero and one.",
        ),
        _result(
            "known_transaction_customer",
            sum(transaction.customer_id not in known_customers for transaction in transactions),
            "Every transaction must reference an input customer.",
        ),
        _result(
            "non_negative_amount",
            sum(transaction.amount < 0 for transaction in transactions),
            "Transaction amounts cannot be negative.",
        ),
        _result(
            "as_of_boundary",
            sum(transaction.transaction_date > as_of for transaction in transactions),
            "Input transactions cannot exceed the processing boundary.",
        ),
    )
    return DataQualityReport(checks)


def validate_recommendations(
    recommendations: list[Recommendation], regional_limits: dict[str, int]
) -> DataQualityReport:
    keys = [item.idempotency_key for item in recommendations]
    region_counts = {
        region: sum(item.region == region for item in recommendations) for region in regional_limits
    }
    checks = (
        _result(
            "unique_idempotency_key",
            len(keys) - len(set(keys)),
            "Each recommendation must have a unique idempotency key in one batch.",
        ),
        _result(
            "normalized_score",
            sum(not 0.0 <= item.score <= 1.0 for item in recommendations),
            "Recommendation scores must be normalized.",
        ),
        _result(
            "regional_limit",
            sum(region_counts[region] > limit for region, limit in regional_limits.items()),
            "Recommendation counts must respect configured regional limits.",
        ),
    )
    return DataQualityReport(checks)
