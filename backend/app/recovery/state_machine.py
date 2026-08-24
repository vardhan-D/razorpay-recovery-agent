from app.models.recovery import RecoveryCase, RecoveryStatus


ALLOWED_TRANSITIONS = {
    RecoveryStatus.pending: {
        RecoveryStatus.investigating,
        RecoveryStatus.action_scheduled,
        RecoveryStatus.escalated,
        RecoveryStatus.stopped,
    },

    RecoveryStatus.investigating: {
        RecoveryStatus.action_scheduled,
        RecoveryStatus.escalated,
        RecoveryStatus.stopped,
    },

    RecoveryStatus.action_scheduled: {
        RecoveryStatus.recovered,
        RecoveryStatus.failed,
        RecoveryStatus.escalated,
        RecoveryStatus.stopped,
    },

    RecoveryStatus.failed: {
        RecoveryStatus.investigating,
        RecoveryStatus.action_scheduled,
        RecoveryStatus.escalated,
        RecoveryStatus.stopped,
    },

    RecoveryStatus.recovered: set(),
    RecoveryStatus.escalated: set(),
    RecoveryStatus.stopped: set(),
}


def transition_case(
    case: RecoveryCase,
    new_status: RecoveryStatus,
) -> RecoveryCase:

    current_status = case.recovery_status

    allowed = ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed:
        raise ValueError(
            f"Invalid recovery state transition: "
            f"{current_status.value} -> {new_status.value}"
        )

    case.recovery_status = new_status

    return case