import { Navigate, useLocation } from "react-router-dom"

import { auth } from "../services/api"

function ProtectedRoute({ allowedRoles, allowedInstitutionTypes, children }) {
  const location = useLocation()
  const token = auth.getToken()
  const role = auth.getRole()
  const institutionType = auth.getInstitutionType()

  if (!token) {
    const loginRoute =
      allowedRoles?.[0] === "super_admin"
        ? "/super-admin/login"
        : allowedRoles?.[0] === "teacher"
        ? "/teacher/login"
        : allowedRoles?.[0] === "student"
          ? "/student/login"
          : "/admin/login"
    return <Navigate to={loginRoute} replace state={{ from: location }} />
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    const fallback = role === "super_admin" ? "/super-admin/dashboard" : role === "teacher" ? "/teacher/dashboard" : role === "student" ? "/student/dashboard" : "/admin/dashboard"
    return <Navigate to={fallback} replace />
  }

  if (allowedInstitutionTypes && role === "admin" && !allowedInstitutionTypes.includes(institutionType)) {
    return <Navigate to="/admin/dashboard" replace />
  }

  return children
}

export default ProtectedRoute
