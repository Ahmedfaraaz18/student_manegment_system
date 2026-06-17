import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

import Layout from "./components/Layout"
import ProtectedRoute from "./components/ProtectedRoute"
import AdminDashboard from "./pages/AdminDashboard"
import Admissions from "./pages/Admissions"
import Approvals from "./pages/Approvals"
import Attendance from "./pages/Attendance"
import Departments from "./pages/Departments"
import Exams from "./pages/Exams"
import Fees from "./pages/Fees"
import Login from "./pages/Login"
import Placements from "./pages/Placements"
import InstitutionSetup from "./pages/InstitutionSetup"
import StudentDashboard from "./pages/StudentDashboard"
import Students from "./pages/Students"
import Subjects from "./pages/Subjects"
import SuperAdminDashboard from "./pages/SuperAdminDashboard"
import TeacherDashboard from "./pages/TeacherDashboard"
import Teachers from "./pages/Teachers"
import TenantManagement from "./pages/TenantManagement"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/admin/login" replace />} />
        <Route path="/login" element={<Navigate to="/admin/login" replace />} />
        <Route path="/super-admin/login" element={<Login role="super_admin" />} />
        <Route path="/admin/login" element={<Login role="admin" />} />
        <Route path="/teacher/login" element={<Login role="teacher" />} />
        <Route path="/student/login" element={<Login role="student" />} />

        <Route
          path="/super-admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={["super_admin"]}>
              <Layout><SuperAdminDashboard /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/super-admin/tenants"
          element={
            <ProtectedRoute allowedRoles={["super_admin"]}>
              <Layout><TenantManagement /></Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/institution"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Layout><InstitutionSetup /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/admissions"
          element={
            <ProtectedRoute allowedRoles={["admin"]} allowedInstitutionTypes={["college"]}>
              <Layout><Admissions /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/fees"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Layout><Fees /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/approvals"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Layout><Approvals /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Layout><AdminDashboard /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/students"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Layout><Students /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/teachers"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Layout><Teachers /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/departments"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Layout><Departments /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/subjects"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Layout><Subjects /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/attendance"
          element={
            <ProtectedRoute allowedRoles={["admin", "teacher"]}>
              <Layout><Attendance /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/exams"
          element={
            <ProtectedRoute allowedRoles={["admin", "teacher"]}>
              <Layout><Exams /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/placements"
          element={
            <ProtectedRoute allowedRoles={["admin"]} allowedInstitutionTypes={["college"]}>
              <Layout><Placements /></Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/teacher/dashboard"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <Layout><TeacherDashboard /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/dashboard"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <Layout><StudentDashboard /></Layout>
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/admin/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
