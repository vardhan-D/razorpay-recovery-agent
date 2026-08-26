from app.razorpay.client import get_razorpay_client
from app.models.recovery import RecoveryCase


def create_recovery_payment_link(
    case: RecoveryCase,
) -> dict:
    """
    Create a Razorpay Test Mode Payment Link
    for a failed recurring payment.
    """

    client = get_razorpay_client()

    amount_paise = case.payment.amount * 100

    reference_id = (
        f"recovery_{case.case_id}"
    )

    payload = {
        "amount": amount_paise,
        "currency": case.payment.currency,
        "reference_id": reference_id,
        "description": (
            f"Recovery payment for "
            f"{case.subscription.subscription_id}"
        ),
        "notes": {
            "recovery_case_id": case.case_id,
            "original_payment_id": case.payment.payment_id,
            "subscription_id": case.subscription.subscription_id,
        },
    }

    payment_link = (
        client.payment_link.create(
            payload
        )
    )

    return payment_link