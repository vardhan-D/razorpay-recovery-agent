from app.models.failure import FailureCategory
from app.models.recovery import RecoveryActionType


RECOVERY_RULES = {
    FailureCategory.insufficient_funds: {
        "action": RecoveryActionType.retry,
        "delay_minutes": 1440,
        "reason": "Customer may have insufficient balance. Retry after 24 hours.",
    },

    FailureCategory.bank_unavailable: {
        "action": RecoveryActionType.retry,
        "delay_minutes": 180,
        "reason": "Bank appears temporarily unavailable. Retry after a cooldown.",
    },

    FailureCategory.mandate_issue: {
        "action": RecoveryActionType.create_payment_link,
        "delay_minutes": None,
        "reason": "Mandate is invalid or inactive, so an automatic retry should not be attempted.",
    },

    FailureCategory.authentication_issue: {
        "action": RecoveryActionType.send_reminder,
        "delay_minutes": None,
        "reason": "Customer interaction is required to complete authentication.",
    },

    FailureCategory.technical_error: {
        "action": RecoveryActionType.retry,
        "delay_minutes": 60,
        "reason": "Temporary technical failure. Retry after a short cooldown.",
    },

    FailureCategory.unknown: {
        "action": RecoveryActionType.escalate,
        "delay_minutes": None,
        "reason": "Failure reason is unknown and should not be automatically acted upon.",
    },
}