import { useState,useEffect } from "react";
import API from "../services/api";

export default function Marks(){

  const [students,setStudents] = useState([]);
  const [marks,setMarks] = useState({});

  useEffect(()=>{

    API.get("/students/")
    .then(res => setStudents(res.data))

  },[])

  const updateMarks = (id,value)=>{

    setMarks({
      ...marks,
      [id]:value
    })

  }

  const submitMarks = async ()=>{

    await API.post("/results/",marks)

    alert("Marks saved")

  }

  return(

    <div>

      <h1 className="text-2xl font-bold mb-6">
        Marks Entry
      </h1>

      {students.map(student =>(

        <div
        key={student.id}
        className="flex justify-between border p-3 mb-2"
        >

          {student.first_name}

          <input
          type="number"
          className="border p-2"
          onChange={(e)=>updateMarks(student.id,e.target.value)}
          />

        </div>

      ))}

      <button
      onClick={submitMarks}
      className="bg-blue-600 text-white px-4 py-2 mt-4"
      >
      Save Marks
      </button>

    </div>

  )

}
