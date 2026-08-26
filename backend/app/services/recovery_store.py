from typing import Dict, Optional

from app.models.recovery import RecoveryCase


RECOVERY_CASES: Dict[str, RecoveryCase] = {}


def save_recovery_case(
    case: RecoveryCase,
) -> RecoveryCase:
    RECOVERY_CASES[case.case_id] = case
    return case


def get_recovery_case(
    case_id: str,
) -> Optional[RecoveryCase]:
    return RECOVERY_CASES.get(case_id)


def get_all_recovery_cases():
    return list(
        RECOVERY_CASES.values()
    )