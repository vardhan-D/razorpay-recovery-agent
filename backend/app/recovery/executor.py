import random

from app.models.audit import AuditEventType
from app.models.recovery import (
    RecoveryCase,
    RecoveryActionType,
    RecoveryStatus,
)
from app.services.audit_service import add_audit_event
from app.recovery.state_machine import transition_case
from app.models.failure import FailureCategory

SUCCESS_MATRIX = {
    FailureCategory.insufficient_funds: {
        RecoveryActionType.retry: 0.35,
        RecoveryActionType.send_reminder: 0.45,
        RecoveryActionType.create_payment_link: 0.55,
        RecoveryActionType.promise_to_pay: 0.60,
    },

    FailureCategory.bank_unavailable: {
        RecoveryActionType.retry: 0.75,
        RecoveryActionType.send_reminder: 0.20,
        RecoveryActionType.create_payment_link: 0.50,
    },

    FailureCategory.mandate_issue: {
        RecoveryActionType.retry: 0.05,
        RecoveryActionType.create_payment_link: 0.65,
        RecoveryActionType.send_reminder: 0.40,
    },

    FailureCategory.authentication_issue: {
        RecoveryActionType.retry: 0.10,
        RecoveryActionType.send_reminder: 0.60,
        RecoveryActionType.create_payment_link: 0.70,
    },

    FailureCategory.technical_error: {
        RecoveryActionType.retry: 0.70,
        RecoveryActionType.create_payment_link: 0.55,
    },

    FailureCategory.unknown: {
        RecoveryActionType.retry: 0.10,
        RecoveryActionType.send_reminder: 0.20,
        RecoveryActionType.create_payment_link: 0.25,
    },
}


def execute_recovery_action(case: RecoveryCase) -> RecoveryCase:
    """
    Simulate execution of the selected recovery action.
    """

    if case.selected_action is None:
        add_audit_event(
            case,
            AuditEventType.action_failed,
            "No recovery action was selected."
        )
        return case

    action_type = case.selected_action.action_type

    if action_type == RecoveryActionType.escalate:
        if case.recovery_status != RecoveryStatus.escalated:
            transition_case(
                case,
                RecoveryStatus.escalated,
            )

        add_audit_event(
            case,
            AuditEventType.escalated,
            "Case sent for human review."
        )

        return case

    if action_type == RecoveryActionType.stop:
        transition_case(
            case,
            RecoveryStatus.stopped,
        )

        add_audit_event(
            case,
            AuditEventType.stopped,
            "Recovery workflow stopped."
        )

        return case

    case.action_history.append(
        case.selected_action
    )
    
    case.recovery_attempts += 1

    add_audit_event(
        case,
        AuditEventType.action_executed,
        f"Executed recovery action: {action_type.value}.",
        {
            "recovery_attempt": case.recovery_attempts,
            "action": action_type.value,
        },
    )

    category_probabilities = SUCCESS_MATRIX.get(
        case.failure.category,
        {}
    )

    probability = category_probabilities.get(
        action_type,
        0.0,
    )

    success = random.random() < probability

    if success:
        transition_case(
            case,
            RecoveryStatus.recovered,
        )

        case.amount_recovered = case.payment.amount

        add_audit_event(
            case,
            AuditEventType.payment_recovered,
            f"Recovered ₹{case.payment.amount}.",
            {
                "amount_recovered": case.payment.amount,
                "action": action_type.value,
            },
        )

    else:
        transition_case(
            case,
            RecoveryStatus.failed,
        )

        add_audit_event(
            case,
            AuditEventType.action_failed,
            f"Recovery action {action_type.value} did not recover the payment.",
            {
                "action": action_type.value,
            },
        )

    return case

def execute_recovery_batch(cases):
    return [
        execute_recovery_action(case)
        for case in cases
    ]