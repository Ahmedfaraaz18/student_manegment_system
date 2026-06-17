import DepartmentChart from "./charts/DepartmentChart"
import AttendanceChart from "./charts/AttendanceChart"
import PlacementChart from "./charts/PlacementChart"

export default function Charts({
  departmentData = [],
  attendanceData = [],
  placementData = [],
}) {
  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 shadow rounded-xl">
          <h2 className="font-semibold mb-4">Department Distribution</h2>
          <DepartmentChart data={departmentData} />
        </div>

        <div className="bg-white p-6 shadow rounded-xl">
          <h2 className="font-semibold mb-4">Placement Overview</h2>
          <PlacementChart data={placementData} />
        </div>
      </div>

      <div className="bg-white p-6 shadow rounded-xl mt-6">
        <h2 className="font-semibold mb-4">Attendance Trend</h2>
        <AttendanceChart data={attendanceData} />
      </div>
    </>
  )
}
