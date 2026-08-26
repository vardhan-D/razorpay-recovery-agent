import json

import requests

from app.models.ai_decision import AIDecision
from app.models.recovery import RecoveryCase


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


SYSTEM_PROMPT = """
You are a payment recovery decision agent.

You analyze failed recurring-payment cases.

Your job is to:
1. identify the most likely failure category,
2. estimate confidence,
3. recommend the safest next recovery action.

Allowed diagnosis values:
- insufficient_funds
- bank_unavailable
- mandate_issue
- authentication_issue
- technical_error
- unknown

Allowed actions:
- retry
- send_reminder
- create_payment_link
- promise_to_pay
- escalate
- stop

Rules:
- Never assume missing financial facts.
- If evidence is insufficient, use unknown and prefer escalate.
- Never recommend endless retries.
- Do not recommend retry if a mandate is expired, revoked, or inactive.
- If the case is already recovered, recommend stop.
- Return valid JSON only.

Required JSON structure:

{
  "diagnosis": "bank_unavailable",
  "confidence": 0.85,
  "recommended_action": "retry",
  "retry_after_minutes": 180,
  "reasoning_summary": "Short explanation"
}
"""


def build_case_context(
    case: RecoveryCase,
) -> dict:

    return {
        "case_id": case.case_id,

        "payment": {
            "amount": case.payment.amount,
            "currency": case.payment.currency,
            "status": case.payment.status.value,
            "payment_method": (
                case.payment.payment_method.value
            ),
            "attempt_number": (
                case.payment.attempt_number
            ),
        },

        "subscription": {
            "status": (
                case.subscription.status.value
            ),
            "mandate_status": (
                case.subscription.mandate_status.value
            ),
        },

        "failure": {
            "failure_code": (
                case.failure.failure_code
            ),
            "failure_message": (
                case.failure.failure_message
            ),
            "existing_category": (
                case.failure.category.value
            ),
            "retryable": (
                case.failure.retryable
            ),
        },

        "recovery": {
            "recovery_status": (
                case.recovery_status.value
            ),
            "recovery_attempts": (
                case.recovery_attempts
            ),
            "previous_actions": [
                action.action_type.value
                for action in case.action_history
            ],
        },
    }


def diagnose_case_with_ai(
    case: RecoveryCase,
) -> AIDecision:

    context = build_case_context(
        case
    )

    prompt = f"""
{SYSTEM_PROMPT}

Recovery case:

{json.dumps(context, indent=2)}

Return JSON only.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )

    response.raise_for_status()

    result = response.json()

    raw_output = result.get(
        "response",
        ""
    )

    decision_data = json.loads(
        raw_output
    )

    decision = AIDecision(
        **decision_data
    )

    return decision