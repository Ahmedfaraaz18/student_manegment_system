import { useState } from "react"
import { createStudent } from "../services/studentService"

export default function AddStudentForm({reload}){

const [name,setName] = useState("")
const [reg,setReg] = useState("")

const submit = async () => {
const [firstName, ...rest] = name.trim().split(" ")
const lastName = rest.join(" ")

await createStudent({
  first_name:firstName || name,
  last_name:lastName,
  register_number:reg
})

reload()

}

return(

<div className="bg-white p-6 shadow rounded mb-6">

<h2 className="font-semibold mb-4">
Add Student
</h2>

<input
placeholder="Name"
className="border p-2 mr-3"
onChange={(e)=>setName(e.target.value)}
/>

<input
placeholder="Register Number"
className="border p-2 mr-3"
onChange={(e)=>setReg(e.target.value)}
/>

<button
onClick={submit}
className="bg-blue-600 text-white px-4 py-2 rounded"
>
Add
</button>

</div>

)

}
