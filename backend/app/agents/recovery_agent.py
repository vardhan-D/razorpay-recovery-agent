from app.agents.diagnosis_agent import (
    diagnose_case_with_ai,
)

from app.models.audit import AuditEventType
from app.models.recovery import RecoveryCase
from app.models.recovery import (
    RecoveryCase,
    RecoveryAction,
    RecoveryActionType,
)
from app.recovery.ai_safety import (
    validate_ai_decision,
)

from app.recovery.tool_router import (
    execute_approved_action,
)

from app.services.audit_service import (
    add_audit_event,
)


def run_ai_recovery_step(
    case: RecoveryCase,
) -> RecoveryCase:
    """
    Run one AI-powered recovery step:

    Observe
    -> Diagnose
    -> Safety validate
    -> Execute approved tool
    """

    # 1. AI reasoning
    ai_decision = diagnose_case_with_ai(
        case
    )

    add_audit_event(
        case,
        AuditEventType.failure_classified,
        (
            "AI diagnosis: "
            f"{ai_decision.diagnosis.value}"
        ),
        {
            "confidence": (
                ai_decision.confidence
            ),
            "recommended_action": (
                ai_decision.recommended_action.value
            ),
            "reasoning_summary": (
                ai_decision.reasoning_summary
            ),
            "source": "llama3.2",
        },
    )

    # 2. Deterministic safety validation
    safety_result = validate_ai_decision(
        case,
        ai_decision,
    )

    add_audit_event(
        case,
        AuditEventType.action_selected,
        (
            "Safety validation completed. "
            f"Final action: "
            f"{safety_result.final_action.value}"
        ),
        {
            "approved": (
                safety_result.approved
            ),
            "original_action": (
                safety_result.original_action.value
            ),
            "final_action": (
                safety_result.final_action.value
            ),
            "reason": (
                safety_result.reason
            ),
        },
    )

    final_action = (
        safety_result.final_action.value
    )

    recovery_action = RecoveryAction(
        action_type=RecoveryActionType(
            final_action
        ),
        reason=(
            ai_decision.reasoning_summary
            if safety_result.approved
            else safety_result.reason
        ),
        scheduled_after_minutes=(
            ai_decision.retry_after_minutes
            if final_action == "retry"
            else None
        ),
    )

    case.selected_action = (
        recovery_action
    )

    case.action_history.append(
        recovery_action
    )

    # 3. Execute trusted backend tool
    case = execute_approved_action(
        case,
        safety_result,
    )

    return case