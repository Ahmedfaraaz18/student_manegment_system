import { useEffect, useState } from "react"

import api, { endpoints, extractApiError } from "../services/api"

const initialForm = {
  institution_name: "",
  institution_code: "",
  institution_type: "college",
  contact_email: "",
  phone: "",
  address: "",
  admin_name: "",
  admin_username: "",
  admin_email: "",
  password: "",
}

function TenantManagement() {
  const [tenants, setTenants] = useState([])
  const [form, setForm] = useState(initialForm)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")

  const loadTenants = async () => {
    try {
      const { data } = await api.get(endpoints.tenants)
      setTenants(data)
      setError("")
    } catch (err) {
      setError(extractApiError(err, "Unable to load tenants."))
    }
  }

  useEffect(() => {
    loadTenants()
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setMessage("")
    setError("")
    try {
      await api.post(endpoints.tenants, form)
      setForm(initialForm)
      setMessage("Tenant provisioned successfully.")
      loadTenants()
    } catch (err) {
      setError(extractApiError(err, "Unable to provision tenant."))
    }
  }

  const handleLifecycle = async (tenantId, action) => {
    setMessage("")
    setError("")
    try {
      await api.post(`${endpoints.tenants}${tenantId}/${action}/`)
      setMessage(`Tenant ${action.replace('_', ' ')} completed.`)
      loadTenants()
    } catch (err) {
      setError(extractApiError(err, `Unable to ${action} tenant.`))
    }
  }

  return (
    <div className="stack-lg">
      <section className="two-column">
        <div className="panel">
          <div className="panel-header"><h3>Provision Tenant</h3></div>
          <form className="form-grid" onSubmit={handleSubmit}>
            <label>Institution Name<input value={form.institution_name} onChange={(e) => setForm({ ...form, institution_name: e.target.value })} required /></label>
            <label>Institution Code<input value={form.institution_code} onChange={(e) => setForm({ ...form, institution_code: e.target.value })} required /></label>
            <label>
              Institution Type
              <select value={form.institution_type} onChange={(e) => setForm({ ...form, institution_type: e.target.value })}>
                <option value="college">College</option>
                <option value="school">School</option>
              </select>
            </label>
            <label>Contact Email<input type="email" value={form.contact_email} onChange={(e) => setForm({ ...form, contact_email: e.target.value })} /></label>
            <label>Phone<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
            <label>Address<input value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} /></label>
            <label>Admin Name<input value={form.admin_name} onChange={(e) => setForm({ ...form, admin_name: e.target.value })} required /></label>
            <label>Admin Username<input value={form.admin_username} onChange={(e) => setForm({ ...form, admin_username: e.target.value })} required /></label>
            <label>Admin Email<input type="email" value={form.admin_email} onChange={(e) => setForm({ ...form, admin_email: e.target.value })} required /></label>
            <label>Password<input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required /></label>
            {message ? <p className="helper-text">{message}</p> : null}
            {error ? <p className="error-text">{error}</p> : null}
            <button className="button" type="submit">Create Tenant</button>
          </form>
        </div>
        <div className="panel">
          <div className="panel-header"><h3>Tenant Lifecycle</h3></div>
          <table className="data-table">
            <thead><tr><th>Name</th><th>Type</th><th>Status</th><th>Plan</th><th>Actions</th></tr></thead>
            <tbody>
              {tenants.map((tenant) => (
                <tr key={tenant.id}>
                  <td>{tenant.name}</td>
                  <td>{tenant.institution_type}</td>
                  <td>{tenant.status}</td>
                  <td>{tenant.subscription?.plan_name || "-"}</td>
                  <td>
                    <div className="button-row">
                      <button className="button button-secondary" type="button" onClick={() => handleLifecycle(tenant.id, "suspend")}>Suspend</button>
                      <button className="button" type="button" onClick={() => handleLifecycle(tenant.id, "reactivate")}>Reactivate</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

export default TenantManagement
