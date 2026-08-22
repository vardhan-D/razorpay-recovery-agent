from enum import Enum
from pydantic import BaseModel


class FailureCategory(str, Enum):
    insufficient_funds = "insufficient_funds"
    bank_unavailable = "bank_unavailable"
    mandate_issue = "mandate_issue"
    authentication_issue = "authentication_issue"
    technical_error = "technical_error"
    unknown = "unknown"


class FailureInfo(BaseModel):
    failure_code: str
    failure_message: str
    category: FailureCategory
    retryable: bool