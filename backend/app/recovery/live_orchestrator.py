from app.models.audit import AuditEventType
from app.models.recovery import (
    RecoveryActionType,
    RecoveryCase,
    RecoveryStatus,
)

from app.recovery.strategy import (
    choose_next_action,
)

from app.recovery.live_executor import (
    execute_live_recovery_action,
)

from app.services.audit_service import (
    add_audit_event,
)


def run_live_recovery_workflow(
    case: RecoveryCase,
) -> RecoveryCase:

    action = choose_next_action(case)

    case.selected_action = action

    add_audit_event(
        case,
        AuditEventType.action_selected,
        f"Selected recovery action: {action.action_type.value}.",
        {
            "reason": action.reason,
        },
    )

    if (
        action.action_type
        == RecoveryActionType.escalate
    ):
        case.recovery_status = (
            RecoveryStatus.escalated
        )

        add_audit_event(
            case,
            AuditEventType.escalated,
            "Case escalated for manual review.",
        )

        return case

    case.recovery_status = (
        RecoveryStatus.action_scheduled
    )

    execute_live_recovery_action(
        case
    )

    return case