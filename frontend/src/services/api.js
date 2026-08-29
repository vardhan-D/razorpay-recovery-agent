const API_BASE_URL = "http://127.0.0.1:8000"


export async function getRecoveryCases() {
  const response = await fetch(
    `${API_BASE_URL}/recovery-cases`
  )

  if (!response.ok) {
    throw new Error(
      "Failed to fetch recovery cases"
    )
  }

  return response.json()
}

export async function getDashboardMetrics() {
    const response = await fetch(
      `${API_BASE_URL}/dashboard/metrics`
    )
  
    if (!response.ok) {
      throw new Error(
        "Failed to fetch dashboard metrics"
      )
    }
  
    return response.json()
  }

  export async function getRecoveryCase(caseId) {
    const response = await fetch(
      `${API_BASE_URL}/recovery-cases/${caseId}`
    )
  
    if (!response.ok) {
      throw new Error(
        "Failed to fetch recovery case"
      )
    }
  
    return response.json()
  }

  export async function runRecoveryAgent(caseId) {
    const response = await fetch(
      `${API_BASE_URL}/recovery-cases/${caseId}/run-agent`,
      {
        method: "POST",
      }
    )
  
    if (!response.ok) {
      const errorText =
        await response.text()
  
      throw new Error(
        `Failed to run recovery agent: ${response.status} ${errorText}`
      )
    }
  
    return response.json()
  }

  export async function seedCuratedDemo() {
    const response = await fetch(
      `${API_BASE_URL}/demo/seed-curated`,
      {
        method: "POST",
      }
    )
  
    if (!response.ok) {
      throw new Error(
        "Failed to prepare demo data"
      )
    }
  
    return response.json()
  }