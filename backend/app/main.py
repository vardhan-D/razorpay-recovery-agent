from fastapi import FastAPI, Request, Header, HTTPException

from app.razorpay.webhooks import parse_razorpay_event,verify_webhook_signature
from app.recovery.executor import execute_recovery_batch
from app.services.metrics_service import calculate_recovery_metrics
from app.recovery.engine import decide_recovery_action,process_recovery_batch,calculate_decision_summary
from app.services.simulation_service import generate_failure_batch,calculate_batch_summary
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.subscription import (
    Subscription,
    SubscriptionStatus,
    MandateStatus,
)
from app.razorpay.mapper import (
    razorpay_event_to_recovery_case,
)
from app.models.failure import FailureInfo, FailureCategory
from app.models.recovery import RecoveryCase
from app.recovery.orchestrator import (
    
    run_recovery_workflow,
    run_recovery_workflow_batch,
)
from app.razorpay.client import get_razorpay_client


app = FastAPI(
    title="Razorpay Recovery Agent",
    description="Backend for recovering failed subscription and mandate payments.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Recovery Agent backend is running"
    }


@app.get("/demo/recovery-case")
def get_demo_recovery_case():

    payment = Payment(
        payment_id="pay_001",
        customer_id="cust_001",
        subscription_id="sub_001",
        amount=1499,
        status=PaymentStatus.failed,
        payment_method=PaymentMethod.upi_autopay,
        attempt_number=1,
    )

    subscription = Subscription(
        subscription_id="sub_001",
        customer_id="cust_001",
        plan_name="Premium Monthly Plan",
        amount=1499,
        status=SubscriptionStatus.active,
        mandate_status=MandateStatus.active,
    )

    failure = FailureInfo(
        failure_code="BANK_TEMPORARILY_UNAVAILABLE",
        failure_message="Issuer bank is temporarily unavailable",
        category=FailureCategory.bank_unavailable,
        retryable=True,
    )

    recovery_case = RecoveryCase(
        case_id="case_001",
        payment=payment,
        subscription=subscription,
        failure=failure,
    )

    return recovery_case

@app.get("/demo/simulate-failures")
def simulate_failures(count: int = 20):

    if count < 1:
        count = 1

    if count > 500:
        count = 500

    cases = generate_failure_batch(count)

    summary = calculate_batch_summary(cases)

    return {
        "summary": summary,
        "cases": cases,
    }

@app.get("/demo/recovery-batch")
def recovery_batch(count: int = 20):

    if count < 1:
        count = 1

    if count > 500:
        count = 500

    cases = generate_failure_batch(count)

    processed_cases = process_recovery_batch(cases)

    summary = calculate_decision_summary(
        processed_cases
    )

    return {
        "summary": summary,
        "cases": processed_cases,
    }

@app.get("/demo/run-recovery")
def run_recovery(count: int = 20):

    if count < 1:
        count = 1

    if count > 500:
        count = 500

    cases = generate_failure_batch(count)

    decided_cases = process_recovery_batch(cases)

    executed_cases = execute_recovery_batch(
        decided_cases
    )

    metrics = calculate_recovery_metrics(
        executed_cases
    )

    return {
        "metrics": metrics,
        "cases": executed_cases,
    }

@app.get("/demo/run-agentic-recovery")
def run_agentic_recovery(count: int = 20):

    if count < 1:
        count = 1

    if count > 500:
        count = 500

    cases = generate_failure_batch(count)

    processed_cases = run_recovery_workflow_batch(
        cases
    )

    metrics = calculate_recovery_metrics(
        processed_cases
    )

    return {
        "metrics": metrics,
        "cases": processed_cases,
    }

@app.get("/razorpay/test-connection")
def test_razorpay_connection():
    try:
        client = get_razorpay_client()

        payments = client.payment.all(
            {
                "count": 1
            }
        )

        return {
            "connected": True,
            "message": "Successfully connected to Razorpay Test Mode.",
            "payments_found": len(
                payments.get("items", [])
            ),
        }

    except Exception as exc:
        return {
            "connected": False,
            "error": str(exc),
        }

@app.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
):
    raw_body = await request.body()

    if not x_razorpay_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay signature.",
        )

    is_valid = verify_webhook_signature(
        raw_body,
        x_razorpay_signature,
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay webhook signature.",
        )

    parsed_event = parse_razorpay_event(
        raw_body
    )

    event_name = parsed_event["event"]

    supported_failure_events = {
        "subscription.pending",
        "subscription.halted",
    }

    if event_name not in supported_failure_events:
        return {
            "received": True,
            "verified": True,
            "event": event_name,
            "processed": False,
            "reason": "Event does not require recovery processing.",
        }

    recovery_case = (
        razorpay_event_to_recovery_case(
            parsed_event
        )
    )

    processed_case = run_recovery_workflow(
        recovery_case
    )

    return {
        "received": True,
        "verified": True,
        "event": event_name,
        "processed": True,
        "recovery_case": processed_case,
    }
