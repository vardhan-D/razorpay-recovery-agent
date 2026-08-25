from typing import Any, Dict


def parse_razorpay_event(payload: Dict[str, Any]) -> dict:
    """
    Extract the basic event information from a Razorpay webhook payload.
    """

    event_name = payload.get("event")

    return {
        "event": event_name,
        "payload": payload,
    }