import { useEffect, useState } from "react"

import api, { endpoints } from "../services/api"

function Placements() {
  const [placements, setPlacements] = useState([])
  const [students, setStudents] = useState([])
  const [form, setForm] = useState({ student: "", company: "", package: "", year: "" })

  const loadData = async () => {
    const [placementRes, studentRes] = await Promise.all([api.get(endpoints.placements), api.get(endpoints.students)])
    setPlacements(placementRes.data)
    setStudents(studentRes.data)
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    await api.post(endpoints.placements, {
      ...form,
      student: Number(form.student),
      package: Number(form.package),
      year: Number(form.year),
    })
    setForm({ student: "", company: "", package: "", year: "" })
    loadData()
  }

  return (
    <div className="two-column">
      <section className="panel">
        <div className="panel-header"><h3>Add Placement</h3></div>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>Student<select value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })} required><option value="">Select</option>{students.map((student) => <option key={student.id} value={student.id}>{student.name}</option>)}</select></label>
          <label>Company<input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} required /></label>
          <label>Package<input type="number" step="0.01" value={form.package} onChange={(e) => setForm({ ...form, package: e.target.value })} required /></label>
          <label>Year<input type="number" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} required /></label>
          <button className="button" type="submit">Save Placement</button>
        </form>
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Placement Tracking</h3></div>
        <table className="data-table">
          <thead><tr><th>Student</th><th>Company</th><th>Package</th><th>Year</th></tr></thead>
          <tbody>
            {placements.map((placement) => (
              <tr key={placement.id}><td>{placement.student_name}</td><td>{placement.company}</td><td>{placement.package}</td><td>{placement.year}</td></tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default Placements
