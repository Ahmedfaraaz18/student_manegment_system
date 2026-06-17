import API from "./api"

export const getStudents = () => {
  return API.get("/students/")
}

export const createStudent = (data) => {
  return API.post("/students/", data)
}

export const updateStudent = (id,data) => {
  return API.put(`/students/${id}/`, data)
}

export const deleteStudent = (id) => {
  return API.delete(`/students/${id}/`)
}
