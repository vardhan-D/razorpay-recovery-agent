from app.models.ai_decision import (
    AIRecommendedAction,
    SafetyValidationResult,
)

from app.models.audit import AuditEventType
from app.models.recovery import (
    RecoveryCase,
    RecoveryStatus,
)

from app.recovery.tools import (
    execute_payment_link_tool,
)

from app.services.audit_service import (
    add_audit_event,
)


def execute_approved_action(
    case: RecoveryCase,
    safety_result: SafetyValidationResult,
) -> RecoveryCase:
    """
    Route a safety-approved AI decision
    to the correct trusted backend tool.
    """

    action = safety_result.final_action

    # -----------------------------
    # CREATE PAYMENT LINK
    # -----------------------------

    if (
        action
        == AIRecommendedAction.create_payment_link
    ):
        add_audit_event(
            case,
            AuditEventType.action_selected,
            "Tool router selected Razorpay Payment Link tool.",
            {
                "action": action.value,
                "source": "ai_tool_router",
            },
        )

        return execute_payment_link_tool(
            case
        )

    # -----------------------------
    # RETRY
    # -----------------------------

    if action == AIRecommendedAction.retry:
        return schedule_retry_tool(
            case
        )

    # -----------------------------
    # SEND REMINDER
    # -----------------------------

    if (
        action
        == AIRecommendedAction.send_reminder
    ):
        return send_reminder_tool(
            case
        )

    # -----------------------------
    # PROMISE TO PAY
    # -----------------------------

    if (
        action
        == AIRecommendedAction.promise_to_pay
    ):
        return create_promise_to_pay_tool(
            case
        )

    # -----------------------------
    # ESCALATE
    # -----------------------------

    if (
        action
        == AIRecommendedAction.escalate
    ):
        return escalate_tool(
            case
        )

    # -----------------------------
    # STOP
    # -----------------------------

    if action == AIRecommendedAction.stop:
        return stop_tool(
            case
        )

    raise ValueError(
        f"Unsupported recovery action: {action}"
    )

def schedule_retry_tool(
    case: RecoveryCase,
) -> RecoveryCase:
    """
    Schedule a retry.

    This does not directly charge money yet.
    It records a bounded retry action.
    """

    case.recovery_attempts += 1

    case.recovery_status = (
        RecoveryStatus.waiting
    )

    add_audit_event(
        case,
        AuditEventType.action_scheduled,
        "Retry recovery action scheduled.",
        {
            "recovery_attempt": (
                case.recovery_attempts
            ),
            "source": "ai_tool_router",
        },
    )

    return case


def send_reminder_tool(
    case: RecoveryCase,
) -> RecoveryCase:
    """
    Record a customer reminder action.

    Messaging provider integration comes later.
    """

    case.recovery_attempts += 1

    case.recovery_status = (
        RecoveryStatus.waiting
    )

    add_audit_event(
        case,
        AuditEventType.action_executed,
        "Customer payment reminder queued.",
        {
            "recovery_attempt": (
                case.recovery_attempts
            ),
            "source": "ai_tool_router",
        },
    )

    return case


def create_promise_to_pay_tool(
    case: RecoveryCase,
) -> RecoveryCase:
    """
    Create a placeholder promise-to-pay workflow.
    """

    case.recovery_attempts += 1

    case.recovery_status = (
        RecoveryStatus.waiting
    )

    add_audit_event(
        case,
        AuditEventType.action_executed,
        "Promise-to-pay workflow created.",
        {
            "recovery_attempt": (
                case.recovery_attempts
            ),
            "source": "ai_tool_router",
        },
    )

    return case


def escalate_tool(
    case: RecoveryCase,
) -> RecoveryCase:

    case.recovery_status = (
        RecoveryStatus.escalated
    )

    add_audit_event(
        case,
        AuditEventType.escalated,
        "Case escalated for human review.",
        {
            "source": "ai_tool_router",
        },
    )

    return case


def stop_tool(
    case: RecoveryCase,
) -> RecoveryCase:

    case.recovery_status = (
        RecoveryStatus.stopped
    )

    add_audit_event(
        case,
        AuditEventType.stopped,
        "Recovery workflow stopped safely.",
        {
            "source": "ai_tool_router",
        },
    )

    return case