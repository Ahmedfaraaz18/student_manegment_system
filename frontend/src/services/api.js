import axios from "axios"

const apiBaseUrl = import.meta.env.DEV
  ? import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api"
  : "https://student-manegment-system-c380.onrender.com/api"

const api = axios.create({
  baseURL: apiBaseUrl,
})

api.interceptors.request.use((config) => {
  const isPublicAuthRequest = config.url?.includes("/login/")
  const token = localStorage.getItem("token")
  if (token && !isPublicAuthRequest) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export function extractApiError(error, fallback = "Request failed") {
  const detail = error?.response?.data
  if (!detail) {
    return error?.message || fallback
  }
  if (typeof detail === "string") {
    return detail
  }
  if (typeof detail.detail === "string") {
    return detail.detail
  }
  const messages = Object.entries(detail).flatMap(([key, value]) => {
    if (Array.isArray(value)) {
      return value.map((item) => `${key}: ${item}`)
    }
    if (typeof value === "string") {
      return `${key}: ${value}`
    }
    return []
  })
  return messages[0] || fallback
}

export const auth = {
  getToken: () => localStorage.getItem("token"),
  getRole: () => localStorage.getItem("role"),
  getUsername: () => localStorage.getItem("username"),
  getInstitutionName: () => localStorage.getItem("institutionName"),
  getInstitutionShortName: () => localStorage.getItem("institutionShortName"),
  getInstitutionCode: () => localStorage.getItem("institutionCode"),
  getInstitutionType: () => localStorage.getItem("institutionType") || "college",
  login: (payload) => api.post("/login/", payload),
  logout: () => {
    localStorage.removeItem("token")
    localStorage.removeItem("refresh")
    localStorage.removeItem("role")
    localStorage.removeItem("username")
    localStorage.removeItem("institutionId")
    localStorage.removeItem("institutionName")
    localStorage.removeItem("institutionCode")
    localStorage.removeItem("institutionShortName")
    localStorage.removeItem("institutionType")
  },
  saveSession: ({ token, refresh, role, username, institution }) => {
    localStorage.setItem("token", token)
    if (refresh) {
      localStorage.setItem("refresh", refresh)
    } else {
      localStorage.removeItem("refresh")
    }
    localStorage.setItem("role", role)
    localStorage.setItem("username", username)
    if (institution) {
      localStorage.setItem("institutionId", institution.id)
      localStorage.setItem("institutionName", institution.name)
      localStorage.setItem("institutionCode", institution.code)
      localStorage.setItem("institutionShortName", institution.short_name || institution.name)
      localStorage.setItem("institutionType", institution.institution_type || "college")
    } else {
      localStorage.removeItem("institutionId")
      localStorage.removeItem("institutionName")
      localStorage.removeItem("institutionCode")
      localStorage.removeItem("institutionShortName")
      localStorage.removeItem("institutionType")
    }
  },
}

export const endpoints = {
  superAdminDashboard: "/tenants/dashboard/",
  tenants: "/tenants/institutions/",
  subscriptionPlans: "/tenants/plans/",
  tenantSubscriptions: "/tenants/subscriptions/",
  institutionSettings: "/accounts/settings/",
  academicYears: "/academics/academic-years/",
  programs: "/academics/programs/",
  sections: "/academics/sections/",
  admissions: "/admissions/",
  dashboardAnalytics: "/dashboard/analytics/",
  teacherDashboard: "/dashboard/teacher/",
  studentDashboard: "/dashboard/student/",
  departments: "/departments/",
  teachers: "/teachers/",
  students: "/students/",
  subjects: "/subjects/",
  attendance: "/attendance/",
  attendanceMark: "/attendance/mark/",
  attendanceSummary: "/attendance/summary/",
  exams: "/exams/",
  feeStructures: "/fees/structures/",
  feeInvoices: "/fees/invoices/",
  feePayments: "/fees/payments/",
  results: "/results/",
  resultUpload: "/results/upload-marks/",
  resultStudentSummary: "/results/student-summary/",
  placements: "/placements/",
  placementStats: "/placements/stats/",
  announcements: "/announcements/",
  workflows: "/workflows/",
  aiBriefing: "/ai/briefing/",
  aiChat: "/ai/chat/",
}

export default api
