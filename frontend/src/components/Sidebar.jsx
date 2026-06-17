import { NavLink } from "react-router-dom"

import { auth } from "../services/api"

const linksByRole = {
  super_admin: [
    ["/super-admin/dashboard", "Platform Dashboard"],
    ["/super-admin/tenants", "Tenants"],
  ],
  admin: [
    ["/admin/dashboard", "Dashboard"],
    ["/admin/institution", "Institution Setup"],
    ["/admin/admissions", "Admissions"],
    ["/admin/fees", "Fees"],
    ["/admin/approvals", "Approvals"],
    ["/admin/departments", "Departments"],
    ["/admin/teachers", "Teachers"],
    ["/admin/students", "Students"],
    ["/admin/subjects", "Subjects"],
    ["/admin/attendance", "Attendance"],
    ["/admin/exams", "Exams & Results"],
    ["/admin/placements", "Placements"],
  ],
  teacher: [
    ["/teacher/dashboard", "Dashboard"],
    ["/admin/attendance", "Attendance"],
    ["/admin/exams", "Marks Upload"],
  ],
  student: [["/student/dashboard", "Dashboard"]],
}

function Sidebar() {
  const role = auth.getRole() || "student"
  const institutionType = auth.getInstitutionType()
  const adminLinks =
    institutionType === "school"
      ? [
          ["/admin/dashboard", "Dashboard"],
          ["/admin/institution", "School Setup"],
          ["/admin/fees", "Fees"],
          ["/admin/approvals", "Approvals"],
          ["/admin/departments", "Classes"],
          ["/admin/teachers", "Teachers"],
          ["/admin/students", "Students"],
          ["/admin/subjects", "Subjects"],
          ["/admin/attendance", "Attendance"],
          ["/admin/exams", "Exams & Results"],
        ]
      : linksByRole.admin
  const links = role === "admin" ? adminLinks : linksByRole[role] || []
  const productLabel = institutionType === "school" ? "School ERP Suite" : "College ERP Suite"
  const brand = institutionType === "school" ? "CampusFlow School" : "CampusFlow"

  return (
    <aside className="sidebar">
      <div>
        <p className="eyebrow">{role === "admin" ? productLabel : "ERP SaaS Suite"}</p>
        <h2 className="sidebar-brand">{brand}</h2>
      </div>
      <nav className="sidebar-nav">
        {links.map(([to, label]) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
          >
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
