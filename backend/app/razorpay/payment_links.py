from uuid import uuid4

from app.models.recovery import (
    RecoveryCase,
)

from app.razorpay.client import (
    client,
)


def create_recovery_payment_link(
    case: RecoveryCase,
):
    """
    Create a real Razorpay Test Mode
    Payment Link for a recovery case.

    Every request gets a unique reference_id
    so the same recovery case can be tested
    multiple times during development.
    """

    amount_paise = int(
        case.payment.amount * 100
    )

    if amount_paise <= 0:
        raise ValueError(
            "Payment Link amount must be greater than zero."
        )

    # Razorpay reference IDs should be unique.
    unique_suffix = uuid4().hex[:8]

    reference_id = (
        f"recovery_"
        f"{case.case_id}_"
        f"{unique_suffix}"
    )

    payload = {
        "amount": amount_paise,
        "currency": (
            case.payment.currency
        ),
        "accept_partial": False,
        "reference_id": reference_id,
        "description": (
            f"Recovery payment for "
            f"{case.subscription.plan_name}"
        ),
        "notes": {
            "recovery_case_id": (
                case.case_id
            ),
            "original_payment_id": (
                case.payment.payment_id
            ),
            "subscription_id": (
                case.subscription.subscription_id
            ),
        },
    }

    try:
        result = (
            client.payment_link.create(
                payload
            )
        )

    except Exception as exc:
        raise RuntimeError(
            "Razorpay Payment Link creation failed: "
            f"{str(exc)}"
        ) from exc

    payment_link_id = (
        result.get("id")
    )

    payment_link_url = (
        result.get("short_url")
    )

    payment_link_status = (
        result.get("status")
    )

    if not payment_link_id:
        raise RuntimeError(
            "Razorpay response did not contain "
            "a Payment Link ID."
        )

    if not payment_link_url:
        raise RuntimeError(
            "Razorpay response did not contain "
            "a Payment Link URL."
        )

    return {
        "id": payment_link_id,
        "short_url": payment_link_url,
        "status": payment_link_status,
        "reference_id": reference_id,
    }