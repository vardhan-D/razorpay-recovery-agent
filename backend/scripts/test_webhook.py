import hashlib
import hmac
import json
import os

import requests
from dotenv import load_dotenv


load_dotenv()


WEBHOOK_SECRET = os.getenv(
    "RAZORPAY_WEBHOOK_SECRET"
)


if not WEBHOOK_SECRET:
    raise ValueError(
        "RAZORPAY_WEBHOOK_SECRET is missing."
    )


payload = {
    "entity": "event",
    "event": "subscription.pending",
    "contains": [
        "subscription",
        "payment",
    ],
    "payload": {
        "subscription": {
            "entity": {
                "id": "sub_test_001",
                "customer_id": "cust_test_001",
                "status": "pending",
                "plan_id": "plan_test_001",
            }
        },
        "payment": {
            "entity": {
                "id": "pay_test_001",
                "amount": 149900,
                "currency": "INR",
                "status": "failed",
                "method": "upi",
                "error_code": "BAD_REQUEST_ERROR",
                "error_description": "Payment failed",
            }
        },
    },
}


raw_body = json.dumps(
    payload,
    separators=(",", ":"),
)


signature = hmac.new(
    key=WEBHOOK_SECRET.encode("utf-8"),
    msg=raw_body.encode("utf-8"),
    digestmod=hashlib.sha256,
).hexdigest()


response = requests.post(
    "http://127.0.0.1:8000/webhooks/razorpay",
    data=raw_body.encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature,
    },
)


print("Status:", response.status_code)

try:
    print("Response:", response.json())
except Exception:
    print("Raw response:", response.text)