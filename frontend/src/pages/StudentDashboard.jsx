import { useEffect, useState } from "react"

import StatsCard from "../components/StatsCard"
import api, { endpoints } from "../services/api"

function StudentDashboard() {
  const [data, setData] = useState({ attendance_percentage: 0, results: [], announcements: [] })

  useEffect(() => {
    api.get(endpoints.studentDashboard).then((response) => setData(response.data))
  }, [])

  return (
    <div className="stack-lg">
      <section className="stats-grid">
        <StatsCard label="Attendance %" value={`${data.attendance_percentage}%`} accent="cool" />
        <StatsCard label="Subjects Marked" value={data.results.length} accent="warm" />
        <StatsCard label="Announcements" value={data.announcements.length} accent="accent" />
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Exam Results</h3></div>
        <table className="data-table">
          <thead><tr><th>Subject</th><th>Exam</th><th>Marks</th><th>Grade</th></tr></thead>
          <tbody>{data.results.map((result, index) => <tr key={`${result.subject}-${index}`}><td>{result.subject}</td><td>{result.exam}</td><td>{result.marks}</td><td>{result.grade}</td></tr>)}</tbody>
        </table>
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Announcements</h3></div>
        <div className="announcement-list">
          {data.announcements.map((announcement) => (
            <article key={announcement.id} className="announcement-card">
              <h4>{announcement.title}</h4>
              <p>{announcement.message}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}

export default StudentDashboard
