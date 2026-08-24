from app.models.failure import FailureCategory
from app.models.recovery import (
    RecoveryAction,
    RecoveryActionType,
    RecoveryCase,
)


MAX_RECOVERY_ACTIONS = 3


def choose_next_action(case: RecoveryCase) -> RecoveryAction:
    """
    Choose the next recovery action based on:
    - failure category
    - previous actions
    - number of attempts
    """

    previous_actions = [
        action.action_type
        for action in case.action_history
    ]

    if len(previous_actions) >= MAX_RECOVERY_ACTIONS:
        return RecoveryAction(
            action_type=RecoveryActionType.escalate,
            reason="Maximum recovery actions reached."
        )

    category = case.failure.category

    # -------------------------
    # Insufficient funds
    # -------------------------

    if category == FailureCategory.insufficient_funds:

        if RecoveryActionType.retry not in previous_actions:
            return RecoveryAction(
                action_type=RecoveryActionType.retry,
                reason="First recovery attempt: retry after balance may become available.",
                scheduled_after_minutes=1440,
            )

        if RecoveryActionType.send_reminder not in previous_actions:
            return RecoveryAction(
                action_type=RecoveryActionType.send_reminder,
                reason="Retry failed. Ask customer to complete payment.",
            )

        return RecoveryAction(
            action_type=RecoveryActionType.create_payment_link,
            reason="Previous recovery attempts failed. Offer fallback payment link.",
        )

    # -------------------------
    # Bank unavailable
    # -------------------------

    if category == FailureCategory.bank_unavailable:

        retry_count = previous_actions.count(
            RecoveryActionType.retry
        )

        if retry_count == 0:
            return RecoveryAction(
                action_type=RecoveryActionType.retry,
                reason="Transient bank failure. Retry after short cooldown.",
                scheduled_after_minutes=180,
            )

        if retry_count == 1:
            return RecoveryAction(
                action_type=RecoveryActionType.retry,
                reason="First retry failed. Try once more after longer cooldown.",
                scheduled_after_minutes=720,
            )

        return RecoveryAction(
            action_type=RecoveryActionType.create_payment_link,
            reason="Repeated issuer failures. Switch to customer-driven payment.",
        )

    # -------------------------
    # Mandate issue
    # -------------------------

    if category == FailureCategory.mandate_issue:

        if RecoveryActionType.create_payment_link not in previous_actions:
            return RecoveryAction(
                action_type=RecoveryActionType.create_payment_link,
                reason="Mandate is inactive. Automatic retries are not allowed.",
            )

        return RecoveryAction(
            action_type=RecoveryActionType.send_reminder,
            reason="Payment link was not successful. Remind customer.",
        )

    # -------------------------
    # Authentication issue
    # -------------------------

    if category == FailureCategory.authentication_issue:

        if RecoveryActionType.send_reminder not in previous_actions:
            return RecoveryAction(
                action_type=RecoveryActionType.send_reminder,
                reason="Customer authentication is required.",
            )

        return RecoveryAction(
            action_type=RecoveryActionType.create_payment_link,
            reason="Authentication reminder did not resolve payment.",
        )

    # -------------------------
    # Technical problem
    # -------------------------

    if category == FailureCategory.technical_error:

        if RecoveryActionType.retry not in previous_actions:
            return RecoveryAction(
                action_type=RecoveryActionType.retry,
                reason="Temporary technical failure. Retry after cooldown.",
                scheduled_after_minutes=60,
            )

        return RecoveryAction(
            action_type=RecoveryActionType.create_payment_link,
            reason="Technical retry failed. Provide alternative payment route.",
        )

    # -------------------------
    # Unknown
    # -------------------------

    return RecoveryAction(
        action_type=RecoveryActionType.escalate,
        reason="Failure cannot be safely diagnosed."
    )