import random

from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.subscription import (
    Subscription,
    SubscriptionStatus,
    MandateStatus,
)
from app.models.failure import FailureInfo, FailureCategory
from app.models.recovery import RecoveryCase


FAILURE_SCENARIOS = [
    {
        "category": FailureCategory.insufficient_funds,
        "code": "INSUFFICIENT_FUNDS",
        "message": "Customer account does not have sufficient balance",
        "retryable": True,
        "weight": 35,
    },
    {
        "category": FailureCategory.bank_unavailable,
        "code": "BANK_TEMPORARILY_UNAVAILABLE",
        "message": "Issuer bank is temporarily unavailable",
        "retryable": True,
        "weight": 25,
    },
    {
        "category": FailureCategory.mandate_issue,
        "code": "MANDATE_INVALID",
        "message": "Mandate is expired, revoked, or inactive",
        "retryable": False,
        "weight": 15,
    },
    {
        "category": FailureCategory.authentication_issue,
        "code": "AUTHENTICATION_REQUIRED",
        "message": "Customer authentication is required",
        "retryable": False,
        "weight": 10,
    },
    {
        "category": FailureCategory.technical_error,
        "code": "TECHNICAL_ERROR",
        "message": "Temporary technical processing error",
        "retryable": True,
        "weight": 10,
    },
    {
        "category": FailureCategory.unknown,
        "code": "UNKNOWN_FAILURE",
        "message": "Failure reason could not be confidently identified",
        "retryable": False,
        "weight": 5,
    },
]


PLAN_OPTIONS = [
    ("Basic Monthly", 499),
    ("Standard Monthly", 999),
    ("Premium Monthly", 1499),
    ("Business Monthly", 2499),
    ("Enterprise Monthly", 4999),
]


def choose_failure_scenario():
    scenarios = FAILURE_SCENARIOS

    weights = [
        scenario["weight"]
        for scenario in scenarios
    ]

    return random.choices(
        scenarios,
        weights=weights,
        k=1,
    )[0]


def get_mandate_status(category: FailureCategory):
    if category == FailureCategory.mandate_issue:
        return random.choice([
            MandateStatus.expired,
            MandateStatus.revoked,
            MandateStatus.inactive,
        ])

    return MandateStatus.active


def generate_recovery_case(index: int) -> RecoveryCase:
    customer_id = f"cust_{index:04d}"
    subscription_id = f"sub_{index:04d}"
    payment_id = f"pay_{index:04d}"
    case_id = f"case_{index:04d}"

    plan_name, amount = random.choice(PLAN_OPTIONS)

    failure_scenario = choose_failure_scenario()

    payment_method = random.choice([
        PaymentMethod.upi_autopay,
        PaymentMethod.card_mandate,
    ])

    payment = Payment(
        payment_id=payment_id,
        customer_id=customer_id,
        subscription_id=subscription_id,
        amount=amount,
        status=PaymentStatus.failed,
        payment_method=payment_method,
        attempt_number=random.randint(1, 3),
    )

    subscription = Subscription(
        subscription_id=subscription_id,
        customer_id=customer_id,
        plan_name=plan_name,
        amount=amount,
        status=SubscriptionStatus.active,
        mandate_status=get_mandate_status(
            failure_scenario["category"]
        ),
    )

    failure = FailureInfo(
        failure_code=failure_scenario["code"],
        failure_message=failure_scenario["message"],
        category=failure_scenario["category"],
        retryable=failure_scenario["retryable"],
    )

    return RecoveryCase(
        case_id=case_id,
        payment=payment,
        subscription=subscription,
        failure=failure,
    )


def generate_failure_batch(count: int = 20):
    return [
        generate_recovery_case(index)
        for index in range(1, count + 1)
    ]

def calculate_batch_summary(cases):
    total_revenue_at_risk = sum(
        case.payment.amount
        for case in cases
    )

    category_counts = {}

    for case in cases:
        category = case.failure.category.value

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    average_amount = (
        total_revenue_at_risk / len(cases)
        if cases
        else 0
    )

    return {
        "total_cases": len(cases),
        "revenue_at_risk": total_revenue_at_risk,
        "average_failed_payment": round(
            average_amount,
            2
        ),
        "failure_breakdown": category_counts,
    }