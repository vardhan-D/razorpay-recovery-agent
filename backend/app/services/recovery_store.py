from typing import List, Optional

from app.database import SessionLocal
from app.db_models import RecoveryCaseDB
from app.models.recovery import RecoveryCase


def save_recovery_case(
    case: RecoveryCase,
) -> RecoveryCase:

    db = SessionLocal()

    try:
        existing = (
            db.query(RecoveryCaseDB)
            .filter(
                RecoveryCaseDB.case_id
                == case.case_id
            )
            .first()
        )

        case_json = (
            case.model_dump_json()
        )

        if existing:
            existing.recovery_status = (
                case.recovery_status.value
            )

            existing.payment_id = (
                case.payment.payment_id
            )

            existing.subscription_id = (
                case.subscription.subscription_id
            )

            existing.customer_id = (
                case.payment.customer_id
            )

            existing.amount = str(
                case.payment.amount
            )

            existing.case_json = (
                case_json
            )

        else:
            db_case = RecoveryCaseDB(
                case_id=case.case_id,
                recovery_status=(
                    case.recovery_status.value
                ),
                payment_id=(
                    case.payment.payment_id
                ),
                subscription_id=(
                    case.subscription.subscription_id
                ),
                customer_id=(
                    case.payment.customer_id
                ),
                amount=str(
                    case.payment.amount
                ),
                case_json=case_json,
            )

            db.add(
                db_case
            )

        db.commit()

        return case

    finally:
        db.close()


def get_recovery_case(
    case_id: str,
) -> Optional[RecoveryCase]:

    db = SessionLocal()

    try:
        db_case = (
            db.query(RecoveryCaseDB)
            .filter(
                RecoveryCaseDB.case_id
                == case_id
            )
            .first()
        )

        if not db_case:
            return None

        return (
            RecoveryCase.model_validate_json(
                db_case.case_json
            )
        )

    finally:
        db.close()


def get_all_recovery_cases() -> List[
    RecoveryCase
]:

    db = SessionLocal()

    try:
        rows = (
            db.query(RecoveryCaseDB)
            .all()
        )

        return [
            RecoveryCase.model_validate_json(
                row.case_json
            )
            for row in rows
        ]

    finally:
        db.close()