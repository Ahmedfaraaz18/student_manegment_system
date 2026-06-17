import { useEffect, useState } from "react"

import StatsCard from "../components/StatsCard"
import api, { endpoints } from "../services/api"

function TeacherDashboard() {
  const [data, setData] = useState({ subjects: [], students: [], recent_results: [] })

  useEffect(() => {
    api.get(endpoints.teacherDashboard).then((response) => setData(response.data))
  }, [])

  return (
    <div className="stack-lg">
      <section className="stats-grid">
        <StatsCard label="Assigned Subjects" value={data.subjects.length} accent="cool" />
        <StatsCard label="Department Students" value={data.students.length} accent="warm" />
        <StatsCard label="Uploaded Marks" value={data.recent_results.length} accent="accent" />
      </section>
      <section className="two-column">
        <div className="panel">
          <div className="panel-header"><h3>Assigned Subjects</h3></div>
          <ul className="simple-list">{data.subjects.map((subject) => <li key={subject.id}>{subject.name} <span>{subject.department__name}</span></li>)}</ul>
        </div>
        <div className="panel">
          <div className="panel-header"><h3>Students in Department</h3></div>
          <table className="data-table compact">
            <thead><tr><th>Name</th><th>Email</th><th>Year</th></tr></thead>
            <tbody>{data.students.map((student) => <tr key={student.id}><td>{student.name}</td><td>{student.email}</td><td>{student.year}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

export default TeacherDashboard
