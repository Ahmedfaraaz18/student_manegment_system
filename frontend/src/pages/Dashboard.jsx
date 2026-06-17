import StatsCard from "../components/StatsCard"
import DepartmentChart from "../components/charts/DepartmentChart"
import PlacementChart from "../components/charts/PlacementChart"
import AttendanceChart from "../components/charts/AttendanceChart"

export default function Dashboard(){

return(

<div>

<h1 className="text-2xl font-bold mb-6">
Dashboard
</h1>

{/* CARDS */}

<div className="grid grid-cols-4 gap-6 mb-8">

<StatsCard title="Students" value="120"/>
<StatsCard title="Teachers" value="20"/>
<StatsCard title="Departments" value="4"/>
<StatsCard title="Subjects" value="35"/>

</div>

{/* CHARTS */}

<div className="grid grid-cols-2 gap-6">

<div className="bg-white p-6 shadow rounded-xl">

<h2 className="font-semibold mb-4">
Department Distribution
</h2>

<DepartmentChart/>

</div>

<div className="bg-white p-6 shadow rounded-xl">

<h2 className="font-semibold mb-4">
Placement Overview
</h2>

<PlacementChart/>

</div>

</div>

{/* ATTENDANCE */}

<div className="bg-white p-6 shadow rounded-xl mt-6">

<h2 className="font-semibold mb-4">
Attendance Trend
</h2>

<AttendanceChart/>

</div>

</div>

)

}
