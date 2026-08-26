from app.models.ai_decision import (
    AIDecision,
    AIRecommendedAction,
    SafetyValidationResult,
)

from app.models.recovery import (
    RecoveryCase,
    RecoveryStatus,
)

from app.models.subscription import (
    MandateStatus,
)


MAX_PAYMENT_ATTEMPTS = 3
MAX_RECOVERY_ATTEMPTS = 3


def validate_ai_decision(
    case: RecoveryCase,
    decision: AIDecision,
) -> SafetyValidationResult:
    """
    Validate an AI recommendation before any action
    is allowed to execute.
    """

    proposed_action = (
        decision.recommended_action
    )

    # --------------------------------
    # Rule 1:
    # Recovered cases must stop.
    # --------------------------------

    if (
        case.recovery_status
        == RecoveryStatus.recovered
    ):
        return SafetyValidationResult(
            approved=False,
            original_action=proposed_action,
            final_action=AIRecommendedAction.stop,
            reason=(
                "Case is already recovered. "
                "No further recovery action is allowed."
            ),
        )

    # --------------------------------
    # Rule 2:
    # Never retry an inactive mandate.
    # --------------------------------

    if (
        proposed_action
        == AIRecommendedAction.retry
        and case.subscription.mandate_status
        in {
            MandateStatus.expired,
            MandateStatus.revoked,
            MandateStatus.inactive,
        }
    ):
        return SafetyValidationResult(
            approved=False,
            original_action=proposed_action,
            final_action=(
                AIRecommendedAction.create_payment_link
            ),
            reason=(
                "Automatic retry blocked because "
                "the mandate is not active."
            ),
        )

    # --------------------------------
    # Rule 3:
    # Stop excessive payment retries.
    # --------------------------------

    if (
        proposed_action
        == AIRecommendedAction.retry
        and case.payment.attempt_number
        >= MAX_PAYMENT_ATTEMPTS
    ):
        return SafetyValidationResult(
            approved=False,
            original_action=proposed_action,
            final_action=AIRecommendedAction.escalate,
            reason=(
                "Maximum payment retry attempts "
                "have been reached."
            ),
        )

    # --------------------------------
    # Rule 4:
    # Stop excessive recovery actions.
    # --------------------------------

    if (
        case.recovery_attempts
        >= MAX_RECOVERY_ATTEMPTS
    ):
        return SafetyValidationResult(
            approved=False,
            original_action=proposed_action,
            final_action=AIRecommendedAction.escalate,
            reason=(
                "Maximum recovery attempts reached."
            ),
        )

    # --------------------------------
    # Rule 5:
    # Low-confidence AI decisions
    # should not automatically act.
    # --------------------------------

    if decision.confidence < 0.60:
        return SafetyValidationResult(
            approved=False,
            original_action=proposed_action,
            final_action=AIRecommendedAction.escalate,
            reason=(
                "AI confidence is below the "
                "automatic-action threshold."
            ),
        )

    # --------------------------------
    # Rule 6:
    # Unknown diagnosis should be
    # treated conservatively.
    # --------------------------------

    if (
        decision.diagnosis.value == "unknown"
        and proposed_action
        not in {
            AIRecommendedAction.escalate,
            AIRecommendedAction.stop,
        }
    ):
        return SafetyValidationResult(
            approved=False,
            original_action=proposed_action,
            final_action=AIRecommendedAction.escalate,
            reason=(
                "Unknown failure diagnosis cannot "
                "trigger an automatic recovery action."
            ),
        )

    # --------------------------------
    # Everything passed.
    # --------------------------------

    return SafetyValidationResult(
        approved=True,
        original_action=proposed_action,
        final_action=proposed_action,
        reason="AI recommendation passed all safety checks.",
    )