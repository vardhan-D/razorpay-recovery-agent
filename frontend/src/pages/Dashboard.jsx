import {
    useEffect,
    useState,
  } from "react"
  
  import {
    useNavigate,
  } from "react-router-dom"
  
  import {
    getDashboardMetrics,
    getRecoveryCases,
    seedCuratedDemo,
  } from "../services/api"
  
  import MetricCard from "../components/MetricCard"
  import StatusBadge from "../components/StatusBadge"
  
  import "./Dashboard.css"
  
  
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
  
  
  function prettyText(value) {
    if (!value) {
      return "—"
    }
  
    return value.replaceAll("_", " ")
  }
  
  
  function Dashboard() {
    const navigate = useNavigate()
  
    const [cases, setCases] = useState([])
    const [metrics, setMetrics] = useState(null)
  
    const [loading, setLoading] = useState(true)
    const [preparingDemo, setPreparingDemo] =
      useState(false)
  
    const [error, setError] = useState(null)
  
  
    async function loadDashboardData() {
      const [
        casesData,
        metricsData,
      ] = await Promise.all([
        getRecoveryCases(),
        getDashboardMetrics(),
      ])
  
      setCases(
        casesData.cases || []
      )
  
      setMetrics(
        metricsData
      )
    }
  
  
    useEffect(() => {
      async function loadDashboard() {
        try {
          setError(null)
  
          await loadDashboardData()
  
        } catch (err) {
          console.error(
            "Dashboard load error:",
            err
          )
  
          setError(err.message)
  
        } finally {
          setLoading(false)
        }
      }
  
      loadDashboard()
    }, [])
  
  
    async function handlePrepareDemo() {
      try {
        setPreparingDemo(true)
        setError(null)
  
        await seedCuratedDemo()
  
        await loadDashboardData()
  
      } catch (err) {
        console.error(
          "Prepare demo error:",
          err
        )
  
        setError(err.message)
  
      } finally {
        setPreparingDemo(false)
      }
    }
  
  
    if (loading) {
      return (
        <div className="page-state">
          Loading RecoveryOS...
        </div>
      )
    }
  
  
    if (
      error
      && cases.length === 0
    ) {
      return (
        <div className="page-state error-state">
          {error}
        </div>
      )
    }
  
  
    return (
      <div className="dashboard">
  
        {/* -------------------------------- */}
        {/* HEADER */}
        {/* -------------------------------- */}
  
        <header className="dashboard-header">
  
          <div>
  
            <div className="brand-row">
  
              <h1>
                RecoveryOS
              </h1>
  
              <span className="agent-indicator">
  
                <span className="agent-dot" />
  
                Agent Online
  
              </span>
  
            </div>
  
  
            <p>
              Autonomous recurring payment
              recovery powered by Llama 3.2
            </p>
  
          </div>
  
  
          <div className="header-actions">
  
            <button
              className="demo-button"
              onClick={
                handlePrepareDemo
              }
              disabled={
                preparingDemo
              }
            >
  
              {
                preparingDemo
                  ? "Preparing..."
                  : "Prepare Demo"
              }
  
            </button>
  
  
            <div className="environment-badge">
              Razorpay Test Mode
            </div>
  
          </div>
  
        </header>
  
  
        {/* -------------------------------- */}
        {/* ERROR BANNER */}
        {/* -------------------------------- */}
  
        {
          error
          && (
            <div className="dashboard-error">
              {error}
            </div>
          )
        }
  
  
        {/* -------------------------------- */}
        {/* METRICS */}
        {/* -------------------------------- */}
  
        <section className="metrics-grid">
  
          <MetricCard
            label="Revenue at Risk"
            value={
              formatCurrency(
                metrics
                  ?.revenue_at_risk
              )
            }
            helper={
              `${
                metrics
                  ?.total_cases
                || 0
              } cases`
            }
          />
  
  
          <MetricCard
            label="Recovered Revenue"
            value={
              formatCurrency(
                metrics
                  ?.recovered_revenue
              )
            }
            helper={
              `${
                metrics
                  ?.recovered_cases
                || 0
              } recovered cases`
            }
          />
  
  
          <MetricCard
            label="Recovery Rate"
            value={
              `${
                metrics
                  ?.recovery_rate_percent
                || 0
              }%`
            }
            helper={
              "Share of revenue recovered"
            }
          />
  
  
          <MetricCard
            label="Active Cases"
            value={
              metrics
                ?.active_cases
              || 0
            }
            helper={
              `${
                metrics
                  ?.escalated_cases
                || 0
              } escalated`
            }
          />
  
        </section>
  
  
        {/* -------------------------------- */}
        {/* HOW IT WORKS */}
        {/* -------------------------------- */}
  
        <section className="workflow-strip">
  
          <div>
  
            <span>
              1
            </span>
  
            <strong>
              Detect failure
            </strong>
  
            <p>
              Razorpay webhook creates
              a recovery case.
            </p>
  
          </div>
  
  
          <div>
  
            <span>
              2
            </span>
  
            <strong>
              AI diagnoses
            </strong>
  
            <p>
              Llama 3.2 recommends
              the next recovery action.
            </p>
  
          </div>
  
  
          <div>
  
            <span>
              3
            </span>
  
            <strong>
              Safety validates
            </strong>
  
            <p>
              Deterministic rules approve
              or override the AI.
            </p>
  
          </div>
  
  
          <div>
  
            <span>
              4
            </span>
  
            <strong>
              Razorpay executes
            </strong>
  
            <p>
              Recovery tools execute
              the approved action.
            </p>
  
          </div>
  
        </section>
  
  
        {/* -------------------------------- */}
        {/* RECOVERY CASES */}
        {/* -------------------------------- */}
  
        <section className="cases-section">
  
          <div className="section-heading">
  
            <div>
  
              <h2>
                Recovery Cases
              </h2>
  
              <p>
                AI diagnosis, recovery
                decisions, and current
                case state
              </p>
  
            </div>
  
  
            <span className="case-count">
              {cases.length} cases
            </span>
  
          </div>
  
  
          {
            cases.length === 0
            ? (
  
              <div className="empty-state">
  
                <strong>
                  No recovery cases yet.
                </strong>
  
                <p>
                  Click Prepare Demo
                  to create curated
                  recovery scenarios.
                </p>
  
              </div>
  
            )
            : (
  
              <div className="table-wrapper">
  
                <table className="recovery-table">
  
                  <thead>
  
                    <tr>
  
                      <th>
                        Payment
                      </th>
  
                      <th>
                        Amount
                      </th>
  
                      <th>
                        Method
                      </th>
  
                      <th>
                        Diagnosis
                      </th>
  
                      <th>
                        Action
                      </th>
  
                      <th>
                        Status
                      </th>
  
                    </tr>
  
                  </thead>
  
  
                  <tbody>
  
                    {
                      cases.map(
                        (
                          recoveryCase
                        ) => {
  
                          const payment =
                            recoveryCase
                              .payment
  
                          const failure =
                            recoveryCase
                              .failure
  
  
                          const latestAction =
                            recoveryCase
                              .selected_action
                              ?.action_type
                            ||
                            recoveryCase
                              .action_history
                              ?.at(-1)
                              ?.action_type
                            ||
                            "—"
  
  
                          return (
  
                            <tr
                              key={
                                recoveryCase
                                  .case_id
                              }
                              className="clickable-row"
                              onClick={
                                () =>
                                  navigate(
                                    `/cases/${
                                      recoveryCase
                                        .case_id
                                    }`
                                  )
                              }
                            >
  
                              {/* PAYMENT */}
  
                              <td>
  
                                <div className="payment-cell">
  
                                  {
                                    payment
                                      .payment_id
                                  }
  
                                  <span>
                                    {
                                      recoveryCase
                                        .case_id
                                    }
                                  </span>
  
                                </div>
  
                              </td>
  
  
                              {/* AMOUNT */}
  
                              <td className="amount-cell">
  
                                {
                                  formatCurrency(
                                    payment
                                      .amount
                                  )
                                }
  
                              </td>
  
  
                              {/* PAYMENT METHOD */}
  
                              <td>
  
                                <span className="capitalize-text">
  
                                  {
                                    prettyText(
                                      payment
                                        .payment_method
                                    )
                                  }
  
                                </span>
  
                              </td>
  
  
                              {/* FAILURE */}
  
                              <td>
  
                                <div className="diagnosis-cell">
  
                                  {
                                    prettyText(
                                      failure
                                        .category
                                    )
                                  }
  
                                  <span>
                                    {
                                      failure
                                        .failure_code
                                    }
                                  </span>
  
                                </div>
  
                              </td>
  
  
                              {/* ACTION */}
  
                              <td>
  
                                <span className="capitalize-text">
  
                                  {
                                    prettyText(
                                      latestAction
                                    )
                                  }
  
                                </span>
  
                              </td>
  
  
                              {/* STATUS */}
  
                              <td>
  
                                <StatusBadge
                                  status={
                                    recoveryCase
                                      .recovery_status
                                  }
                                />
  
                              </td>
  
                            </tr>
  
                          )
                        }
                      )
                    }
  
                  </tbody>
  
                </table>
  
              </div>
  
            )
          }
  
        </section>
  
      </div>
    )
  }
  
  
  export default Dashboard