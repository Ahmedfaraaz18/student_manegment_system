import { useState } from "react";
import API from "../services/api";

export default function Timetable(){

  const [department,setDepartment] = useState("");

  const generate = async () => {

    await API.post("/timetable/generate/",{
      department
    });

    alert("Timetable generated");

  }

  return(

    <div>

      <h1 className="text-2xl font-bold mb-6">
        Timetable Generator
      </h1>

      <input
      placeholder="Department ID"
      className="border p-2 mb-4"
      onChange={(e)=>setDepartment(e.target.value)}
      />

      <button
      onClick={generate}
      className="bg-blue-600 text-white px-4 py-2"
      >
      Generate Timetable
      </button>

    </div>

  )

}
