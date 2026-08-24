from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AuditEventType(str, Enum):
    case_created = "case_created"
    payment_failed = "payment_failed"
    failure_classified = "failure_classified"
    action_selected = "action_selected"
    action_scheduled = "action_scheduled"
    action_executed = "action_executed"
    action_failed = "action_failed"
    payment_recovered = "payment_recovered"
    escalated = "escalated"
    stopped = "stopped"


class AuditEvent(BaseModel):
    event_type: AuditEventType
    message: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: Optional[dict] = None