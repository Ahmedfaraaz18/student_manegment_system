import axios from "axios";

const defaultApiBaseUrl = import.meta.env.DEV
  ? "http://127.0.0.1:8000/api"
  : "https://student-manegment-system-c380.onrender.com/api";

const API = axios.create({
  baseURL: import.meta?.env?.VITE_API_BASE_URL || defaultApiBaseUrl,
});

export default API;
