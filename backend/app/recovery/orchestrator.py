from app.models.audit import AuditEventType
from app.models.recovery import (
    RecoveryCase,
    RecoveryActionType,
    RecoveryStatus,
)

from app.recovery.executor import execute_recovery_action
from app.recovery.strategy import choose_next_action
from app.services.audit_service import add_audit_event


MAX_WORKFLOW_STEPS = 4


def run_recovery_workflow(
    case: RecoveryCase,
) -> RecoveryCase:
    """
    Run a bounded multi-step recovery workflow.
    """

    step = 0

    while step < MAX_WORKFLOW_STEPS:

        if case.recovery_status == RecoveryStatus.recovered:
            break

        if case.recovery_status in {
            RecoveryStatus.escalated,
            RecoveryStatus.stopped,
        }:
            break

        step += 1

        action = choose_next_action(case)

        case.selected_action = action

        add_audit_event(
            case,
            AuditEventType.action_selected,
            f"Workflow step {step}: selected {action.action_type.value}.",
            {
                "step": step,
                "action": action.action_type.value,
                "reason": action.reason,
            },
        )

        if action.action_type == RecoveryActionType.escalate:
            case.recovery_status = RecoveryStatus.escalated

            add_audit_event(
                case,
                AuditEventType.escalated,
                "Recovery workflow escalated for human review.",
            )

            break

        case.recovery_status = RecoveryStatus.action_scheduled

        execute_recovery_action(case)

        if case.recovery_status == RecoveryStatus.recovered:
            break

        # Failed actions become eligible for another decision.
        if case.recovery_status == RecoveryStatus.failed:
            continue

    if (
        case.recovery_status not in {
            RecoveryStatus.recovered,
            RecoveryStatus.escalated,
            RecoveryStatus.stopped,
        }
        and step >= MAX_WORKFLOW_STEPS
    ):
        case.recovery_status = RecoveryStatus.escalated

        add_audit_event(
            case,
            AuditEventType.escalated,
            "Maximum workflow steps reached. Case escalated.",
            {
                "max_steps": MAX_WORKFLOW_STEPS,
            },
        )

    return case

def run_recovery_workflow_batch(cases):
    return [
        run_recovery_workflow(case)
        for case in cases
    ]