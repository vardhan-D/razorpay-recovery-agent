from app.models.audit import AuditEventType
from app.models.recovery import (
    RecoveryCase,
    RecoveryStatus,
)

from app.services.audit_service import (
    add_audit_event,
)


def mark_case_recovered(
    case: RecoveryCase,
) -> RecoveryCase:

    case.recovery_status = (
        RecoveryStatus.recovered
    )

    case.amount_recovered = (
        case.payment.amount
    )

    add_audit_event(
        case,
        AuditEventType.payment_recovered,
        f"Recovered ₹{case.payment.amount} through Razorpay.",
        {
            "amount_recovered": (
                case.payment.amount
            ),
            "payment_link_id": (
                case.payment_link_id
            ),
        },
    )

    return case