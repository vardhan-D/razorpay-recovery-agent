from app.agents.recovery_agent import (
    run_ai_recovery_step,
)

from app.models.audit import AuditEventType
from app.models.recovery import (
    RecoveryCase,
    RecoveryStatus,
)

from app.services.audit_service import (
    add_audit_event,
)


MAX_AGENT_STEPS = 4


def run_full_ai_recovery_loop(
    case: RecoveryCase,
) -> RecoveryCase:
    """
    Run a bounded AI recovery loop.

    Observe
    -> Reason
    -> Safety Check
    -> Tool
    -> Observe Again

    until the case is:
    - recovered
    - escalated
    - stopped
    - or max steps are reached
    """

    step = 0

    while step < MAX_AGENT_STEPS:

        if case.recovery_status in {
            RecoveryStatus.recovered,
            RecoveryStatus.escalated,
            RecoveryStatus.stopped,
            RecoveryStatus.waiting,
        }:
            break

        step += 1

        add_audit_event(
            case,
            AuditEventType.action_selected,
            f"Starting AI recovery step {step}.",
            {
                "agent_step": step,
                "source": "llama3.2_agent_loop",
            },
        )

        case = run_ai_recovery_step(
            case
        )

        if case.recovery_status in {
            RecoveryStatus.recovered,
            RecoveryStatus.escalated,
            RecoveryStatus.stopped,
            RecoveryStatus.waiting,
        }:
            break

    if (
        step >= MAX_AGENT_STEPS
        and case.recovery_status
        not in {
            RecoveryStatus.recovered,
            RecoveryStatus.escalated,
            RecoveryStatus.stopped,
        }
    ):
        case.recovery_status = (
            RecoveryStatus.escalated
        )

        add_audit_event(
            case,
            AuditEventType.escalated,
            "Maximum AI recovery steps reached. Case escalated for human review.",
            {
                "max_agent_steps": MAX_AGENT_STEPS,
            },
        )

    return case