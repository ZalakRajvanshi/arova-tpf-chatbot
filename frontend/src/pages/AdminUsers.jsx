import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import Header from "../components/Header";
import AddEmployeeModal from "../components/AddEmployeeModal";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showAdd, setShowAdd] = useState(false);

  useEffect(() => { reload(); }, []);

  const reload = () => {
    setLoading(true);
    api.get("/admin/users")
      .then(({ data }) => setUsers(data))
      .finally(() => setLoading(false));
  };

  const filtered = useMemo(() => {
    if (!search.trim()) return users;
    const q = search.toLowerCase();
    return users.filter(
      (u) => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    );
  }, [users, search]);

  const totalSessions = users.reduce((acc, u) => acc + (u.total_sessions || 0), 0);
  const scored = users.filter((u) => u.avg_score != null);
  const overallAvg = scored.length > 0
    ? scored.reduce((acc, u) => acc + u.avg_score, 0) / scored.length
    : null;
  const activeUsers = users.filter((u) => u.last_active).length;

  return (
    <div className="min-h-full">
      <Header />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 animate-fade-in">
        {/* Stat cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-6 sm:mb-8">
          <StatCard label="Employees" value={users.length} />
          <StatCard label="Total Sessions" value={totalSessions} />
          <StatCard
            label="Average Score"
            value={overallAvg != null ? `${Math.round(overallAvg * 100)}%` : "—"}
            accent={overallAvg != null && overallAvg >= 0.75}
          />
        </div>

        {/* Toolbar */}
        <div className="flex items-center justify-between gap-3 mb-3">
          <h2 className="text-lg font-semibold">Employees</h2>
          <span className="text-xs text-zinc-500 dark:text-zinc-400">
            {users.length} total · {activeUsers} active
          </span>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 mb-4">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or email..."
            className="flex-1 px-3.5 py-2.5 rounded-lg bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
          />
          <button
            onClick={() => setShowAdd(true)}
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm rounded-lg font-medium transition flex items-center justify-center gap-1.5"
          >
            <span className="text-base leading-none">+</span> Add Employee
          </button>
        </div>

        {loading ? (
          <Card>Loading employees...</Card>
        ) : filtered.length === 0 ? (
          <Card>
            {search ? "No employees match your search." : "No employees yet. Click 'Add Employee' to get started."}
          </Card>
        ) : (
          <>
            {/* Mobile: card list */}
            <div className="sm:hidden space-y-2">
              {filtered.map((u) => (
                <Link
                  key={u.id}
                  to={`/admin/user/${u.id}`}
                  className="block bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 hover:border-zinc-300 dark:hover:border-zinc-700 active:bg-zinc-50 dark:active:bg-zinc-800/40 transition"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
                      {u.name?.[0]?.toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">{u.name}</div>
                      <div className="text-xs text-zinc-500 dark:text-zinc-400 truncate">{u.email}</div>
                    </div>
                    <span className="text-zinc-400 dark:text-zinc-500 text-sm flex-shrink-0">→</span>
                  </div>
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-xs text-zinc-500 dark:text-zinc-400">
                      {u.total_sessions} session{u.total_sessions === 1 ? "" : "s"}
                    </span>
                    <ScoreCell value={u.avg_score} />
                  </div>
                </Link>
              ))}
            </div>

            {/* Tablet/Desktop: table */}
            <div className="hidden sm:block bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-zinc-50 dark:bg-zinc-800/50 border-b border-zinc-200 dark:border-zinc-800">
                  <tr>
                    <Th>Employee</Th>
                    <Th>Sessions</Th>
                    <Th>Score</Th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((u, i) => (
                    <tr
                      key={u.id}
                      className={`hover:bg-zinc-50 dark:hover:bg-zinc-800/40 transition ${
                        i !== 0 ? "border-t border-zinc-100 dark:border-zinc-800" : ""
                      }`}
                    >
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-sm font-semibold">
                            {u.name?.[0]?.toUpperCase()}
                          </div>
                          <div>
                            <div className="text-sm font-medium">{u.name}</div>
                            <div className="text-xs text-zinc-500 dark:text-zinc-400">{u.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-sm text-zinc-700 dark:text-zinc-300">{u.total_sessions}</td>
                      <td className="px-5 py-3.5">
                        <ScoreCell value={u.avg_score} />
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <Link
                          to={`/admin/user/${u.id}`}
                          className="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition"
                        >
                          View →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      <AddEmployeeModal
        open={showAdd}
        onClose={() => setShowAdd(false)}
        onCreated={() => reload()}
      />
    </div>
  );
}

function Th({ children }) {
  return (
    <th className="text-left px-5 py-3 text-[11px] font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
      {children}
    </th>
  );
}

function ScoreCell({ value }) {
  if (value == null) return <span className="text-xs text-zinc-400">No data</span>;
  const color = value >= 0.75 ? "bg-emerald-500"
    : value >= 0.5 ? "bg-amber-500" : "bg-red-500";
  const text = value >= 0.75 ? "text-emerald-600 dark:text-emerald-400"
    : value >= 0.5 ? "text-amber-600 dark:text-amber-400" : "text-red-600 dark:text-red-400";
  return (
    <div className="flex items-center gap-2.5 max-w-[180px]">
      <div className="flex-1 h-1.5 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${value * 100}%` }} />
      </div>
      <span className={`text-xs font-semibold ${text} min-w-[36px] text-right`}>
        {Math.round(value * 100)}%
      </span>
    </div>
  );
}

function Card({ children }) {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-12 text-center text-zinc-500 dark:text-zinc-400 text-sm">
      {children}
    </div>
  );
}

function StatCard({ label, value, accent }) {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5">
      <div className="text-xs font-medium uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-2">{label}</div>
      <div className={`text-3xl font-semibold ${accent ? "text-emerald-600 dark:text-emerald-400" : ""}`}>{value}</div>
    </div>
  );
}
