import { useEffect, useState } from "react"

import api, { endpoints } from "../services/api"

function Admissions() {
  const [applications, setApplications] = useState([])
  const [academicYears, setAcademicYears] = useState([])
  const [programs, setPrograms] = useState([])
  const [sections, setSections] = useState([])
  const [form, setForm] = useState({
    applicant_name: "",
    email: "",
    phone: "",
    previous_qualification: "",
    academic_year: "",
    program: "",
    section: "",
    notes: "",
  })

  const loadData = async () => {
    const [appsRes, yearsRes, programsRes, sectionsRes] = await Promise.all([
      api.get(endpoints.admissions),
      api.get(endpoints.academicYears),
      api.get(endpoints.programs),
      api.get(endpoints.sections),
    ])
    setApplications(appsRes.data)
    setAcademicYears(yearsRes.data)
    setPrograms(programsRes.data)
    setSections(sectionsRes.data)
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    await api.post(endpoints.admissions, {
      ...form,
      academic_year: Number(form.academic_year),
      program: Number(form.program),
      section: form.section ? Number(form.section) : null,
    })
    setForm({
      applicant_name: "",
      email: "",
      phone: "",
      previous_qualification: "",
      academic_year: "",
      program: "",
      section: "",
      notes: "",
    })
    loadData()
  }

  const handleStatusChange = async (application, status) => {
    await api.patch(`${endpoints.admissions}${application.id}/`, { status })
    loadData()
  }

  return (
    <div className="stack-lg">
      <section className="two-column">
        <div className="panel">
          <div className="panel-header"><h3>Create Admission Application</h3></div>
          <form className="form-grid" onSubmit={handleSubmit}>
            <label>Applicant Name<input value={form.applicant_name} onChange={(e) => setForm({ ...form, applicant_name: e.target.value })} required /></label>
            <label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></label>
            <label>Phone<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
            <label>Previous Qualification<input value={form.previous_qualification} onChange={(e) => setForm({ ...form, previous_qualification: e.target.value })} /></label>
            <label>Academic Year<select value={form.academic_year} onChange={(e) => setForm({ ...form, academic_year: e.target.value })} required><option value="">Select</option>{academicYears.map((year) => <option key={year.id} value={year.id}>{year.name}</option>)}</select></label>
            <label>Program<select value={form.program} onChange={(e) => setForm({ ...form, program: e.target.value })} required><option value="">Select</option>{programs.map((program) => <option key={program.id} value={program.id}>{program.name}</option>)}</select></label>
            <label>Section<select value={form.section} onChange={(e) => setForm({ ...form, section: e.target.value })}><option value="">Optional</option>{sections.map((section) => <option key={section.id} value={section.id}>{section.program_name} - Sem {section.semester} {section.name}</option>)}</select></label>
            <label>Notes<textarea rows="3" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></label>
            <button className="button" type="submit">Save Application</button>
          </form>
        </div>
        <div className="panel">
          <div className="panel-header"><h3>Admission Workflow</h3></div>
          <p className="helper-text">Use this as the ERP admission funnel: application intake, review, approval, and section assignment.</p>
          <table className="data-table compact-table">
            <thead><tr><th>Applicant</th><th>Program</th><th>Status</th></tr></thead>
            <tbody>{applications.slice(0, 6).map((app) => <tr key={app.id}><td>{app.applicant_name}</td><td>{app.program_name}</td><td>{app.status}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Applications</h3></div>
        <table className="data-table">
          <thead><tr><th>Applicant</th><th>Email</th><th>Academic Year</th><th>Program</th><th>Section</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            {applications.map((application) => (
              <tr key={application.id}>
                <td>{application.applicant_name}</td>
                <td>{application.email}</td>
                <td>{application.academic_year_name}</td>
                <td>{application.program_name}</td>
                <td>{application.section_name || "-"}</td>
                <td>{application.status}</td>
                <td className="table-actions">
                  <button className="button button-small" onClick={() => handleStatusChange(application, "approved")}>Approve</button>
                  <button className="button button-secondary button-small" onClick={() => handleStatusChange(application, "rejected")}>Reject</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default Admissions
