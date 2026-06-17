import { useEffect, useMemo, useState } from "react"

import api, { endpoints, extractApiError } from "../services/api"

function Students() {
  const [students, setStudents] = useState([])
  const [departments, setDepartments] = useState([])
  const [form, setForm] = useState({ name: "", email: "", year: "", department: "" })
  const [csvFile, setCsvFile] = useState(null)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")

  const departmentOptions = useMemo(() => departments.map((department) => ({ value: department.id, label: department.name })), [departments])

  const loadData = async () => {
    try {
      const [studentRes, departmentRes] = await Promise.all([
        api.get(endpoints.students),
        api.get(endpoints.departments),
      ])
      setStudents(studentRes.data)
      setDepartments(departmentRes.data)
      setError("")
    } catch (err) {
      setError(extractApiError(err, "Unable to load students."))
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
      await api.post(endpoints.students, { ...form, year: Number(form.year), department: Number(form.department) })
      setForm({ name: "", email: "", year: "", department: "" })
      setMessage("Student created successfully.")
      loadData()
    } catch (err) {
      setError(extractApiError(err, "Unable to create student."))
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
      const { data } = await api.post(`${endpoints.students}upload/`, body)
      setCsvFile(null)
      setMessage(`${data.students_created || 0} student records uploaded.`)
      loadData()
    } catch (err) {
      setError(extractApiError(err, "Unable to upload student CSV."))
    }
  }

  return (
    <div className="stack-lg">
      <section className="two-column">
        <div className="panel">
          <div className="panel-header"><h3>Add Student</h3></div>
          <form className="form-grid" onSubmit={handleSubmit}>
            <label>Name<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></label>
            <label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></label>
            <label>Year<input type="number" min="1" max="4" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} required /></label>
            <label>Department<select value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} required><option value="">Select</option>{departmentOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
            {message ? <p className="helper-text">{message}</p> : null}
            {error ? <p className="error-text">{error}</p> : null}
            <button className="button" type="submit">Create Student</button>
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
        <div className="panel-header"><h3>Student Records</h3></div>
        <table className="data-table">
          <thead><tr><th>Name</th><th>Email</th><th>Year</th><th>Department</th><th>Login Password</th></tr></thead>
          <tbody>
            {students.map((student) => (
              <tr key={student.id}>
                <td>{student.name}</td>
                <td>{student.email}</td>
                <td>{student.year}</td>
                <td>{student.department_name}</td>
                <td>{student.generated_password || "default123"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default Students
