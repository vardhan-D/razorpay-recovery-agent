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
  
  
  function Dashboard() {
    const [cases, setCases] = useState([])
    const [metrics, setMetrics] = useState(null)
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
  
  
    useEffect(() => {
      async function loadDashboard() {
        try {
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
  
        } catch (err) {
          setError(err.message)
  
        } finally {
          setLoading(false)
        }
      }
  
      loadDashboard()
    }, [])
  
  
    if (loading) {
      return (
        <div className="page-state">
          Loading RecoveryOS...
        </div>
      )
    }
  
  
    if (error) {
      return (
        <div className="page-state error-state">
          {error}
        </div>
      )
    }
  
  
    return (
      <div className="dashboard">
  
        <header className="dashboard-header">
  
          <div>
            <div className="brand-row">
              <h1>RecoveryOS</h1>
  
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
  
          <div className="environment-badge">
            Razorpay Test Mode
          </div>
  
        </header>
  
  
        <section className="metrics-grid">
  
          <MetricCard
            label="Revenue at Risk"
            value={
              formatCurrency(
                metrics?.revenue_at_risk
              )
            }
            helper={
              `${metrics?.total_cases || 0} cases`
            }
          />
  
          <MetricCard
            label="Recovered Revenue"
            value={
              formatCurrency(
                metrics?.recovered_revenue
              )
            }
            helper={
              `${metrics?.recovered_cases || 0} recovered cases`
            }
          />
  
          <MetricCard
            label="Recovery Rate"
            value={
              `${metrics?.recovery_rate_percent || 0}%`
            }
            helper="Share of revenue recovered"
          />
  
          <MetricCard
            label="Active Cases"
            value={
              metrics?.active_cases || 0
            }
            helper={
              `${metrics?.escalated_cases || 0} escalated`
            }
          />
  
        </section>
  
  
        <section className="cases-section">
  
          <div className="section-heading">
  
            <div>
              <h2>
                Recovery Cases
              </h2>
  
              <p>
                AI diagnosis, recovery decisions,
                and current case state
              </p>
            </div>
  
          </div>
  
  
          {cases.length === 0 ? (
  
            <div className="empty-state">
              No recovery cases yet.
            </div>
  
          ) : (
  
            <div className="table-wrapper">
  
              <table className="recovery-table">
  
                <thead>
                  <tr>
                    <th>Payment</th>
                    <th>Amount</th>
                    <th>Method</th>
                    <th>Diagnosis</th>
                    <th>Action</th>
                    <th>Status</th>
                  </tr>
                </thead>
  
                <tbody>
  
                  {cases.map(
                    (recoveryCase) => {
  
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
                            key={recoveryCase.case_id}
                            className="clickable-row"
                            onClick={() =>
                                navigate(
                                `/cases/${recoveryCase.case_id}`
                                )
                            }
                            >
  
                          <td>
                            <div className="payment-cell">
                              {
                                recoveryCase
                                  .payment
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
  
                          <td className="amount-cell">
                            {
                              formatCurrency(
                                recoveryCase
                                  .payment
                                  .amount
                              )
                            }
                          </td>
  
                          <td>
                            {
                              recoveryCase
                                .payment
                                .payment_method
                                .replaceAll(
                                  "_",
                                  " "
                                )
                            }
                          </td>
  
                          <td>
                            <div className="diagnosis-cell">
                              {
                                recoveryCase
                                  .failure
                                  .category
                                  .replaceAll(
                                    "_",
                                    " "
                                  )
                              }
  
                              <span>
                                {
                                  recoveryCase
                                    .failure
                                    .failure_code
                                }
                              </span>
                            </div>
                          </td>
  
                          <td>
                            {
                              latestAction
                                .replaceAll(
                                  "_",
                                  " "
                                )
                            }
                          </td>
  
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
                  )}
  
                </tbody>
  
              </table>
  
            </div>
          )}
  
        </section>
  
      </div>
    )
  }
  
  
  export default Dashboard