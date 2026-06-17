import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"

const COLORS = ["#2563eb", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"]

export default function DepartmentChart({ data = [] }) {
  const chartData = data.length
    ? data
    : [
        { name: "CSE", value: 120 },
        { name: "ECE", value: 90 },
      ]

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie data={chartData} dataKey="value" outerRadius={80} label>
          {chartData.map((entry, index) => (
            <Cell key={`${entry.name}-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}
