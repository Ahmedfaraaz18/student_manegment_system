import { useEffect, useState } from "react"

import api, { auth, endpoints } from "../services/api"

function Attendance() {
  const [departments, setDepartments] = useState([])
  const [subjects, setSubjects] = useState([])
  const [students, setStudents] = useState([])
  const [records, setRecords] = useState([])
  const [filters, setFilters] = useState({ department: "", subject: "", date: new Date().toISOString().slice(0, 10) })

  useEffect(() => {
    Promise.all([api.get(endpoints.departments), api.get(endpoints.subjects), api.get(endpoints.students)]).then(([d, s, st]) => {
      setDepartments(d.data)
      setSubjects(s.data)
      setStudents(st.data)
    })
  }, [])

  useEffect(() => {
    const filteredStudents = students.filter((student) => String(student.department) === String(filters.department || student.department))
    setRecords(filteredStudents.map((student) => ({ student: student.id, name: student.name, status: "Present" })))
  }, [students, filters.department])

  const visibleSubjects = subjects.filter((subject) => !filters.department || String(subject.department) === String(filters.department))

  const handleRecordChange = (studentId, status) => {
    setRecords((current) => current.map((record) => (record.student === studentId ? { ...record, status } : record)))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    await api.post(endpoints.attendanceMark, {
      subject: Number(filters.subject),
      date: filters.date,
      records: records.map(({ student, status }) => ({ student, status })),
    })
  }

  const isTeacher = auth.getRole() === "teacher"

  return (
    <div className="stack-lg">
      <section className="panel">
        <div className="panel-header"><h3>{isTeacher ? "Teacher Attendance" : "Attendance Control"}</h3></div>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>Department<select value={filters.department} onChange={(e) => setFilters({ ...filters, department: e.target.value })} required><option value="">Select</option>{departments.map((department) => <option key={department.id} value={department.id}>{department.name}</option>)}</select></label>
          <label>Subject<select value={filters.subject} onChange={(e) => setFilters({ ...filters, subject: e.target.value })} required><option value="">Select</option>{visibleSubjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>)}</select></label>
          <label>Date<input type="date" value={filters.date} onChange={(e) => setFilters({ ...filters, date: e.target.value })} required /></label>
          <button className="button" type="submit">Mark Attendance</button>
        </form>
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Student Register</h3></div>
        <table className="data-table">
          <thead><tr><th>Student</th><th>Status</th></tr></thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.student}>
                <td>{record.name}</td>
                <td>
                  <select value={record.status} onChange={(e) => handleRecordChange(record.student, e.target.value)}>
                    <option value="Present">Present</option>
                    <option value="Absent">Absent</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default Attendance
