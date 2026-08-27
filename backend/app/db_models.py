from sqlalchemy import Column, String, Text

from sqlalchemy.orm import declarative_base


Base = declarative_base()


class RecoveryCaseDB(Base):

    __tablename__ = "recovery_cases"

    case_id = Column(
        String,
        primary_key=True,
        index=True,
    )

    recovery_status = Column(
        String,
        nullable=False,
    )

    payment_id = Column(
        String,
        nullable=False,
    )

    subscription_id = Column(
        String,
        nullable=False,
    )

    customer_id = Column(
        String,
        nullable=False,
    )

    amount = Column(
        String,
        nullable=False,
    )

    case_json = Column(
        Text,
        nullable=False,
    )