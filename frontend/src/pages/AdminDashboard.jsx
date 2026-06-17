import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { useEffect, useState } from "react"

import StatsCard from "../components/StatsCard"
import api, { auth, endpoints } from "../services/api"

function AdminDashboard() {
  const [data, setData] = useState({ totals: {}, placement_statistics: { companies: [] } })
  const institutionType = auth.getInstitutionType()
  const isSchool = institutionType === "school"

  useEffect(() => {
    api.get(endpoints.dashboardAnalytics).then((response) => setData(response.data))
  }, [])

  return (
    <div className="stack-lg">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Admin Control Center</p>
          <h2>{isSchool ? "School operations, academics, and attendance visibility" : "College-wide metrics, structure setup, and placement visibility"}</h2>
          <p className="helper-text">Current academic year: {data.academic_overview?.current_year || "Not configured"}</p>
        </div>
      </section>
      <section className="stats-grid">
        <StatsCard label="Total Students" value={data.totals.students || 0} accent="warm" />
        <StatsCard label="Total Teachers" value={data.totals.teachers || 0} accent="cool" />
        <StatsCard label={isSchool ? "Classes" : "Departments"} value={data.totals.departments || 0} accent="default" />
        <StatsCard label={isSchool ? "Attendance Records" : "Placements"} value={isSchool ? data.totals.attendance_records || 0 : data.placement_statistics.total_placements || 0} accent="accent" />
      </section>
      <section className="stats-grid">
        <StatsCard label={isSchool ? "Subjects" : "Programs"} value={isSchool ? data.totals.subjects || 0 : data.totals.programs || 0} accent="cool" />
        <StatsCard label={isSchool ? "Results" : "Sections"} value={isSchool ? data.totals.results || 0 : data.totals.sections || 0} accent="warm" />
        <StatsCard label="Subjects" value={data.totals.subjects || 0} accent="default" />
        <StatsCard label="Results" value={data.totals.results || 0} accent="accent" />
      </section>
      <section className="stats-grid">
        <StatsCard label={isSchool ? "Fee Pending" : "Admissions"} value={isSchool ? data.totals.pending_fees || 0 : data.totals.admissions || 0} accent="warm" />
        <StatsCard label="Pending Fees" value={data.totals.pending_fees || 0} accent="accent" />
        <StatsCard label="Attendance Records" value={data.totals.attendance_records || 0} accent="cool" />
        <StatsCard label="Current Year" value={data.academic_overview?.current_year || "-"} accent="default" />
      </section>
      {!isSchool ? (
        <section className="panel">
          <div className="panel-header">
            <h3>Placement Statistics</h3>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={data.placement_statistics.companies || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="company" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#e56b2c" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      ) : null}
    </div>
  )
}

export default AdminDashboard
