import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api",
  timeout: 120000,
});

export async function analyzeCsv(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/analyze", formData);
  return response.data;
}

export async function uploadCsv(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/upload", formData);
  return response.data;
}

export async function getAnalysisHistory() {
  const response = await api.get("/history");
  return response.data;
}

export default api;
