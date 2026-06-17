import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
} from "chart.js";

import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
);

function Analytics() {

  const data = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May"],
    datasets: [
      {
        label: "Student Growth",
        data: [10, 30, 50, 80, 120],
        borderColor: "blue",
        tension: 0.4
      }
    ]
  };

  return (
    <div className="bg-white p-6 rounded shadow mt-10">
      <h2 className="text-xl font-bold mb-4">Student Growth</h2>
      <Line data={data} />
    </div>
  );
}

export default Analytics;