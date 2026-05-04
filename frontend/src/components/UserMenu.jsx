import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { auth } from "../api";

export default function UserMenu() {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const user = auth.user();

  useEffect(() => {
    const onClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  if (!user) return null;
  const initial = user.name?.[0]?.toUpperCase() || "?";
  const isAdmin = user.role === "admin";

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-white text-sm font-semibold flex items-center justify-center hover:ring-2 hover:ring-indigo-300 dark:hover:ring-indigo-900 transition"
      >
        {initial}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-xl py-1.5 z-50 animate-fade-in">
          <div className="px-4 py-2.5 border-b border-zinc-100 dark:border-zinc-800">
            <div className="text-sm font-semibold truncate">{user.name}</div>
            <div className="text-xs text-zinc-500 dark:text-zinc-400 truncate">{user.email || (isAdmin ? "Admin" : "Employee")}</div>
          </div>
          <Link
            to={isAdmin ? "/admin" : "/home"}
            onClick={() => setOpen(false)}
            className="block px-4 py-2 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-800 transition"
          >
            {isAdmin ? "Dashboard" : "Home"}
          </Link>
          {!isAdmin && (
            <>
              <Link
                to="/history"
                onClick={() => setOpen(false)}
                className="block px-4 py-2 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-800 transition"
              >
                Chat history
              </Link>
              <Link
                to="/profile"
                onClick={() => setOpen(false)}
                className="block px-4 py-2 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-800 transition"
              >
                Profile settings
              </Link>
            </>
          )}
          <button
            onClick={auth.logout}
            className="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition"
          >
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}
