from enum import Enum

from pydantic import BaseModel, Field


class AIDiagnosisCategory(str, Enum):
    insufficient_funds = "insufficient_funds"
    bank_unavailable = "bank_unavailable"
    mandate_issue = "mandate_issue"
    authentication_issue = "authentication_issue"
    technical_error = "technical_error"
    unknown = "unknown"


class AIRecommendedAction(str, Enum):
    retry = "retry"
    send_reminder = "send_reminder"
    create_payment_link = "create_payment_link"
    promise_to_pay = "promise_to_pay"
    escalate = "escalate"
    stop = "stop"


class AIDecision(BaseModel):
    diagnosis: AIDiagnosisCategory

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    recommended_action: AIRecommendedAction

    retry_after_minutes: int | None = None

    reasoning_summary: str

class SafetyValidationResult(BaseModel):
    approved: bool

    original_action: AIRecommendedAction

    final_action: AIRecommendedAction

    reason: str