import axios from "axios";
import { message } from "antd";

const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.detail || error.message || "请求失败";
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
      message.error("登录已过期，请重新登录");
    } else {
      message.error(msg);
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  login: (data) => api.post("/auth/login", data),
  register: (data) => api.post("/auth/register", data),
  changePassword: (data) => api.put("/auth/password", data),
};

// Users
export const userAPI = {
  getMe: () => api.get("/users/me"),
  updateMe: (data) => api.put("/users/me", data),
  list: (params) => api.get("/users/list", { params }),
  get: (id) => api.get(`/users/${id}`),
  toggleStatus: (id) => api.put(`/users/${id}/toggle-status`),
};

// Patients
export const patientAPI = {
  getProfile: () => api.get("/patients/profile"),
  updateProfile: (data) => api.put("/patients/profile", data),
  list: (params) => api.get("/patients/list", { params }),
};

// Doctors
export const doctorAPI = {
  getProfile: () => api.get("/doctors/profile"),
  updateProfile: (data) => api.put("/doctors/profile", data),
  register: (data) => api.post("/doctors/register", data),
  list: (params) => api.get("/doctors/list", { params }),
  get: (id) => api.get(`/doctors/${id}`),
  approve: (id) => api.put(`/doctors/${id}/approve`),
};

// Departments
export const departmentAPI = {
  list: () => api.get("/departments/list"),
  get: (id) => api.get(`/departments/${id}`),
};

// Appointments
export const appointmentAPI = {
  create: (data) => api.post("/appointments/create", data),
  getMy: (params) => api.get("/appointments/my", { params }),
  getDoctor: (params) => api.get("/appointments/doctor", { params }),
  cancel: (id, reason) => api.put(`/appointments/${id}/cancel`, null, { params: { reason } }),
  updateStatus: (id, data) => api.put(`/appointments/${id}/status`, data),
};

// AI Diagnosis & Chat
export const aiAPI = {
  diagnose: (data) => api.post("/ai/diagnose", data),
  getHistory: (params) => api.get("/ai/history", { params }),
  // AI Chat sessions
  createChatSession: (data) => api.post("/ai/chat/sessions", data),
  getChatSessions: () => api.get("/ai/chat/sessions"),
  deleteChatSession: (sessionId) => api.delete(`/ai/chat/sessions/${sessionId}`),
  // AI Chat messages
  getChatMessages: (sessionId) => api.get(`/ai/chat/sessions/${sessionId}/messages`),
  sendChatMessage: (sessionId, content) => api.post(`/ai/chat/sessions/${sessionId}/messages`, { content }),
};

// Diagnosis Records
export const diagnosisAPI = {
  create: (data) => api.post("/diagnosis/create", data),
  getMy: (params) => api.get("/diagnosis/my", { params }),
  getDoctor: (params) => api.get("/diagnosis/doctor", { params }),
  get: (id) => api.get(`/diagnosis/${id}`),
};

// Prescriptions
export const prescriptionAPI = {
  create: (data) => api.post("/prescriptions/create", data),
  getByRecord: (recordId) => api.get(`/prescriptions/record/${recordId}`),
};


// Admin
export const adminAPI = {
  getStats: () => api.get("/admin/stats"),
  getRecentActivities: () => api.get("/admin/recent-activities"),
};

// Medicines
export const medicineAPI = {
  list: (params) => api.get("/medicines/list", { params }),
};

export default api;



