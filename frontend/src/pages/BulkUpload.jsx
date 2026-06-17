import { useState } from "react";
import API from "../services/api";

export default function BulkUpload(){

  const [file,setFile] = useState(null);

  const upload = async () => {

    const formData = new FormData();

    formData.append("file",file);

    await API.post("/students/bulk-upload/",formData);

    alert("Students uploaded successfully");

  }

  return(

    <div>

      <h1 className="text-2xl font-bold mb-6">
        Bulk Student Upload
      </h1>

      <input
      type="file"
      onChange={(e)=>setFile(e.target.files[0])}
      className="mb-4"
      />

      <button
      onClick={upload}
      className="bg-blue-600 text-white px-4 py-2"
      >
      Upload Excel
      </button>

    </div>

  )

}
