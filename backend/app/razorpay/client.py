import razorpay

from app.config import (
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
)


if (
    not RAZORPAY_KEY_ID
    or not RAZORPAY_KEY_SECRET
):
    raise RuntimeError(
        "Razorpay credentials are missing. "
        "Check RAZORPAY_KEY_ID and "
        "RAZORPAY_KEY_SECRET in your .env file."
    )


client = razorpay.Client(
    auth=(
        RAZORPAY_KEY_ID,
        RAZORPAY_KEY_SECRET,
    )
)