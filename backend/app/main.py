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
from app.init_db import init_db
from app.agents.agent_orchestrator import (
    run_full_ai_recovery_loop,
)
from app.agents.recovery_agent import (
    run_ai_recovery_step,
)
from app.recovery.ai_safety import (
    validate_ai_decision,
)
from app.agents.diagnosis_agent import (
    diagnose_case_with_ai,
)
from app.razorpay.mapper import (
    razorpay_event_to_recovery_case,
    extract_recovery_case_id_from_payment_link,
)
from app.services.recovery_service import (
    mark_case_recovered,
)
from app.recovery.live_orchestrator import (
    run_live_recovery_workflow,
)
from app.services.recovery_store import (
    save_recovery_case,
    get_recovery_case,
    get_all_recovery_cases,
)
from app.razorpay.payment_links import (
    create_recovery_payment_link,
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

init_db()

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

    if event_name in {
        "payment_link.paid",
    }:
        case_id = (
            extract_recovery_case_id_from_payment_link(
                parsed_event
            )
        )

        if not case_id:
            return {
                "received": True,
                "verified": True,
                "event": event_name,
                "processed": False,
                "reason": (
                    "No recovery case linked "
                    "to Payment Link."
                ),
            }

        case = get_recovery_case(
            case_id
        )

        if not case:
            return {
                "received": True,
                "verified": True,
                "event": event_name,
                "processed": False,
                "reason": (
                    "Recovery case not found."
                ),
            }

        mark_case_recovered(
            case
        )

        save_recovery_case(
            case
        )

        return {
            "received": True,
            "verified": True,
            "event": event_name,
            "processed": True,
            "recovery_case": case,
        }

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

    processed_case = run_live_recovery_workflow(
        recovery_case
    )

    save_recovery_case(
        processed_case
    )

    return {
        "received": True,
        "verified": True,
        "event": event_name,
        "processed": True,
        "recovery_case": processed_case,
    }

@app.get("/razorpay/test-payment-link")
def test_payment_link():

    payment = Payment(
        payment_id="pay_test_recovery_001",
        customer_id="cust_test_001",
        subscription_id="sub_test_001",
        amount=1499,
        status=PaymentStatus.failed,
        payment_method=PaymentMethod.upi_autopay,
        attempt_number=1,
    )

    subscription = Subscription(
        subscription_id="sub_test_001",
        customer_id="cust_test_001",
        plan_name="Premium Monthly",
        amount=1499,
        status=SubscriptionStatus.active,
        mandate_status=MandateStatus.inactive,
    )

    failure = FailureInfo(
        failure_code="MANDATE_INVALID",
        failure_message="Mandate is inactive",
        category=FailureCategory.mandate_issue,
        retryable=False,
    )

    case = RecoveryCase(
        case_id="test_payment_link_001",
        payment=payment,
        subscription=subscription,
        failure=failure,
    )

    result = create_recovery_payment_link(
        case
    )

    return {
        "created": True,
        "payment_link_id": result.get("id"),
        "short_url": result.get("short_url"),
        "status": result.get("status"),
        "amount": result.get("amount"),
    }

@app.get("/recovery-cases")
def list_recovery_cases():
    return {
        "count": len(
            get_all_recovery_cases()
        ),
        "cases": get_all_recovery_cases(),
    }

@app.get(
    "/recovery-cases/{case_id}"
)
def fetch_recovery_case(
    case_id: str,
):

    case = get_recovery_case(
        case_id
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Recovery case not found.",
        )

    return case

@app.get("/demo/ai-diagnosis")
def test_ai_diagnosis():

    payment = Payment(
        payment_id="pay_ai_001",
        customer_id="cust_ai_001",
        subscription_id="sub_ai_001",
        amount=1499,
        status=PaymentStatus.failed,
        payment_method=PaymentMethod.upi_autopay,
        attempt_number=1,
    )

    subscription = Subscription(
        subscription_id="sub_ai_001",
        customer_id="cust_ai_001",
        plan_name="Premium Monthly",
        amount=1499,
        status=SubscriptionStatus.active,
        mandate_status=MandateStatus.active,
    )

    failure = FailureInfo(
        failure_code="BAD_REQUEST_ERROR",
        failure_message=(
            "Issuer bank is temporarily unavailable"
        ),
        category=FailureCategory.bank_unavailable,
        retryable=True,
    )

    case = RecoveryCase(
        case_id="case_ai_001",
        payment=payment,
        subscription=subscription,
        failure=failure,
    )

    decision = diagnose_case_with_ai(
        case
    )

    return {
        "case": case,
        "ai_decision": decision,
    }

@app.get("/demo/ai-safe-decision")
def test_ai_safe_decision():

    payment = Payment(
        payment_id="pay_ai_safe_001",
        customer_id="cust_ai_safe_001",
        subscription_id="sub_ai_safe_001",
        amount=1499,
        status=PaymentStatus.failed,
        payment_method=PaymentMethod.upi_autopay,
        attempt_number=1,
    )

    subscription = Subscription(
        subscription_id="sub_ai_safe_001",
        customer_id="cust_ai_safe_001",
        plan_name="Premium Monthly",
        amount=1499,
        status=SubscriptionStatus.active,
        mandate_status=MandateStatus.active,
    )

    failure = FailureInfo(
        failure_code="BAD_REQUEST_ERROR",
        failure_message=(
            "Issuer bank is temporarily unavailable"
        ),
        category=FailureCategory.bank_unavailable,
        retryable=True,
    )

    case = RecoveryCase(
        case_id="case_ai_safe_001",
        payment=payment,
        subscription=subscription,
        failure=failure,
    )

    ai_decision = diagnose_case_with_ai(
        case
    )

    safety_result = validate_ai_decision(
        case,
        ai_decision,
    )

    return {
        "case": case,
        "ai_decision": ai_decision,
        "safety_validation": safety_result,
    }

@app.get("/demo/ai-tool-execution")
def test_ai_tool_execution():

    payment = Payment(
        payment_id="pay_agent_001",
        customer_id="cust_agent_001",
        subscription_id="sub_agent_001",
        amount=1499,
        status=PaymentStatus.failed,
        payment_method=PaymentMethod.upi_autopay,
        attempt_number=1,
    )

    subscription = Subscription(
        subscription_id="sub_agent_001",
        customer_id="cust_agent_001",
        plan_name="Premium Monthly",
        amount=1499,
        status=SubscriptionStatus.active,
        mandate_status=MandateStatus.active,
    )

    failure = FailureInfo(
        failure_code="BAD_REQUEST_ERROR",
        failure_message=(
            "Issuer bank is temporarily unavailable"
        ),
        category=FailureCategory.bank_unavailable,
        retryable=True,
    )

    case = RecoveryCase(
        case_id="case_agent_001",
        payment=payment,
        subscription=subscription,
        failure=failure,
    )

    processed_case = (
        run_ai_recovery_step(
            case
        )
    )

    return processed_case

@app.get("/demo/full-ai-agent")
def test_full_ai_agent():

    payment = Payment(
        payment_id="pay_full_agent_001",
        customer_id="cust_full_agent_001",
        subscription_id="sub_full_agent_001",
        amount=1499,
        status=PaymentStatus.failed,
        payment_method=PaymentMethod.upi_autopay,
        attempt_number=1,
    )

    subscription = Subscription(
        subscription_id="sub_full_agent_001",
        customer_id="cust_full_agent_001",
        plan_name="Premium Monthly",
        amount=1499,
        status=SubscriptionStatus.active,
        mandate_status=MandateStatus.active,
    )

    failure = FailureInfo(
        failure_code="BAD_REQUEST_ERROR",
        failure_message=(
            "Issuer bank is temporarily unavailable"
        ),
        category=FailureCategory.bank_unavailable,
        retryable=True,
    )

    case = RecoveryCase(
        case_id="case_full_agent_001",
        payment=payment,
        subscription=subscription,
        failure=failure,
    )

    processed_case = (
        run_full_ai_recovery_loop(
            case
        )
    )

    return processed_case

@app.get("/database/status")
def database_status():

    cases = get_all_recovery_cases()

    return {
        "connected": True,
        "database": "sqlite",
        "stored_recovery_cases": len(
            cases
        ),
    }