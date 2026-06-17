import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { Spin } from "antd";
import Login from "./pages/Login";
import Register from "./pages/Register";
import AdminDashboard from "./pages/Admin/Dashboard";
import UserManage from "./pages/Admin/UserManage";
import DoctorApproval from "./pages/Admin/DoctorApproval";
import AdminSettings from "./pages/Admin/Settings";
import DoctorWorkbench from "./pages/Doctor/Workbench";
import DoctorAppointmentList from "./pages/Doctor/AppointmentList";
import DoctorRecords from "./pages/Doctor/DoctorRecords";
import PatientAppointment from "./pages/Patient/Appointment";
import PatientMyAppointments from "./pages/Patient/MyAppointments";
import PatientMyRecords from "./pages/Patient/MyRecords";
import AIDiagnosisPage from "./pages/AIDiagnosis";
import MainLayout from "./components/MainLayout";

function PrivateRoute({ children, roles }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;
  return children;
}

function HomeRedirect() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  switch (user.role) {
    case "admin": return <Navigate to="/admin" replace />;
    case "doctor": return <Navigate to="/doctor" replace />;
    case "patient": return <Navigate to="/patient/appointments" replace />;
    default: return <Navigate to="/login" replace />;
  }
}

function AdminRoutes() {
  return (
    <MainLayout>
      <Routes>
        <Route index element={<AdminDashboard />} />
        <Route path="users" element={<UserManage />} />
        <Route path="doctors" element={<DoctorApproval />} />
        <Route path="settings" element={<AdminSettings />} />
        <Route path="*" element={<Navigate to="/admin" replace />} />
      </Routes>
    </MainLayout>
  );
}

function DoctorRoutes() {
  return (
    <MainLayout>
      <Routes>
        <Route index element={<DoctorWorkbench />} />
        <Route path="appointments" element={<DoctorAppointmentList />} />
        <Route path="records" element={<DoctorRecords />} />
        <Route path="*" element={<Navigate to="/doctor" replace />} />
      </Routes>
    </MainLayout>
  );
}

function PatientRoutes() {
  return (
    <MainLayout>
      <Routes>
        <Route path="appointments" element={<PatientAppointment />} />
        <Route path="my-appointments" element={<PatientMyAppointments />} />
        <Route path="ai" element={<AIDiagnosisPage />} />
        <Route path="records" element={<PatientMyRecords />} />
        <Route path="*" element={<Navigate to="appointments" replace />} />
      </Routes>
    </MainLayout>
  );
}

export default function App() {
  const { user, loading } = useAuth();
  if (loading) return <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}><Spin size="large" /></div>;
  return (
    <Routes>
      <Route path="/login" element={user ? <HomeRedirect /> : <Login />} />
      <Route path="/register" element={user ? <HomeRedirect /> : <Register />} />
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/admin/*" element={<PrivateRoute roles={["admin"]}><AdminRoutes /></PrivateRoute>} />
      <Route path="/doctor/*" element={<PrivateRoute roles={["doctor"]}><DoctorRoutes /></PrivateRoute>} />
      <Route path="/patient/*" element={<PrivateRoute roles={["patient"]}><PatientRoutes /></PrivateRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
