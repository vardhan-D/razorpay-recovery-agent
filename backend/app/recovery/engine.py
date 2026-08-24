from app.models.recovery import (
    RecoveryCase,
    RecoveryAction,
    RecoveryActionType,
    RecoveryStatus,
)

from app.models.subscription import MandateStatus
from app.models.audit import AuditEventType

from app.recovery.rules import RECOVERY_RULES
from app.services.audit_service import add_audit_event


MAX_RETRY_ATTEMPTS = 3


def decide_recovery_action(case: RecoveryCase) -> RecoveryCase:
    """
    Decide the next safe recovery action for a failed payment.
    """

    if case.recovery_status in {
        RecoveryStatus.recovered,
        RecoveryStatus.stopped,
        RecoveryStatus.escalated,
    }:
        return case

    if case.payment.attempt_number >= MAX_RETRY_ATTEMPTS:
        case.selected_action = RecoveryAction(
            action_type=RecoveryActionType.escalate,
            reason="Maximum retry attempts reached. Escalating for manual review.",
        )

        case.recovery_status = RecoveryStatus.escalated

        add_audit_event(
            case,
            AuditEventType.escalated,
            "Maximum retry attempts reached. Case escalated for manual review.",
            {
                "attempt_number": case.payment.attempt_number,
                "max_attempts": MAX_RETRY_ATTEMPTS,
            },
        )

        return case

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

        add_audit_event(
            case,
            AuditEventType.action_selected,
            "Payment link selected because the mandate is inactive.",
            {
                "action": RecoveryActionType.create_payment_link.value,
                "mandate_status": case.subscription.mandate_status.value,
            },
        )

        add_audit_event(
            case,
            AuditEventType.action_scheduled,
            "Fallback payment-link recovery action scheduled.",
        )

        return case

    rule = RECOVERY_RULES.get(case.failure.category)

    if not rule:
        case.selected_action = RecoveryAction(
            action_type=RecoveryActionType.escalate,
            reason="No safe recovery rule exists for this failure.",
        )

        case.recovery_status = RecoveryStatus.escalated

        add_audit_event(
            case,
            AuditEventType.escalated,
            "No safe recovery rule exists. Case escalated.",
            {
                "failure_category": case.failure.category.value,
            },
        )

        return case

    case.selected_action = RecoveryAction(
        action_type=rule["action"],
        reason=rule["reason"],
        scheduled_after_minutes=rule["delay_minutes"],
    )

    case.recovery_status = RecoveryStatus.action_scheduled

    add_audit_event(
        case,
        AuditEventType.action_selected,
        f"Recovery action selected: {rule['action'].value}.",
        {
            "failure_category": case.failure.category.value,
            "action": rule["action"].value,
        },
    )

    add_audit_event(
        case,
        AuditEventType.action_scheduled,
        rule["reason"],
        {
            "scheduled_after_minutes": rule["delay_minutes"],
        },
    )

    return case


def process_recovery_batch(cases):
    return [
        decide_recovery_action(case)
        for case in cases
    ]


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