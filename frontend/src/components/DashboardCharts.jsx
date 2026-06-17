import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

export default function DashboardCharts() {

  const data = [
    { name: "CSE", students: 120 },
    { name: "ECE", students: 90 },
    { name: "MECH", students: 80 },
    { name: "CIVIL", students: 60 }
  ];

  return (

    <div className="bg-white p-6 rounded-xl shadow">

      <h2 className="text-lg font-semibold mb-4">
        Department Distribution
      </h2>

      <ResponsiveContainer width="100%" height={300}>

        <BarChart data={data}>

          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="name" />

          <YAxis />

          <Tooltip />

          <Bar dataKey="students" fill="#3b82f6" />

        </BarChart>

      </ResponsiveContainer>

    </div>

  );
}
