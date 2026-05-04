import { Navigate } from "react-router-dom";
import { auth } from "../api";

export default function ProtectedRoute({ children, adminOnly = false }) {
  if (!auth.isLoggedIn()) return <Navigate to="/login" replace />;
  const user = auth.user();
  if (adminOnly && user?.role !== "admin") return <Navigate to="/home" replace />;
  return children;
}
