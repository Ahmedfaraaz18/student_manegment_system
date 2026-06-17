import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts"

export default function AttendanceChart({ data = [] }) {
  const chartData = data.length
    ? data
    : [
        { day: "Mon", attendance: 92 },
        { day: "Tue", attendance: 88 },
      ]

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="day" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="attendance" stroke="#22c55e" strokeWidth={3} />
      </LineChart>
    </ResponsiveContainer>
  )
}
