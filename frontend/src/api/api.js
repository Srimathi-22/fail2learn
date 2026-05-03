import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  timeout: 10000, // avoid hanging forever
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ Response interceptor
API.interceptors.response.use(
  (response) => {
    // Normalize response so frontend always gets usable data
    return response?.data ?? response;
  },
  (error) => {
    const message =
      error?.response?.data?.message ||
      error?.response?.data ||
      error.message ||
      "Something went wrong";

    console.error("🚨 API Error:", message);

    // Optional: you can return a safe fallback instead of crashing UI
    return Promise.reject({
      status: error?.response?.status,
      message,
      raw: error,
    });
  }
);

export default API;