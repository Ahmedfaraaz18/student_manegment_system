import { useNavigate } from "react-router-dom"

import { auth } from "../services/api"

function Navbar() {
  const navigate = useNavigate()
  const role = auth.getRole()
  const username = auth.getUsername()
  const institutionName = auth.getInstitutionShortName() || auth.getInstitutionName()
  const institutionType = auth.getInstitutionType()
  const portalTitle =
    role === "admin"
      ? institutionType === "school"
        ? "School admin portal"
        : "College admin portal"
      : role
        ? `${role.charAt(0).toUpperCase()}${role.slice(1)} portal`
        : "Dashboard"

  const handleLogout = () => {
    auth.logout()
    const loginRoute = role === "super_admin" ? "/super-admin/login" : role === "teacher" ? "/teacher/login" : role === "student" ? "/student/login" : "/admin/login"
    navigate(loginRoute)
  }

  return (
    <header className="navbar">
      <div>
        <p className="eyebrow">{institutionName || "Multi-Institution ERP"}</p>
        <h1 className="navbar-title">{portalTitle}</h1>
      </div>
      <div className="navbar-actions">
        <div>
          <p className="meta-label">Signed in as</p>
          <p className="meta-value">{username || "guest"}</p>
        </div>
        <button className="button button-secondary" onClick={handleLogout}>Logout</button>
      </div>
    </header>
  )
}

export default Navbar
