import {
  useEffect,
  useState,
} from "react"

import {
  Link,
  useParams,
} from "react-router-dom"

import {
  getRecoveryCase,
  runRecoveryAgent,
} from "../services/api"

import StatusBadge from "../components/StatusBadge"

import "./RecoveryCaseDetail.css"


function formatCurrency(amount) {
  return new Intl.NumberFormat(
    "en-IN",
    {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }
  ).format(amount || 0)
}


function formatDate(timestamp) {
  if (!timestamp) {
    return "—"
  }

  return new Date(timestamp).toLocaleString(
    "en-IN"
  )
}


function prettyText(value) {
  if (!value) {
    return "—"
  }

  return value.replaceAll("_", " ")
}


function RecoveryCaseDetail() {
  const { caseId } = useParams()

  const [recoveryCase, setRecoveryCase] =
    useState(null)

  const [loading, setLoading] =
    useState(true)

  const [runningAgent, setRunningAgent] =
    useState(false)

  const [error, setError] =
    useState(null)


  async function loadCase() {
    try {
      setError(null)

      const data =
        await getRecoveryCase(caseId)

      setRecoveryCase(data)

    } catch (err) {
      console.error(
        "Failed to load recovery case:",
        err
      )

      setError(err.message)

    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadCase()
  }, [caseId])


  async function handleRunAgent() {
    try {
      console.log(
        "Run Recovery Agent clicked:",
        caseId
      )

      setRunningAgent(true)
      setError(null)

      const result =
        await runRecoveryAgent(caseId)

      console.log(
        "Agent result:",
        result
      )

      if (!result?.case) {
        throw new Error(
          "Backend did not return an updated recovery case."
        )
      }

      setRecoveryCase(
        result.case
      )

    } catch (err) {
      console.error(
        "Agent error:",
        err
      )

      setError(err.message)

    } finally {
      setRunningAgent(false)
    }
  }


  if (loading) {
    return (
      <div className="detail-state">
        Loading recovery case...
      </div>
    )
  }


  if (
    error
    && !recoveryCase
  ) {
    return (
      <div className="detail-state error-state">
        {error}
      </div>
    )
  }


  if (!recoveryCase) {
    return (
      <div className="detail-state">
        Recovery case not found.
      </div>
    )
  }


  const payment =
    recoveryCase.payment

  const subscription =
    recoveryCase.subscription

  const failure =
    recoveryCase.failure

  const selectedAction =
    recoveryCase.selected_action


  const auditTrail =
    recoveryCase.audit_trail || []


  const latestAiEvent =
    [...auditTrail]
      .reverse()
      .find(
        (event) =>
          event.metadata?.source
          === "llama3.2"
      )


  const safetyEvent =
    [...auditTrail]
      .reverse()
      .find(
        (event) =>
          event.message
            ?.toLowerCase()
            .includes(
              "safety validation"
            )
      )


  return (
    <div className="case-detail">

      <div className="detail-topbar">

        <Link
          to="/"
          className="back-link"
        >
          ← Back to dashboard
        </Link>


        <div className="topbar-actions">

          <StatusBadge
            status={
              recoveryCase
                .recovery_status
            }
          />


          <button
            className="run-agent-button"
            onClick={handleRunAgent}
            disabled={runningAgent}
          >
            {
              runningAgent
                ? "Running Llama..."
                : "Run Recovery Agent"
            }
          </button>

        </div>

      </div>


      {
        error
        && (
          <div className="inline-error">
            {error}
          </div>
        )
      }


      <header className="case-header">

        <div>

          <div className="eyebrow">
            Recovery Case
          </div>

          <h1>
            {recoveryCase.case_id}
          </h1>

          <p>
            Payment {payment.payment_id}
          </p>

        </div>


        <div className="case-amount">

          <span>
            Amount at risk
          </span>

          <strong>
            {
              formatCurrency(
                payment.amount
              )
            }
          </strong>

        </div>

      </header>


      <div className="detail-grid">

        <section className="detail-card">

          <h2>
            Payment Context
          </h2>


          <div className="detail-list">

            <div>

              <span>
                Payment method
              </span>

              <strong>
                {
                  prettyText(
                    payment
                      .payment_method
                  )
                }
              </strong>

            </div>


            <div>

              <span>
                Subscription
              </span>

              <strong>
                {
                  subscription
                    .plan_name
                }
              </strong>

            </div>


            <div>

              <span>
                Mandate
              </span>

              <strong>
                {
                  prettyText(
                    subscription
                      .mandate_status
                  )
                }
              </strong>

            </div>


            <div>

              <span>
                Payment attempt
              </span>

              <strong>
                #{payment.attempt_number}
              </strong>

            </div>


            <div>

              <span>
                Customer
              </span>

              <strong>
                {payment.customer_id}
              </strong>

            </div>


            <div>

              <span>
                Subscription ID
              </span>

              <strong>
                {
                  payment
                    .subscription_id
                }
              </strong>

            </div>

          </div>

        </section>


        <section className="detail-card">

          <h2>
            Failure
          </h2>


          <div className="diagnosis-large">
            {
              prettyText(
                failure.category
              )
            }
          </div>


          <p className="failure-message">
            {failure.failure_message}
          </p>


          <div className="failure-code">
            {failure.failure_code}
          </div>


          <div className="retryable-row">

            <span>
              Retryable
            </span>

            <strong>
              {
                failure.retryable
                  ? "Yes"
                  : "No"
              }
            </strong>

          </div>

        </section>

      </div>


      <div className="detail-grid">

        <section className="detail-card">

          <div className="card-heading-row">

            <h2>
              AI Diagnosis
            </h2>

            <span className="llama-badge">
              Llama 3.2
            </span>

          </div>


          {
            latestAiEvent
              ? (
                <>

                  <div className="diagnosis-large">

                    {
                      prettyText(
                        latestAiEvent
                          .metadata
                          ?.diagnosis
                        ||
                        latestAiEvent
                          .message
                          ?.replace(
                            "AI diagnosis: ",
                            ""
                          )
                      )
                    }

                  </div>


                  <div className="confidence-row">

                    <span>
                      Confidence
                    </span>

                    <strong>
                      {
                        Math.round(
                          (
                            latestAiEvent
                              .metadata
                              ?.confidence
                            || 0
                          )
                          * 100
                        )
                      }%
                    </strong>

                  </div>


                  <div className="recommendation-row">

                    <span>
                      AI recommendation
                    </span>

                    <strong>
                      {
                        prettyText(
                          latestAiEvent
                            .metadata
                            ?.recommended_action
                        )
                      }
                    </strong>

                  </div>


                  <p className="ai-reason">
                    {
                      latestAiEvent
                        .metadata
                        ?.reasoning_summary
                    }
                  </p>

                </>
              )
              : (
                <p className="muted-text">
                  No AI diagnosis has been
                  recorded for this case yet.
                </p>
              )
          }

        </section>


        <section className="detail-card">

          <h2>
            Recovery Decision
          </h2>


          <div className="action-display">

            <span>
              Selected action
            </span>

            <strong>
              {
                prettyText(
                  selectedAction
                    ?.action_type
                )
              }
            </strong>

          </div>


          {
            selectedAction
              ?.scheduled_after_minutes
              && (
                <div className="schedule-box">

                  <span>
                    Retry after
                  </span>

                  <strong>
                    {
                      selectedAction
                        .scheduled_after_minutes
                    } minutes
                  </strong>

                </div>
              )
          }


          {
            selectedAction
              ?.reason
              && (
                <p className="decision-reason">
                  {
                    selectedAction
                      .reason
                  }
                </p>
              )
          }


          {
            safetyEvent
              && (
                <div
                  className={
                    safetyEvent
                      .metadata
                      ?.approved
                      ? "safety-box approved"
                      : "safety-box blocked"
                  }
                >

                  <span>
                    Safety validation
                  </span>

                  <strong>
                    {
                      safetyEvent
                        .metadata
                        ?.approved
                        ? "APPROVED"
                        : "OVERRIDDEN"
                    }
                  </strong>


                  <p>
                    {
                      safetyEvent
                        .metadata
                        ?.reason
                    }
                  </p>


                  {
                    safetyEvent
                      .metadata
                      ?.original_action
                      && (
                        <div className="safety-detail">

                          AI proposed:
                          {" "}
                          {
                            prettyText(
                              safetyEvent
                                .metadata
                                ?.original_action
                            )
                          }

                        </div>
                      )
                  }


                  {
                    safetyEvent
                      .metadata
                      ?.final_action
                      && (
                        <div className="safety-detail">

                          Final action:
                          {" "}
                          {
                            prettyText(
                              safetyEvent
                                .metadata
                                ?.final_action
                            )
                          }

                        </div>
                      )
                  }

                </div>
              )
          }

        </section>

      </div>


      {
        recoveryCase.payment_link_id
        && (
          <section className="payment-link-card">

            <div>

              <span>
                Razorpay Recovery Payment Link
              </span>

              <strong>
                {
                  recoveryCase
                    .payment_link_id
                }
              </strong>

            </div>


            {
              recoveryCase
                .payment_link_url
                && (
                  <a
                    href={
                      recoveryCase
                        .payment_link_url
                    }
                    target="_blank"
                    rel="noreferrer"
                  >
                    Open Payment Link
                  </a>
                )
            }

          </section>
        )
      }


      <section className="timeline-card">

        <div className="timeline-header">

          <div>

            <h2>
              Agent Timeline
            </h2>

            <p>
              Complete explainable recovery
              audit trail
            </p>

          </div>


          <span>
            {auditTrail.length} events
          </span>

        </div>


        {
          auditTrail.length === 0
            ? (
              <p className="muted-text">
                No audit events recorded yet.
              </p>
            )
            : (
              <div className="timeline">

                {
                  auditTrail.map(
                    (
                      event,
                      index
                    ) => (

                      <div
                        className="timeline-item"
                        key={
                          `${event.timestamp}-${index}`
                        }
                      >

                        <div className="timeline-marker">

                          <div className="timeline-dot" />

                          {
                            index
                            <
                            auditTrail.length - 1
                            && (
                              <div
                                className="timeline-line"
                              />
                            )
                          }

                        </div>


                        <div className="timeline-content">

                          <div className="timeline-event">

                            {
                              prettyText(
                                event.event_type
                              )
                            }

                          </div>


                          <div className="timeline-message">
                            {event.message}
                          </div>


                          <div className="timeline-time">

                            {
                              formatDate(
                                event.timestamp
                              )
                            }

                          </div>

                        </div>

                      </div>

                    )
                  )
                }

              </div>
            )
        }

      </section>

    </div>
  )
}


export default RecoveryCaseDetail