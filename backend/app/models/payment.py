from enum import Enum
from pydantic import BaseModel


class PaymentStatus(str, Enum):
    created = "created"
    authorized = "authorized"
    captured = "captured"
    failed = "failed"
    refunded = "refunded"


class PaymentMethod(str, Enum):
    upi_autopay = "upi_autopay"
    card_mandate = "card_mandate"
    payment_link = "payment_link"
    other = "other"


class Payment(BaseModel):
    payment_id: str
    customer_id: str
    subscription_id: str
    amount: int
    currency: str = "INR"
    status: PaymentStatus
    payment_method: PaymentMethod
    attempt_number: int = 1