import { useEffect, useState } from "react"
import API from "../services/api"

export default function Results() {
  const role = localStorage.getItem("role")
  const [rows, setRows] = useState([])
  const [students, setStudents] = useState([])
  const [subjects, setSubjects] = useState([])
  const [form, setForm] = useState({
    student: "",
    subject: "",
    exam_type: "IA1",
    marks: "",
    date: new Date().toISOString().slice(0, 10),
  })

  const canUpload = role === "institution_admin" || role === "teacher" || role === "super_admin"

  const load = async () => {
    const [reportRes, studentsRes, subjectsRes] = await Promise.all([
      API.get("/results/report/"),
      canUpload ? API.get("/students/") : Promise.resolve({ data: [] }),
      canUpload ? API.get("/subjects/") : Promise.resolve({ data: [] }),
    ])
    setRows(reportRes.data || [])
    setStudents(studentsRes.data || [])
    setSubjects(subjectsRes.data || [])
  }

  useEffect(() => {
    load().catch(() => {})
  }, [])

  const submit = async () => {
    if (!canUpload) return
    await API.post("/results/", {
      ...form,
      marks: Number(form.marks),
    })
    setForm({ ...form, marks: "" })
    load()
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Results</h1>

      {canUpload && (
        <div className="bg-white shadow rounded p-4 mb-6 grid grid-cols-1 md:grid-cols-5 gap-3">
          <select className="border p-2 rounded" value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })}>
            <option value="">Select Student</option>
            {students.map((s) => (
              <option value={s.id} key={s.id}>{`${s.first_name} ${s.last_name}`}</option>
            ))}
          </select>
          <select className="border p-2 rounded" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })}>
            <option value="">Select Subject</option>
            {subjects.map((s) => (
              <option value={s.id} key={s.id}>{s.name}</option>
            ))}
          </select>
          <select className="border p-2 rounded" value={form.exam_type} onChange={(e) => setForm({ ...form, exam_type: e.target.value })}>
            <option value="IA1">IA1</option>
            <option value="IA2">IA2</option>
            <option value="MID">MID</option>
            <option value="FINAL">FINAL</option>
          </select>
          <input className="border p-2 rounded" type="number" placeholder="Marks" value={form.marks} onChange={(e) => setForm({ ...form, marks: e.target.value })} />
          <button onClick={submit} className="bg-blue-600 text-white rounded px-3 py-2">Upload Marks</button>
        </div>
      )}

      <div className="bg-white shadow rounded p-4 overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Student</th>
              <th className="text-left py-2">Subject</th>
              <th className="text-left py-2">Marks</th>
              <th className="text-left py-2">Grade</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={`${row.student}-${row.subject}-${i}`} className="border-b">
                <td className="py-2">{row.student}</td>
                <td className="py-2">{row.subject}</td>
                <td className="py-2">{row.marks}</td>
                <td className="py-2">{row.grade}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
