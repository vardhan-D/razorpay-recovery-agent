from app.models.audit import AuditEventType
from app.models.recovery import (
    RecoveryActionType,
    RecoveryCase,
    RecoveryStatus,
)

from app.recovery.tools import (
    execute_payment_link_tool,
)

from app.services.audit_service import (
    add_audit_event,
)


def execute_live_recovery_action(
    case: RecoveryCase,
) -> RecoveryCase:

    if case.selected_action is None:
        return case

    action_type = (
        case.selected_action.action_type
    )

    if (
        action_type
        == RecoveryActionType.create_payment_link
    ):
        execute_payment_link_tool(case)

        case.recovery_status = (
            RecoveryStatus.action_scheduled
        )

        return case

    if (
        action_type
        == RecoveryActionType.escalate
    ):
        case.recovery_status = (
            RecoveryStatus.escalated
        )

        add_audit_event(
            case,
            AuditEventType.escalated,
            "Case escalated for human review.",
        )

        return case

    add_audit_event(
        case,
        AuditEventType.action_scheduled,
        f"Live execution not yet implemented for {action_type.value}.",
        {
            "action": action_type.value,
        },
    )

    return case