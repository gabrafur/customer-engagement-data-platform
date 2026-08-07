"""Simple fictional rules designed only for this portfolio project."""

from engagement_platform.models import CustomerFeatures, RecommendationType


def choose_recommendation(features: CustomerFeatures) -> RecommendationType:
    if features.customer_age_days <= 30:
        return RecommendationType.WELCOME_JOURNEY
    if features.days_since_last_transaction >= 120:
        return RecommendationType.RECONNECT
    if features.purchase_frequency >= 4 and features.average_order_value >= 140:
        return RecommendationType.LOYALTY_THANK_YOU
    if features.engagement_score < 0.30:
        return RecommendationType.RETENTION_CHECKIN
    return RecommendationType.COMMUNITY_UPDATE
