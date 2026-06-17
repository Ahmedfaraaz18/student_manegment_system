import { useEffect, useMemo, useState } from "react"

import api, { endpoints, extractApiError } from "../services/api"

function Teachers() {
  const [teachers, setTeachers] = useState([])
  const [departments, setDepartments] = useState([])
  const [form, setForm] = useState({ name: "", email: "", phone: "", department: "" })
  const [csvFile, setCsvFile] = useState(null)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")

  const departmentOptions = useMemo(() => departments.map((department) => ({ value: department.id, label: department.name })), [departments])

  const loadData = async () => {
    try {
      const [teacherRes, departmentRes] = await Promise.all([
        api.get(endpoints.teachers),
        api.get(endpoints.departments),
      ])
      setTeachers(teacherRes.data)
      setDepartments(departmentRes.data)
      setError("")
    } catch (err) {
      setError(extractApiError(err, "Unable to load teachers."))
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setMessage("")
    setError("")
    try {
      await api.post(endpoints.teachers, { ...form, department: Number(form.department) })
      setForm({ name: "", email: "", phone: "", department: "" })
      setMessage("Teacher created successfully.")
      loadData()
    } catch (err) {
      setError(extractApiError(err, "Unable to create teacher."))
    }
  }

  const handleUpload = async (event) => {
    event.preventDefault()
    if (!csvFile) return
    setMessage("")
    setError("")
    try {
      const body = new FormData()
      body.append("file", csvFile)
      const { data } = await api.post(`${endpoints.teachers}upload/`, body)
      setCsvFile(null)
      setMessage(`${data.teachers_created || 0} teacher records uploaded.`)
      loadData()
    } catch (err) {
      setError(extractApiError(err, "Unable to upload teacher CSV."))
    }
  }

  return (
    <div className="stack-lg">
      <section className="two-column">
        <div className="panel">
          <div className="panel-header"><h3>Add Teacher</h3></div>
          <form className="form-grid" onSubmit={handleSubmit}>
            <label>Name<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></label>
            <label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></label>
            <label>Phone<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
            <label>Department<select value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} required><option value="">Select</option>{departmentOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
            {message ? <p className="helper-text">{message}</p> : null}
            {error ? <p className="error-text">{error}</p> : null}
            <button className="button" type="submit">Create Teacher</button>
          </form>
        </div>
        <div className="panel">
          <div className="panel-header"><h3>Bulk Import</h3></div>
          <form className="form-grid" onSubmit={handleUpload}>
            <label>CSV File<input type="file" accept=".csv" onChange={(e) => setCsvFile(e.target.files?.[0] || null)} /></label>
            <button className="button button-secondary" type="submit">Upload CSV</button>
          </form>
        </div>
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Teacher Directory</h3></div>
        <table className="data-table">
          <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Department</th><th>Login Password</th></tr></thead>
          <tbody>
            {teachers.map((teacher) => (
              <tr key={teacher.id}>
                <td>{teacher.name}</td>
                <td>{teacher.email}</td>
                <td>{teacher.phone || "-"}</td>
                <td>{teacher.department_name}</td>
                <td>{teacher.generated_password || "default123"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default Teachers
