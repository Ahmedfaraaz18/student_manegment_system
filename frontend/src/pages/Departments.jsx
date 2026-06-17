import { useEffect, useState } from "react"

import api, { endpoints, extractApiError } from "../services/api"

function Departments() {
  const [departments, setDepartments] = useState([])
  const [name, setName] = useState("")
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")

  const loadDepartments = async () => {
    try {
      const { data } = await api.get(endpoints.departments)
      setDepartments(data)
      setError("")
    } catch (err) {
      setError(extractApiError(err, "Unable to load departments."))
    }
  }

  useEffect(() => {
    loadDepartments()
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setMessage("")
    setError("")
    try {
      await api.post(endpoints.departments, { name })
      setName("")
      setMessage("Department saved.")
      loadDepartments()
    } catch (err) {
      setError(extractApiError(err, "Unable to save department."))
    }
  }

  return (
    <div className="two-column">
      <section className="panel">
        <div className="panel-header"><h3>Create Department</h3></div>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Name
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          {message ? <p className="helper-text">{message}</p> : null}
          {error ? <p className="error-text">{error}</p> : null}
          <button className="button" type="submit">Save Department</button>
        </form>
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Department List</h3></div>
        <table className="data-table">
          <thead><tr><th>Name</th></tr></thead>
          <tbody>
            {departments.map((department) => (
              <tr key={department.id}><td>{department.name}</td></tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default Departments
