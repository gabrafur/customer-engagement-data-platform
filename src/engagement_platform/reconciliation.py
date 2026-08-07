"""Small reconciliation summary for simulated delivery receipts."""

from dataclasses import dataclass

from engagement_platform.models import DeliveryReceipt, DeliveryState


@dataclass(frozen=True, slots=True)
class ReconciliationSummary:
    accepted: int
    retry_exhausted: int


def reconcile(receipts: list[DeliveryReceipt]) -> ReconciliationSummary:
    return ReconciliationSummary(
        accepted=sum(receipt.state == DeliveryState.ACCEPTED for receipt in receipts),
        retry_exhausted=sum(
            receipt.state == DeliveryState.RETRY_EXHAUSTED for receipt in receipts
        ),
    )
