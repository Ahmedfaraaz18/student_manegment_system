import { Link, useNavigate } from "react-router-dom"
import { useEffect, useState } from "react"

import { auth } from "../services/api"

const initialForm = {
  institution_name: "",
  institution_code: "",
  contact_email: "",
  phone: "",
  address: "",
  admin_name: "",
  admin_username: "",
  admin_email: "",
  password: "",
}

function RegisterInstitution() {
  const navigate = useNavigate()
  const [form, setForm] = useState(initialForm)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  useEffect(() => {
    auth.logout()
  }, [])

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError("")
    setSuccess("")

    try {
      const { data } = await auth.registerInstitution(form)
      setSuccess(`Registered ${data.institution.name}. Admin username: ${data.admin.username}`)
      setTimeout(() => navigate("/admin/login"), 1200)
    } catch (err) {
      const payload = err.response?.data
      if (typeof payload === "string") {
        setError(payload)
      } else if (payload && typeof payload === "object") {
        const firstError = Object.values(payload).flat().find(Boolean)
        setError(firstError || "Unable to register institution")
      } else {
        setError("Unable to register institution")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-shell">
      <div className="login-panel intro-panel admin-theme">
        <p className="eyebrow">Institution onboarding</p>
        <h1>Register your college</h1>
        <p>Create a dedicated college workspace with its own admin, departments, students, teachers, exams, results, placements, and announcements.</p>
        <div className="portal-links">
          <Link to="/admin/login">Admin login</Link>
          <Link to="/teacher/login">Teacher login</Link>
          <Link to="/student/login">Student login</Link>
        </div>
      </div>
      <form className="login-panel form-panel" onSubmit={handleSubmit}>
        <h2>Institution setup</h2>
        <div className="form-grid two-column registration-grid">
          <label>
            College name
            <input name="institution_name" value={form.institution_name} onChange={handleChange} placeholder="Sunrise Engineering College" required />
          </label>
          <label>
            College code
            <input name="institution_code" value={form.institution_code} onChange={handleChange} placeholder="sunrise-eng" required />
          </label>
          <label>
            Contact email
            <input name="contact_email" type="email" value={form.contact_email} onChange={handleChange} placeholder="info@college.edu" />
          </label>
          <label>
            Phone
            <input name="phone" value={form.phone} onChange={handleChange} placeholder="+91 9876543210" />
          </label>
          <label className="form-span-2">
            Address
            <textarea name="address" value={form.address} onChange={handleChange} rows="3" placeholder="Campus address" />
          </label>
          <label>
            Admin name
            <input name="admin_name" value={form.admin_name} onChange={handleChange} placeholder="Principal or ERP Admin" required />
          </label>
          <label>
            Admin username
            <input name="admin_username" value={form.admin_username} onChange={handleChange} placeholder="sunrise_admin" required />
          </label>
          <label>
            Admin email
            <input name="admin_email" type="email" value={form.admin_email} onChange={handleChange} placeholder="admin@college.edu" required />
          </label>
          <label>
            Password
            <input name="password" type="password" value={form.password} onChange={handleChange} placeholder="At least 8 characters" required />
          </label>
        </div>
        <p className="helper-text">Each registered college gets isolated data access. Admins can then manage only their own institution.</p>
        {error ? <p className="error-text">{error}</p> : null}
        {success ? <p className="success-text">{success}</p> : null}
        <button className="button" disabled={loading} type="submit">
          {loading ? "Registering..." : "Create college workspace"}
        </button>
      </form>
    </div>
  )
}

export default RegisterInstitution
