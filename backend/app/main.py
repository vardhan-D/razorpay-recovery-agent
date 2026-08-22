from fastapi import FastAPI

from app.services.simulation_service import generate_failure_batch,calculate_batch_summary
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.subscription import (
    Subscription,
    SubscriptionStatus,
    MandateStatus,
)
from app.models.failure import FailureInfo, FailureCategory
from app.models.recovery import RecoveryCase


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