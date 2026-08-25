from uuid import uuid4

from app.models.failure import (
    FailureCategory,
    FailureInfo,
)
from app.models.payment import (
    Payment,
    PaymentMethod,
    PaymentStatus,
)
from app.models.audit import AuditEventType
from app.services.audit_service import add_audit_event
from app.models.recovery import RecoveryCase
from app.models.subscription import (
    MandateStatus,
    Subscription,
    SubscriptionStatus,
)


def classify_razorpay_failure(
    payment_entity: dict,
) -> FailureInfo:
    """
    Convert Razorpay failure information into our
    internal failure model.
    """

    error_code = (
        payment_entity.get("error_code")
        or "UNKNOWN_FAILURE"
    )

    error_description = (
        payment_entity.get("error_description")
        or "Failure reason unavailable"
    )

    text = (
        f"{error_code} {error_description}"
    ).lower()

    if (
        "insufficient" in text
        or "balance" in text
    ):
        category = FailureCategory.insufficient_funds
        retryable = True

    elif (
        "bank" in text
        or "issuer" in text
        or "temporarily unavailable" in text
    ):
        category = FailureCategory.bank_unavailable
        retryable = True

    elif (
        "mandate" in text
        or "token" in text
        or "expired" in text
        or "revoked" in text
    ):
        category = FailureCategory.mandate_issue
        retryable = False

    elif (
        "authentication" in text
        or "authenticate" in text
        or "otp" in text
    ):
        category = FailureCategory.authentication_issue
        retryable = False

    elif (
        "technical" in text
        or "server" in text
        or "processing" in text
    ):
        category = FailureCategory.technical_error
        retryable = True

    else:
        category = FailureCategory.unknown
        retryable = False

    return FailureInfo(
        failure_code=error_code,
        failure_message=error_description,
        category=category,
        retryable=retryable,
    )


def map_payment_method(
    payment_entity: dict,
) -> PaymentMethod:

    method = (
        payment_entity.get("method")
        or ""
    ).lower()

    if method == "upi":
        return PaymentMethod.upi_autopay

    if method == "card":
        return PaymentMethod.card_mandate

    return PaymentMethod.other


def map_subscription_status(
    razorpay_status: str,
) -> SubscriptionStatus:

    status = (
        razorpay_status
        or ""
    ).lower()

    if status == "active":
        return SubscriptionStatus.active

    if status == "cancelled":
        return SubscriptionStatus.cancelled

    if status == "completed":
        return SubscriptionStatus.completed

    if status == "expired":
        return SubscriptionStatus.expired

    if status in {
        "paused",
        "pending",
        "halted",
    }:
        return SubscriptionStatus.paused

    return SubscriptionStatus.active


def infer_mandate_status(
    subscription_entity: dict,
    failure: FailureInfo,
) -> MandateStatus:

    if failure.category == FailureCategory.mandate_issue:
        return MandateStatus.inactive

    return MandateStatus.active


def razorpay_event_to_recovery_case(
    parsed_event: dict,
) -> RecoveryCase:

    payload = parsed_event["payload"]

    subscription_entity = (
        payload.get("payload", {})
        .get("subscription", {})
        .get("entity", {})
    )

    payment_entity = (
        payload.get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    subscription_id = (
        subscription_entity.get("id")
        or "unknown_subscription"
    )

    customer_id = (
        subscription_entity.get("customer_id")
        or payment_entity.get("customer_id")
        or "unknown_customer"
    )

    payment_id = (
        payment_entity.get("id")
        or "unknown_payment"
    )

    amount_paise = (
        payment_entity.get("amount")
        or 0
    )

    amount_rupees = int(
        amount_paise / 100
    )

    failure = classify_razorpay_failure(
        payment_entity
    )

    payment = Payment(
        payment_id=payment_id,
        customer_id=customer_id,
        subscription_id=subscription_id,
        amount=amount_rupees,
        currency=payment_entity.get(
            "currency",
            "INR",
        ),
        status=PaymentStatus.failed,
        payment_method=map_payment_method(
            payment_entity
        ),
        attempt_number=1,
    )

    subscription = Subscription(
        subscription_id=subscription_id,
        customer_id=customer_id,
        plan_name=subscription_entity.get(
            "plan_id",
            "Unknown Plan",
        ),
        amount=amount_rupees,
        currency=payment.currency,
        status=map_subscription_status(
            subscription_entity.get(
                "status",
                "active",
            )
        ),
        mandate_status=infer_mandate_status(
            subscription_entity,
            failure,
        ),
    )

    case = RecoveryCase(
        case_id=f"rzp_case_{uuid4().hex[:8]}",
        payment=payment,
        subscription=subscription,
        failure=failure,
    )

    add_audit_event(
        case,
        AuditEventType.payment_failed,
        f"Razorpay payment {payment.payment_id} failed for ₹{payment.amount}.",
        {
            "source": "razorpay_webhook",
            "payment_id": payment.payment_id,
        },
    )

    add_audit_event(
        case,
        AuditEventType.case_created,
        f"Recovery case {case.case_id} created from Razorpay webhook.",
    )

    add_audit_event(
        case,
        AuditEventType.failure_classified,
        f"Failure classified as {failure.category.value}.",
        {
            "failure_code": failure.failure_code,
            "category": failure.category.value,
        },
    )

    return case