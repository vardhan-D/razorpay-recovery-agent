from enum import Enum
from pydantic import BaseModel


class SubscriptionStatus(str, Enum):
    active = "active"
    paused = "paused"
    cancelled = "cancelled"
    completed = "completed"
    expired = "expired"


class MandateStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    revoked = "revoked"
    expired = "expired"
    unknown = "unknown"


class Subscription(BaseModel):
    subscription_id: str
    customer_id: str
    plan_name: str
    amount: int
    currency: str = "INR"
    status: SubscriptionStatus
    mandate_status: MandateStatus