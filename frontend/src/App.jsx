import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Home from "./pages/Home";
import Training from "./pages/Training";
import Profile from "./pages/Profile";
import History from "./pages/History";
import AdminUsers from "./pages/AdminUsers";
import AdminUserProfile from "./pages/AdminUserProfile";
import ProtectedRoute from "./components/ProtectedRoute";
import { auth } from "./api";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password/:token" element={<ResetPassword />} />

      {/* Employee */}
      <Route path="/home" element={
        <ProtectedRoute><Home /></ProtectedRoute>
      } />
      <Route path="/training" element={
        <ProtectedRoute><Training /></ProtectedRoute>
      } />
      <Route path="/profile" element={
        <ProtectedRoute><Profile /></ProtectedRoute>
      } />
      <Route path="/history" element={
        <ProtectedRoute><History /></ProtectedRoute>
      } />

      {/* Admin */}
      <Route path="/admin" element={
        <ProtectedRoute adminOnly><AdminUsers /></ProtectedRoute>
      } />
      <Route path="/admin/user/:id" element={
        <ProtectedRoute adminOnly><AdminUserProfile /></ProtectedRoute>
      } />

      {/* Default redirect */}
      <Route path="/" element={
        <Navigate
          to={
            auth.isLoggedIn()
              ? auth.user()?.role === "admin" ? "/admin" : "/home"
              : "/login"
          }
          replace
        />
      } />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
