import { useEffect, useState } from "react"

import api, { endpoints } from "../services/api"

function Approvals() {
  const [requests, setRequests] = useState([])
  const [form, setForm] = useState({ request_type: "bonafide", title: "", description: "" })

  const loadData = async () => {
    const { data } = await api.get(endpoints.workflows)
    setRequests(data)
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    await api.post(endpoints.workflows, form)
    setForm({ request_type: "bonafide", title: "", description: "" })
    loadData()
  }

  const updateStatus = async (item, status) => {
    await api.patch(`${endpoints.workflows}${item.id}/`, { status })
    loadData()
  }

  return (
    <div className="stack-lg">
      <section className="two-column">
        <div className="panel">
          <div className="panel-header"><h3>Create Approval Request</h3></div>
          <form className="form-grid" onSubmit={handleSubmit}>
            <label>Type<select value={form.request_type} onChange={(e) => setForm({ ...form, request_type: e.target.value })}><option value="bonafide">Bonafide</option><option value="leave">Leave</option><option value="document">Document</option></select></label>
            <label>Title<input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></label>
            <label>Description<textarea rows="4" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
            <button className="button" type="submit">Submit Request</button>
          </form>
        </div>
        <div className="panel">
          <div className="panel-header"><h3>Approval Pipeline</h3></div>
          <p className="helper-text">Use this for bonafide letters, student leave, internal office approvals, and document issuance requests.</p>
        </div>
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Requests</h3></div>
        <table className="data-table">
          <thead><tr><th>Title</th><th>Type</th><th>Requested By</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            {requests.map((item) => (
              <tr key={item.id}>
                <td>{item.title}</td>
                <td>{item.request_type}</td>
                <td>{item.requested_by_name}</td>
                <td>{item.status}</td>
                <td className="table-actions">
                  <button className="button button-small" onClick={() => updateStatus(item, "approved")}>Approve</button>
                  <button className="button button-secondary button-small" onClick={() => updateStatus(item, "rejected")}>Reject</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default Approvals
