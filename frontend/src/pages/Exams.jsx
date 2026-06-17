import { useEffect, useState } from "react"

import api, { auth, endpoints } from "../services/api"

function Exams() {
  const [exams, setExams] = useState([])
  const [subjects, setSubjects] = useState([])
  const [students, setStudents] = useState([])
  const [examForm, setExamForm] = useState({ name: "", date: "" })
  const [markForm, setMarkForm] = useState({ exam: "", subject: "", student: "", marks: "" })
  const [results, setResults] = useState([])
  const isAdmin = auth.getRole() === "admin"

  const loadData = async () => {
    const [examRes, subjectRes, studentRes, resultRes] = await Promise.all([
      api.get(endpoints.exams),
      api.get(endpoints.subjects),
      api.get(endpoints.students),
      api.get(endpoints.results),
    ])
    setExams(examRes.data)
    setSubjects(subjectRes.data)
    setStudents(studentRes.data)
    setResults(resultRes.data)
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleExamSubmit = async (event) => {
    event.preventDefault()
    await api.post(endpoints.exams, examForm)
    setExamForm({ name: "", date: "" })
    loadData()
  }

  const handleMarksSubmit = async (event) => {
    event.preventDefault()
    await api.post(endpoints.resultUpload, {
      results: [{
        exam: Number(markForm.exam),
        subject: Number(markForm.subject),
        student: Number(markForm.student),
        marks: Number(markForm.marks),
      }],
    })
    setMarkForm({ exam: "", subject: "", student: "", marks: "" })
    loadData()
  }

  return (
    <div className="stack-lg">
      {isAdmin ? (
        <section className="panel">
          <div className="panel-header"><h3>Create Exam</h3></div>
          <form className="form-grid" onSubmit={handleExamSubmit}>
            <label>Exam Name<input value={examForm.name} onChange={(e) => setExamForm({ ...examForm, name: e.target.value })} required /></label>
            <label>Date<input type="date" value={examForm.date} onChange={(e) => setExamForm({ ...examForm, date: e.target.value })} required /></label>
            <button className="button" type="submit">Create Exam</button>
          </form>
        </section>
      ) : null}
      <section className="panel">
        <div className="panel-header"><h3>Upload Marks</h3></div>
        <form className="form-grid" onSubmit={handleMarksSubmit}>
          <label>Exam<select value={markForm.exam} onChange={(e) => setMarkForm({ ...markForm, exam: e.target.value })} required><option value="">Select</option>{exams.map((exam) => <option key={exam.id} value={exam.id}>{exam.name}</option>)}</select></label>
          <label>Subject<select value={markForm.subject} onChange={(e) => setMarkForm({ ...markForm, subject: e.target.value })} required><option value="">Select</option>{subjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>)}</select></label>
          <label>Student<select value={markForm.student} onChange={(e) => setMarkForm({ ...markForm, student: e.target.value })} required><option value="">Select</option>{students.map((student) => <option key={student.id} value={student.id}>{student.name}</option>)}</select></label>
          <label>Marks<input type="number" value={markForm.marks} onChange={(e) => setMarkForm({ ...markForm, marks: e.target.value })} required /></label>
          <button className="button" type="submit">Save Marks</button>
        </form>
      </section>
      <section className="panel">
        <div className="panel-header"><h3>Result Table</h3></div>
        <table className="data-table">
          <thead><tr><th>Student</th><th>Subject</th><th>Exam</th><th>Marks</th><th>Grade</th></tr></thead>
          <tbody>
            {results.map((result) => (
              <tr key={result.id}><td>{result.student_name}</td><td>{result.subject_name}</td><td>{result.exam_name || "General"}</td><td>{result.marks}</td><td>{result.grade}</td></tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default Exams
