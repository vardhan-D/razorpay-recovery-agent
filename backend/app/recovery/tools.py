from app.models.audit import AuditEventType
from app.models.recovery import RecoveryCase
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
    Execute a real Razorpay Payment Link action.
    """

    try:
        result = create_recovery_payment_link(
            case
        )

        payment_link_id = result.get("id")
        short_url = result.get("short_url")

        case.payment_link_id = payment_link_id
        case.payment_link_url = short_url

        add_audit_event(
            case,
            AuditEventType.action_executed,
            "Razorpay recovery Payment Link created.",
            {
                "payment_link_id": payment_link_id,
                "short_url": short_url,
                "source": "razorpay_test_mode",
            },
        )

        return case

    except Exception as exc:

        add_audit_event(
            case,
            AuditEventType.action_failed,
            "Razorpay Payment Link creation failed.",
            {
                "error": str(exc),
            },
        )

        return case