import { useEffect, useState } from "react"

import api, { endpoints } from "../services/api"

function Fees() {
  const [structures, setStructures] = useState([])
  const [invoices, setInvoices] = useState([])
  const [payments, setPayments] = useState([])
  const [students, setStudents] = useState([])
  const [academicYears, setAcademicYears] = useState([])
  const [programs, setPrograms] = useState([])
  const [structureForm, setStructureForm] = useState({ name: "", amount: "", due_days: 30, academic_year: "", program: "" })
  const [invoiceForm, setInvoiceForm] = useState({ student: "", fee_structure: "", amount: "", due_date: "" })
  const [paymentForm, setPaymentForm] = useState({ invoice: "", amount: "", payment_date: "", reference_number: "", mode: "cash" })

  const loadData = async () => {
    const [structuresRes, invoicesRes, paymentsRes, studentsRes, yearsRes, programsRes] = await Promise.all([
      api.get(endpoints.feeStructures),
      api.get(endpoints.feeInvoices),
      api.get(endpoints.feePayments),
      api.get(endpoints.students),
      api.get(endpoints.academicYears),
      api.get(endpoints.programs),
    ])
    setStructures(structuresRes.data)
    setInvoices(invoicesRes.data)
    setPayments(paymentsRes.data)
    setStudents(studentsRes.data)
    setAcademicYears(yearsRes.data)
    setPrograms(programsRes.data)
  }

  useEffect(() => {
    loadData()
  }, [])

  const submitStructure = async (event) => {
    event.preventDefault()
    await api.post(endpoints.feeStructures, { ...structureForm, amount: Number(structureForm.amount), due_days: Number(structureForm.due_days), academic_year: Number(structureForm.academic_year), program: Number(structureForm.program) })
    setStructureForm({ name: "", amount: "", due_days: 30, academic_year: "", program: "" })
    loadData()
  }

  const submitInvoice = async (event) => {
    event.preventDefault()
    await api.post(endpoints.feeInvoices, { ...invoiceForm, student: Number(invoiceForm.student), fee_structure: Number(invoiceForm.fee_structure), amount: Number(invoiceForm.amount) })
    setInvoiceForm({ student: "", fee_structure: "", amount: "", due_date: "" })
    loadData()
  }

  const submitPayment = async (event) => {
    event.preventDefault()
    await api.post(endpoints.feePayments, { ...paymentForm, invoice: Number(paymentForm.invoice), amount: Number(paymentForm.amount) })
    setPaymentForm({ invoice: "", amount: "", payment_date: "", reference_number: "", mode: "cash" })
    loadData()
  }

  return (
    <div className="stack-lg">
      <section className="three-column">
        <div className="panel">
          <div className="panel-header"><h3>Fee Structure</h3></div>
          <form className="form-grid" onSubmit={submitStructure}>
            <label>Name<input value={structureForm.name} onChange={(e) => setStructureForm({ ...structureForm, name: e.target.value })} required /></label>
            <label>Amount<input type="number" step="0.01" value={structureForm.amount} onChange={(e) => setStructureForm({ ...structureForm, amount: e.target.value })} required /></label>
            <label>Due Days<input type="number" value={structureForm.due_days} onChange={(e) => setStructureForm({ ...structureForm, due_days: e.target.value })} required /></label>
            <label>Academic Year<select value={structureForm.academic_year} onChange={(e) => setStructureForm({ ...structureForm, academic_year: e.target.value })} required><option value="">Select</option>{academicYears.map((year) => <option key={year.id} value={year.id}>{year.name}</option>)}</select></label>
            <label>Program<select value={structureForm.program} onChange={(e) => setStructureForm({ ...structureForm, program: e.target.value })} required><option value="">Select</option>{programs.map((program) => <option key={program.id} value={program.id}>{program.name}</option>)}</select></label>
            <button className="button" type="submit">Save Structure</button>
          </form>
        </div>
        <div className="panel">
          <div className="panel-header"><h3>Generate Invoice</h3></div>
          <form className="form-grid" onSubmit={submitInvoice}>
            <label>Student<select value={invoiceForm.student} onChange={(e) => setInvoiceForm({ ...invoiceForm, student: e.target.value })} required><option value="">Select</option>{students.map((student) => <option key={student.id} value={student.id}>{student.name}</option>)}</select></label>
            <label>Fee Structure<select value={invoiceForm.fee_structure} onChange={(e) => setInvoiceForm({ ...invoiceForm, fee_structure: e.target.value, amount: structures.find((item) => String(item.id) === e.target.value)?.amount || "" })} required><option value="">Select</option>{structures.map((structure) => <option key={structure.id} value={structure.id}>{structure.name}</option>)}</select></label>
            <label>Amount<input type="number" step="0.01" value={invoiceForm.amount} onChange={(e) => setInvoiceForm({ ...invoiceForm, amount: e.target.value })} required /></label>
            <button className="button" type="submit">Create Invoice</button>
          </form>
        </div>
        <div className="panel">
          <div className="panel-header"><h3>Record Payment</h3></div>
          <form className="form-grid" onSubmit={submitPayment}>
            <label>Invoice<select value={paymentForm.invoice} onChange={(e) => setPaymentForm({ ...paymentForm, invoice: e.target.value })} required><option value="">Select</option>{invoices.map((invoice) => <option key={invoice.id} value={invoice.id}>{invoice.student_name} - {invoice.fee_structure_name}</option>)}</select></label>
            <label>Amount<input type="number" step="0.01" value={paymentForm.amount} onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })} required /></label>
            <label>Payment Date<input type="date" value={paymentForm.payment_date} onChange={(e) => setPaymentForm({ ...paymentForm, payment_date: e.target.value })} required /></label>
            <label>Reference<input value={paymentForm.reference_number} onChange={(e) => setPaymentForm({ ...paymentForm, reference_number: e.target.value })} /></label>
            <label>Mode<select value={paymentForm.mode} onChange={(e) => setPaymentForm({ ...paymentForm, mode: e.target.value })}><option value="cash">Cash</option><option value="upi">UPI</option><option value="bank">Bank</option></select></label>
            <button className="button button-secondary" type="submit">Save Payment</button>
          </form>
        </div>
      </section>
      <section className="two-column">
        <div className="panel">
          <div className="panel-header"><h3>Invoices</h3></div>
          <table className="data-table">
            <thead><tr><th>Student</th><th>Structure</th><th>Amount</th><th>Paid</th><th>Status</th></tr></thead>
            <tbody>{invoices.map((invoice) => <tr key={invoice.id}><td>{invoice.student_name}</td><td>{invoice.fee_structure_name}</td><td>{invoice.amount}</td><td>{invoice.amount_paid}</td><td>{invoice.status}</td></tr>)}</tbody>
          </table>
        </div>
        <div className="panel">
          <div className="panel-header"><h3>Payments</h3></div>
          <table className="data-table">
            <thead><tr><th>Student</th><th>Amount</th><th>Date</th><th>Mode</th></tr></thead>
            <tbody>{payments.map((payment) => <tr key={payment.id}><td>{payment.invoice_student_name}</td><td>{payment.amount}</td><td>{payment.payment_date}</td><td>{payment.mode}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

export default Fees
