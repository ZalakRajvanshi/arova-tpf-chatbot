import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { auth } from "../api";
import Header from "../components/Header";

export default function Profile() {
  const [me, setMe] = useState(null);
  const [name, setName] = useState("");
  const [savingName, setSavingName] = useState(false);
  const [nameMsg, setNameMsg] = useState("");

  useEffect(() => {
    api.get("/me").then(({ data }) => {
      setMe(data);
      setName(data.name);
    });
  }, []);

  const saveName = async (e) => {
    e.preventDefault();
    setSavingName(true);
    setNameMsg("");
    try {
      const { data } = await api.patch("/me", { name });
      setMe(data);
      const u = auth.user();
      localStorage.setItem("user", JSON.stringify({ ...u, name: data.name }));
      setNameMsg("Name updated");
      setTimeout(() => setNameMsg(""), 2500);
    } catch (err) {
      setNameMsg(err.response?.data?.detail || "Could not save");
    } finally {
      setSavingName(false);
    }
  };

  const stats = me?.stats;

  return (
    <div className="min-h-full">
      <Header
        left={
          <Link
            to="/home"
            className="text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition flex items-center gap-1.5 ml-2"
          >
            ← Home
          </Link>
        }
      />
      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-6 sm:py-10 animate-fade-in">
        {/* Header card */}
        <div className="flex items-center gap-4 sm:gap-5 mb-6 sm:mb-8">
          <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-white flex items-center justify-center text-xl sm:text-2xl font-semibold flex-shrink-0">
            {(me?.name || "?")[0].toUpperCase()}
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-semibold truncate">{me?.name || "—"}</h1>
            <div className="text-sm text-zinc-500 dark:text-zinc-400 truncate">{me?.email}</div>
          </div>
        </div>

        {/* Personal stats */}
        {stats && (
          <div className="grid grid-cols-3 gap-2 sm:gap-3 mb-6 sm:mb-8">
            <Mini label="Streak" value={stats.streak} suffix={stats.streak === 1 ? "day" : "days"} />
            <Mini label="Sessions" value={stats.completed_sessions} suffix="done" />
            <Mini label="Total" value={stats.total_sessions} suffix="started" />
          </div>
        )}

        {/* Display name */}
        <Section title="Display name">
          <form onSubmit={saveName} className="space-y-3">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-3.5 py-2.5 rounded-lg bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
            />
            <div className="flex items-center justify-between">
              <span className="text-xs text-emerald-600 dark:text-emerald-400">{nameMsg}</span>
              <button
                type="submit"
                disabled={savingName || !name.trim() || name === me?.name}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm rounded-lg font-medium disabled:opacity-50 transition"
              >
                {savingName ? "Saving..." : "Save"}
              </button>
            </div>
          </form>
        </Section>

        {/* Account & security */}
        <Section title="Account & Security">
          <div className="space-y-3">
            <Row label="Email" value={me?.email} note="Email is managed by your admin." />
            <Row
              label="Password"
              value="••••••••"
              note={
                <>
                  Forgot your password? Sign out and use{" "}
                  <a
                    href="/forgot-password"
                    className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline"
                  >
                    Forgot password
                  </a>{" "}
                  on the login page.
                </>
              }
            />
          </div>
        </Section>

        {/* Sign out */}
        <button
          onClick={auth.logout}
          className="mt-2 w-full sm:w-auto px-5 py-2.5 rounded-lg border border-red-200 dark:border-red-900/50 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 text-sm font-medium transition"
        >
          Sign out
        </button>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 mb-4">
      <div className="text-[11px] font-semibold tracking-wider text-zinc-500 dark:text-zinc-400 uppercase mb-3">
        {title}
      </div>
      {children}
    </div>
  );
}

function Row({ label, value, note }) {
  return (
    <div>
      <div className="flex items-baseline justify-between gap-3">
        <div className="text-xs font-medium text-zinc-700 dark:text-zinc-300">{label}</div>
        <div className="text-sm text-zinc-900 dark:text-zinc-100 font-mono">{value}</div>
      </div>
      {note && <div className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">{note}</div>}
    </div>
  );
}

function Mini({ label, value, suffix }) {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-3 sm:p-4">
      <div className="text-[10px] sm:text-[11px] font-semibold tracking-wider text-zinc-500 dark:text-zinc-400 uppercase mb-1">
        {label}
      </div>
      <div className="text-lg sm:text-xl font-semibold">
        {value} <span className="text-[10px] sm:text-xs text-zinc-500 dark:text-zinc-400 font-normal">{suffix}</span>
      </div>
    </div>
  );
}
