import razorpay

from app.config import (
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
)


def get_razorpay_client():
    """
    Create and return an authenticated Razorpay client.
    """

    if not RAZORPAY_KEY_ID:
        raise ValueError(
            "RAZORPAY_KEY_ID is missing."
        )

    if not RAZORPAY_KEY_SECRET:
        raise ValueError(
            "RAZORPAY_KEY_SECRET is missing."
        )

    client = razorpay.Client(
        auth=(
            RAZORPAY_KEY_ID,
            RAZORPAY_KEY_SECRET,
        )
    )

    return client