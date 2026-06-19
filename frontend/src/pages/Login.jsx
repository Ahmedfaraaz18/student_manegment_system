import { Link, useNavigate } from "react-router-dom"
import { useEffect, useState } from "react"

import api, { auth } from "../services/api"

const productionLoginUrl = "https://student-manegment-system-c380.onrender.com/api/login/"

const roleConfig = {
  super_admin: {
    title: "Super admin login",
    eyebrow: "Global SaaS Control",
    description: "Provision institutions, manage plans, suspend tenants, and monitor platform-wide usage.",
    redirect: "/super-admin/dashboard",
    accentClass: "intro-panel admin-theme",
  },
  admin: {
    title: "Admin login",
    eyebrow: "Administration",
    description: "Manage departments, teachers, students, attendance, exams, results, placements, and analytics.",
    redirect: "/admin/dashboard",
    accentClass: "intro-panel admin-theme",
  },
  teacher: {
    title: "Teacher login",
    eyebrow: "Faculty Portal",
    description: "Access assigned subjects, department students, attendance entry, and marks upload.",
    redirect: "/teacher/dashboard",
    accentClass: "intro-panel teacher-theme",
  },
  student: {
    title: "Student login",
    eyebrow: "Student Portal",
    description: "View attendance percentage, marks, exam results, and college announcements.",
    redirect: "/student/dashboard",
    accentClass: "intro-panel student-theme",
  },
}

function Login({ role = "admin" }) {
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: "", password: "" })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const config = roleConfig[role] || roleConfig.admin

  useEffect(() => {
    auth.logout()
  }, [role])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError("")

    try {
      auth.logout()
      const loginUrl = import.meta.env.DEV ? "/login/" : productionLoginUrl
      const { data } = await api.post(loginUrl, form)
      if (data.role !== role) {
        auth.logout()
        setError(`This login page is only for ${role} accounts.`)
        return
      }
      auth.saveSession(data)
      navigate(config.redirect)
    } catch (err) {
      const apiMessage = err.response?.data?.detail
      const networkMessage = err.response
        ? null
        : `${err.message || "Network error"} (${import.meta.env.DEV ? `${api.defaults.baseURL}/login/` : productionLoginUrl})`
      setError(apiMessage || networkMessage || "Unable to log in")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-shell">
      <div className={`login-panel ${config.accentClass}`}>
        <p className="eyebrow">{config.eyebrow}</p>
        <h1>{config.title}</h1>
        <p>{config.description}</p>
        <div className="portal-links">
          <Link to="/super-admin/login">Super Admin</Link>
          <Link to="/admin/login">Admin</Link>
          <Link to="/teacher/login">Teacher</Link>
          <Link to="/student/login">Student</Link>
        </div>
      </div>
      <form className="login-panel form-panel" onSubmit={handleSubmit}>
        <h2>{config.title}</h2>
        <label>
          Username
          <input
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            placeholder={role === "admin" ? "institution admin username" : "email address"}
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            placeholder={role === "admin" ? "Your password" : "default123"}
          />
        </label>
        {role !== "admin" ? <p className="helper-text">Teacher and student accounts are created automatically with `default123`.</p> : null}
        {error ? <p className="error-text">{error}</p> : null}
        <button className="button" disabled={loading} type="submit">
          {loading ? "Signing in..." : `Login as ${role}`}
        </button>
      </form>
    </div>
  )
}

export default Login
