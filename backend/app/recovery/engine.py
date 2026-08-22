from app.models.recovery import (
    RecoveryCase,
    RecoveryAction,
    RecoveryActionType,
    RecoveryStatus,
)

from app.models.subscription import MandateStatus
from app.recovery.rules import RECOVERY_RULES


MAX_RETRY_ATTEMPTS = 3


def decide_recovery_action(case: RecoveryCase) -> RecoveryCase:
    """
    Decide the next safe recovery action for a failed payment.
    """

    # Safety rule 1:
    # Never continue recovery if the case is already complete.
    if case.recovery_status in {
        RecoveryStatus.recovered,
        RecoveryStatus.stopped,
        RecoveryStatus.escalated,
    }:
        return case

    # Safety rule 2:
    # Stop automatic retries after the maximum allowed attempts.
    if case.payment.attempt_number >= MAX_RETRY_ATTEMPTS:
        case.selected_action = RecoveryAction(
            action_type=RecoveryActionType.escalate,
            reason="Maximum retry attempts reached. Escalating for manual review.",
        )

        case.recovery_status = RecoveryStatus.escalated

        return case

    # Safety rule 3:
    # Invalid mandate should never trigger another automatic mandate retry.
    if case.subscription.mandate_status in {
        MandateStatus.expired,
        MandateStatus.revoked,
        MandateStatus.inactive,
    }:
        case.selected_action = RecoveryAction(
            action_type=RecoveryActionType.create_payment_link,
            reason="Mandate is not active. Automatic mandate retry is blocked.",
        )

        case.recovery_status = RecoveryStatus.action_scheduled

        return case

    rule = RECOVERY_RULES.get(case.failure.category)

    if not rule:
        case.selected_action = RecoveryAction(
            action_type=RecoveryActionType.escalate,
            reason="No safe recovery rule exists for this failure.",
        )

        case.recovery_status = RecoveryStatus.escalated

        return case

    case.selected_action = RecoveryAction(
        action_type=rule["action"],
        reason=rule["reason"],
        scheduled_after_minutes=rule["delay_minutes"],
    )

    case.recovery_status = RecoveryStatus.action_scheduled

    return case

def calculate_decision_summary(cases):
    action_counts = {}

    for case in cases:
        if case.selected_action is None:
            continue

        action = case.selected_action.action_type.value

        action_counts[action] = (
            action_counts.get(action, 0) + 1
        )

    return {
        "total_cases": len(cases),
        "action_breakdown": action_counts,
    }

def process_recovery_batch(cases):
    return [
        decide_recovery_action(case)
        for case in cases
    ]