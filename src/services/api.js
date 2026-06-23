import axios from "axios";

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV
    ? "http://127.0.0.1:8000/api"
    : "https://student-manegment-system-c380.onrender.com/api");

const API = axios.create({
  baseURL: apiBaseUrl,
});

export default API;
