import { useEffect, useState } from "react"

import api, { endpoints } from "../services/api"

const defaultSettings = {
  short_name: "",
  primary_color: "#11243d",
  support_email: "",
  attendance_threshold: 75,
  grading_scheme: "",
  current_academic_year: "",
  logo_url: "",
}

function InstitutionSetup() {
  const [settings, setSettings] = useState(defaultSettings)
  const [academicYears, setAcademicYears] = useState([])
  const [programs, setPrograms] = useState([])
  const [sections, setSections] = useState([])
  const [departments, setDepartments] = useState([])
  const [yearForm, setYearForm] = useState({ name: "", start_date: "", end_date: "", is_current: false })
  const [programForm, setProgramForm] = useState({ name: "", code: "", duration_years: 4, department: "" })
  const [sectionForm, setSectionForm] = useState({ name: "", semester: 1, capacity: 60, academic_year: "", program: "" })
  const [message, setMessage] = useState("")

  const loadData = async () => {
    const [settingsRes, yearsRes, programsRes, sectionsRes, departmentsRes] = await Promise.all([
      api.get(endpoints.institutionSettings),
      api.get(endpoints.academicYears),
      api.get(endpoints.programs),
      api.get(endpoints.sections),
      api.get(endpoints.departments),
    ])
    setSettings((current) => ({ ...current, ...settingsRes.data }))
    setAcademicYears(yearsRes.data)
    setPrograms(programsRes.data)
    setSections(sectionsRes.data)
    setDepartments(departmentsRes.data)
  }

  useEffect(() => {
    loadData()
  }, [])

  const saveSettings = async (event) => {
    event.preventDefault()
    await api.put(endpoints.institutionSettings, settings)
    setMessage("Institution settings saved.")
    loadData()
  }

  const createAcademicYear = async (event) => {
    event.preventDefault()
    await api.post(endpoints.academicYears, yearForm)
    setYearForm({ name: "", start_date: "", end_date: "", is_current: false })
    setMessage("Academic year created.")
    loadData()
  }

  const createProgram = async (event) => {
    event.preventDefault()
    await api.post(endpoints.programs, { ...programForm, duration_years: Number(programForm.duration_years), department: Number(programForm.department) })
    setProgramForm({ name: "", code: "", duration_years: 4, department: "" })
    setMessage("Program created.")
    loadData()
  }

  const createSection = async (event) => {
    event.preventDefault()
    await api.post(endpoints.sections, {
      ...sectionForm,
      semester: Number(sectionForm.semester),
      capacity: Number(sectionForm.capacity),
      academic_year: Number(sectionForm.academic_year),
      program: Number(sectionForm.program),
    })
    setSectionForm({ name: "", semester: 1, capacity: 60, academic_year: "", program: "" })
    setMessage("Section created.")
    loadData()
  }

  return (
    <div className="stack-lg">
      <section className="hero-card">
        <p className="eyebrow">ERP Foundation</p>
        <h2>Institution settings and academic structure</h2>
        <p className="helper-text">Set up branding, attendance policy, academic year, programs, and sections before layering fees, timetable, and admissions.</p>
      </section>
      {message ? <p className="success-text">{message}</p> : null}
      <section className="panel">
        <div className="panel-header"><h3>Institution Settings</h3></div>
        <form className="form-grid two-column" onSubmit={saveSettings}>
          <label>Short Name<input value={settings.short_name || ""} onChange={(e) => setSettings({ ...settings, short_name: e.target.value })} /></label>
          <label>Support Email<input type="email" value={settings.support_email || ""} onChange={(e) => setSettings({ ...settings, support_email: e.target.value })} /></label>
          <label>Primary Color<input value={settings.primary_color || ""} onChange={(e) => setSettings({ ...settings, primary_color: e.target.value })} /></label>
          <label>Attendance Threshold<input type="number" min="1" max="100" value={settings.attendance_threshold || 75} onChange={(e) => setSettings({ ...settings, attendance_threshold: Number(e.target.value) })} /></label>
          <label>Current Academic Year<input value={settings.current_academic_year || ""} onChange={(e) => setSettings({ ...settings, current_academic_year: e.target.value })} /></label>
          <label>Logo URL<input value={settings.logo_url || ""} onChange={(e) => setSettings({ ...settings, logo_url: e.target.value })} /></label>
          <label className="form-span-2">Grading Scheme<textarea rows="5" value={settings.grading_scheme || ""} onChange={(e) => setSettings({ ...settings, grading_scheme: e.target.value })} /></label>
          <button className="button" type="submit">Save Settings</button>
        </form>
      </section>
      <section className="two-column">
        <div className="panel">
          <div className="panel-header"><h3>Add Academic Year</h3></div>
          <form className="form-grid" onSubmit={createAcademicYear}>
            <label>Name<input value={yearForm.name} onChange={(e) => setYearForm({ ...yearForm, name: e.target.value })} placeholder="2026-27" required /></label>
            <label>Start Date<input type="date" value={yearForm.start_date} onChange={(e) => setYearForm({ ...yearForm, start_date: e.target.value })} required /></label>
            <label>End Date<input type="date" value={yearForm.end_date} onChange={(e) => setYearForm({ ...yearForm, end_date: e.target.value })} required /></label>
            <label><input type="checkbox" checked={yearForm.is_current} onChange={(e) => setYearForm({ ...yearForm, is_current: e.target.checked })} /> Mark as current</label>
            <button className="button" type="submit">Create Academic Year</button>
          </form>
          <table className="data-table compact-table">
            <thead><tr><th>Name</th><th>Current</th></tr></thead>
            <tbody>{academicYears.map((year) => <tr key={year.id}><td>{year.name}</td><td>{year.is_current ? "Yes" : "No"}</td></tr>)}</tbody>
          </table>
        </div>
        <div className="panel">
          <div className="panel-header"><h3>Add Program</h3></div>
          <form className="form-grid" onSubmit={createProgram}>
            <label>Name<input value={programForm.name} onChange={(e) => setProgramForm({ ...programForm, name: e.target.value })} placeholder="B.E. Computer Science" required /></label>
            <label>Code<input value={programForm.code} onChange={(e) => setProgramForm({ ...programForm, code: e.target.value })} placeholder="BE-CSE" required /></label>
            <label>Duration (Years)<input type="number" min="1" value={programForm.duration_years} onChange={(e) => setProgramForm({ ...programForm, duration_years: e.target.value })} required /></label>
            <label>Department<select value={programForm.department} onChange={(e) => setProgramForm({ ...programForm, department: e.target.value })} required><option value="">Select</option>{departments.map((department) => <option key={department.id} value={department.id}>{department.name}</option>)}</select></label>
            <button className="button" type="submit">Create Program</button>
          </form>
          <table className="data-table compact-table">
            <thead><tr><th>Program</th><th>Department</th></tr></thead>
            <tbody>{programs.map((program) => <tr key={program.id}><td>{program.name}</td><td>{program.department_name}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Add Section</h3></div>
        <form className="form-grid three-column" onSubmit={createSection}>
          <label>Section<input value={sectionForm.name} onChange={(e) => setSectionForm({ ...sectionForm, name: e.target.value })} placeholder="A" required /></label>
          <label>Semester<input type="number" min="1" value={sectionForm.semester} onChange={(e) => setSectionForm({ ...sectionForm, semester: e.target.value })} required /></label>
          <label>Capacity<input type="number" min="1" value={sectionForm.capacity} onChange={(e) => setSectionForm({ ...sectionForm, capacity: e.target.value })} required /></label>
          <label>Academic Year<select value={sectionForm.academic_year} onChange={(e) => setSectionForm({ ...sectionForm, academic_year: e.target.value })} required><option value="">Select</option>{academicYears.map((year) => <option key={year.id} value={year.id}>{year.name}</option>)}</select></label>
          <label>Program<select value={sectionForm.program} onChange={(e) => setSectionForm({ ...sectionForm, program: e.target.value })} required><option value="">Select</option>{programs.map((program) => <option key={program.id} value={program.id}>{program.name}</option>)}</select></label>
          <button className="button" type="submit">Create Section</button>
        </form>
        <table className="data-table">
          <thead><tr><th>Program</th><th>Year</th><th>Semester</th><th>Section</th><th>Capacity</th></tr></thead>
          <tbody>{sections.map((section) => <tr key={section.id}><td>{section.program_name}</td><td>{section.academic_year_name}</td><td>{section.semester}</td><td>{section.name}</td><td>{section.capacity}</td></tr>)}</tbody>
        </table>
      </section>
    </div>
  )
}

export default InstitutionSetup
