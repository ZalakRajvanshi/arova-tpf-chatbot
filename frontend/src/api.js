import axios from "axios";

// In dev, VITE_API_URL is undefined → falls back to "/api" which the Vite proxy
// forwards to http://127.0.0.1:8000.
// In prod (Vercel), set VITE_API_URL=https://your-render-backend.onrender.com
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.clear();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export const auth = {
  login: async (email, password) => {
    const { data } = await api.post("/auth/login", { email, password });
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user", JSON.stringify({
      id: data.user_id,
      name: data.name,
      role: data.role,
    }));
    return data;
  },
  logout: () => {
    localStorage.clear();
    window.location.href = "/login";
  },
  user: () => {
    const u = localStorage.getItem("user");
    return u ? JSON.parse(u) : null;
  },
  isLoggedIn: () => !!localStorage.getItem("token"),
};

export default api;
