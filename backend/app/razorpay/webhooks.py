import hashlib
import hmac
import json
from typing import Any, Dict

from app.config import RAZORPAY_WEBHOOK_SECRET


def verify_webhook_signature(
    raw_body: bytes,
    signature: str,
) -> bool:
    if not RAZORPAY_WEBHOOK_SECRET:
        raise ValueError(
            "RAZORPAY_WEBHOOK_SECRET is missing."
        )

    expected_signature = hmac.new(
        key=RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature,
    )


def parse_razorpay_event(
    raw_body: bytes,
) -> Dict[str, Any]:
    payload = json.loads(
        raw_body.decode("utf-8")
    )

    return {
        "event": payload.get("event"),
        "payload": payload,
    }