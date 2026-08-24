from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List

from app.models.audit import AuditEvent
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.failure import FailureInfo


class RecoveryActionType(str, Enum):
    retry = "retry"
    send_reminder = "send_reminder"
    create_payment_link = "create_payment_link"
    promise_to_pay = "promise_to_pay"
    escalate = "escalate"
    stop = "stop"


class RecoveryStatus(str, Enum):
    pending = "pending"
    investigating = "investigating"
    action_scheduled = "action_scheduled"
    recovered = "recovered"
    failed = "failed"
    escalated = "escalated"
    stopped = "stopped"


class RecoveryAction(BaseModel):
    action_type: RecoveryActionType
    reason: str
    scheduled_after_minutes: Optional[int] = None


class RecoveryCase(BaseModel):
    case_id: str
    payment: Payment
    subscription: Subscription
    failure: FailureInfo
    recovery_status: RecoveryStatus = RecoveryStatus.pending
    selected_action: Optional[RecoveryAction] = None
    amount_recovered: int = 0
    audit_trail: List[AuditEvent] = Field(default_factory=list)