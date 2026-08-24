from typing import Optional

from app.models.audit import AuditEvent, AuditEventType
from app.models.recovery import RecoveryCase


def add_audit_event(
    case: RecoveryCase,
    event_type: AuditEventType,
    message: str,
    metadata: Optional[dict] = None,
) -> RecoveryCase:

    event = AuditEvent(
        event_type=event_type,
        message=message,
        metadata=metadata,
    )

    case.audit_trail.append(event)

    return case