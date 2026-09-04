from app.models.audit import (
    AuditEventType,
)

from app.models.recovery import (
    RecoveryCase,
    RecoveryStatus,
)

from app.razorpay.payment_links import (
    create_recovery_payment_link,
)

from app.services.audit_service import (
    add_audit_event,
)


def execute_payment_link_tool(
    case: RecoveryCase,
) -> RecoveryCase:
    """
    Create a real Razorpay Test Mode Payment Link
    for the outstanding recovery amount.

    The created link is stored on the RecoveryCase
    so it can be displayed in the frontend and later
    correlated with Razorpay payment webhooks.
    """

    try:
        result = create_recovery_payment_link(
            case
        )

        payment_link_id = result.get("id")
        payment_link_url = result.get("short_url")

        if (
            not payment_link_id
            or not payment_link_url
        ):
            raise ValueError(
                "Razorpay did not return a valid "
                "payment link ID or short URL."
            )

        # --------------------------------
        # Persist Razorpay link information
        # on the recovery case.
        # --------------------------------

        case.payment_link_id = (
            payment_link_id
        )

        case.payment_link_url = (
            payment_link_url
        )

        # --------------------------------
        # Record recovery attempt.
        # --------------------------------

        case.recovery_attempts += 1

        # --------------------------------
        # Creating a link does NOT mean the
        # revenue has been recovered yet.
        #
        # The case waits until Razorpay sends
        # a successful payment webhook.
        # --------------------------------

        case.recovery_status = (
            RecoveryStatus.waiting
        )

        # --------------------------------
        # Audit successful tool execution.
        # --------------------------------

        add_audit_event(
            case=case,
            event_type=(
                AuditEventType.action_executed
            ),
            message=(
                "Razorpay recovery payment "
                "link created."
            ),
            metadata={
                "action": (
                    "create_payment_link"
                ),
                "payment_link_id": (
                    payment_link_id
                ),
                "payment_link_url": (
                    payment_link_url
                ),
                "source": (
                    "razorpay_payment_link_tool"
                ),
            },
        )

        return case

    except Exception as exc:
        # --------------------------------
        # Audit the tool failure.
        # --------------------------------

        add_audit_event(
            case=case,
            event_type=(
                AuditEventType.action_failed
            ),
            message=(
                "Failed to create Razorpay "
                "recovery payment link."
            ),
            metadata={
                "action": (
                    "create_payment_link"
                ),
                "error": str(exc),
                "source": (
                    "razorpay_payment_link_tool"
                ),
            },
        )

        # Important:
        # Do not silently hide Razorpay errors.
        # Let the API surface the failure so
        # we can debug it properly.
        raise