import axios from "axios";

// Создаем экземпляр axios
const api = axios.create({
  baseURL: process.env.REACT_APP_API_GATEWAY_URL || "http://localhost",
});

// Устанавливаем токен динамически при каждом запросе
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
