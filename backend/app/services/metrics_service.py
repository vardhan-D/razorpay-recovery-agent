from app.models.recovery import RecoveryStatus


def calculate_recovery_metrics(cases):
    total_revenue_at_risk = sum(
        case.payment.amount
        for case in cases
    )

    recovered_revenue = sum(
        case.amount_recovered
        for case in cases
    )

    recovered_cases = sum(
        1
        for case in cases
        if case.recovery_status == RecoveryStatus.recovered
    )

    escalated_cases = sum(
        1
        for case in cases
        if case.recovery_status == RecoveryStatus.escalated
    )

    unresolved_cases = sum(
        1
        for case in cases
        if case.recovery_status not in {
            RecoveryStatus.recovered,
            RecoveryStatus.escalated,
            RecoveryStatus.stopped,
        }
    )

    total_cases = len(cases)

    recovery_rate = (
        recovered_cases / total_cases * 100
        if total_cases
        else 0
    )

    revenue_recovery_rate = (
        recovered_revenue / total_revenue_at_risk * 100
        if total_revenue_at_risk
        else 0
    )

    unrecovered_revenue = (
        total_revenue_at_risk - recovered_revenue
    )

    return {
        "total_cases": total_cases,
        "revenue_at_risk": total_revenue_at_risk,
        "recovered_revenue": recovered_revenue,
        "unrecovered_revenue": unrecovered_revenue,
        "recovered_cases": recovered_cases,
        "escalated_cases": escalated_cases,
        "unresolved_cases": unresolved_cases,
        "case_recovery_rate_percent": round(
            recovery_rate,
            2,
        ),
        "revenue_recovery_rate_percent": round(
            revenue_recovery_rate,
            2,
        ),
    }