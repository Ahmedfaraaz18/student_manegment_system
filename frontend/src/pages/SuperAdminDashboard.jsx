import { useEffect, useState } from "react"

import StatsCard from "../components/StatsCard"
import api, { endpoints, extractApiError } from "../services/api"

function SuperAdminDashboard() {
  const [data, setData] = useState({
    total_tenants: 0,
    active_tenants: 0,
    suspended_tenants: 0,
    total_students: 0,
    total_teachers: 0,
    active_subscriptions: 0,
    tenant_breakdown: [],
  })
  const [error, setError] = useState("")

  useEffect(() => {
    api
      .get(endpoints.superAdminDashboard)
      .then((response) => {
        setData(response.data)
        setError("")
      })
      .catch((err) => setError(extractApiError(err, "Unable to load super admin metrics.")))
  }, [])

  return (
    <div className="stack-lg">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Multi-Tenant SaaS Control</p>
          <h2>Global tenant operations, subscription oversight, and usage visibility</h2>
          <p className="helper-text">Provision, suspend, and monitor every institution from a single control plane.</p>
        </div>
      </section>
      {error ? <p className="error-text">{error}</p> : null}
      <section className="stats-grid">
        <StatsCard label="Total Tenants" value={data.total_tenants} accent="warm" />
        <StatsCard label="Active Tenants" value={data.active_tenants} accent="cool" />
        <StatsCard label="Suspended Tenants" value={data.suspended_tenants} accent="accent" />
        <StatsCard label="Active Subscriptions" value={data.active_subscriptions} accent="default" />
      </section>
      <section className="stats-grid">
        <StatsCard label="Students Across Tenants" value={data.total_students} accent="warm" />
        <StatsCard label="Teachers Across Tenants" value={data.total_teachers} accent="cool" />
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Tenant Breakdown</h3></div>
        <table className="data-table">
          <thead><tr><th>Institution</th><th>Type</th><th>Code</th><th>Status</th><th>Students</th><th>Teachers</th></tr></thead>
          <tbody>
            {data.tenant_breakdown.map((tenant) => (
              <tr key={tenant.id}>
                <td>{tenant.name}</td>
                <td>{tenant.institution_type}</td>
                <td>{tenant.code}</td>
                <td>{tenant.status}</td>
                <td>{tenant.student_count}</td>
                <td>{tenant.teacher_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default SuperAdminDashboard
