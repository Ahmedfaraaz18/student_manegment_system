import { useEffect, useState } from "react"

import api, { endpoints, extractApiError } from "../services/api"

function Subjects() {
  const [subjects, setSubjects] = useState([])
  const [departments, setDepartments] = useState([])
  const [teachers, setTeachers] = useState([])
  const [form, setForm] = useState({ name: "", department: "", teacher: "" })
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")

  const loadData = async () => {
    try {
      const [subjectRes, departmentRes, teacherRes] = await Promise.all([
        api.get(endpoints.subjects),
        api.get(endpoints.departments),
        api.get(endpoints.teachers),
      ])
      setSubjects(subjectRes.data)
      setDepartments(departmentRes.data)
      setTeachers(teacherRes.data)
      setError("")
    } catch (err) {
      setError(extractApiError(err, "Unable to load subjects."))
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
      await api.post(endpoints.subjects, {
        ...form,
        department: Number(form.department),
        teacher: Number(form.teacher),
      })
      setForm({ name: "", department: "", teacher: "" })
      setMessage("Subject saved.")
      loadData()
    } catch (err) {
      setError(extractApiError(err, "Unable to save subject."))
    }
  }

  return (
    <div className="two-column">
      <section className="panel">
        <div className="panel-header"><h3>Create Subject</h3></div>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>Subject Name<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></label>
          <label>Department<select value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} required><option value="">Select</option>{departments.map((department) => <option key={department.id} value={department.id}>{department.name}</option>)}</select></label>
          <label>Teacher<select value={form.teacher} onChange={(e) => setForm({ ...form, teacher: e.target.value })} required><option value="">Select</option>{teachers.map((teacher) => <option key={teacher.id} value={teacher.id}>{teacher.name}</option>)}</select></label>
          {message ? <p className="helper-text">{message}</p> : null}
          {error ? <p className="error-text">{error}</p> : null}
          <button className="button" type="submit">Save Subject</button>
        </form>
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Subjects</h3></div>
        <table className="data-table">
          <thead><tr><th>Name</th><th>Department</th><th>Teacher</th></tr></thead>
          <tbody>
            {subjects.map((subject) => (
              <tr key={subject.id}><td>{subject.name}</td><td>{subject.department_name}</td><td>{subject.teacher_name}</td></tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default Subjects
