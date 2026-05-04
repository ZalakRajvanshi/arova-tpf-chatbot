import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import api, { auth } from "../api";
import Header from "../components/Header";

export default function Home() {
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(true);
  const user = auth.user();
  const greeting = greet();

  const fetchMe = useCallback(() => {
    api.get("/me").then(({ data }) => setMe(data)).finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchMe(); }, [fetchMe]);

  // Refresh stats when the user comes back to this tab
  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === "visible") fetchMe();
    };
    document.addEventListener("visibilitychange", onVisible);
    window.addEventListener("focus", fetchMe);
    return () => {
      document.removeEventListener("visibilitychange", onVisible);
      window.removeEventListener("focus", fetchMe);
    };
  }, [fetchMe]);

  const stats = me?.stats;
  const sessionDone = stats?.completed_today;
  const sessionInProgress = !sessionDone && stats?.has_active_session_today;
  const sessionNew = !sessionDone && !sessionInProgress;

  // Status label for the third stat card
  const statusLabel = sessionDone ? "Done" : sessionInProgress ? "In Progress" : "Pending";
  const statusAccent = sessionDone ? "emerald" : sessionInProgress ? "amber" : "default";

  // Subtitle text
  const subtitle = sessionDone
    ? "You're done for today. See you tomorrow."
    : sessionInProgress
    ? "You have a conversation in progress. Pick up where you left off."
    : "Today's scenario is waiting for you.";

  // CTA card content varies by state
  const cardLabel = sessionDone
    ? "TODAY'S CONVERSATION"
    : sessionInProgress
    ? "PICK UP WHERE YOU LEFT OFF"
    : "READY WHEN YOU ARE";

  const cardTitle = sessionDone
    ? "You crushed today's scenario."
    : sessionInProgress
    ? "Your conversation is waiting."
    : "One scenario. A few minutes.";

  const cardBody = sessionDone
    ? "Come back tomorrow for a new conversation."
    : sessionInProgress
    ? "You started but haven't finished. Continue the chat to wrap it up."
    : "Type your reply to a real candidate. The AI will respond as them and evaluate your tone, clarity, and care.";

  const ctaText = sessionDone
    ? "Review today's conversation →"
    : sessionInProgress
    ? "Continue conversation →"
    : "Start today's conversation →";

  return (
    <div className="min-h-full">
      <Header />
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 sm:py-12 animate-fade-in">
        {/* Greeting */}
        <div className="mb-8 sm:mb-10">
          <div className="text-xs font-semibold tracking-wide text-indigo-600 dark:text-indigo-400 mb-1">
            {today()}
          </div>
          <h1 className="text-2xl sm:text-3xl font-semibold">
            {greeting}, {user?.name?.split(" ")[0] || "there"}.
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">{subtitle}</p>
        </div>

        {/* Stat cards */}
        {!loading && (
          <div className="grid grid-cols-3 gap-2 sm:gap-3 mb-6 sm:mb-8">
            <StatCard label="Streak" value={stats?.streak ?? 0} suffix={stats?.streak === 1 ? "day" : "days"} icon="🔥" />
            <StatCard label="Sessions" value={stats?.completed_sessions ?? 0} suffix="completed" />
            <StatCard label="Status" value={statusLabel} accent={statusAccent} />
          </div>
        )}

        {/* Big action card */}
        <div className="bg-gradient-to-br from-indigo-600 to-violet-700 rounded-2xl p-6 sm:p-8 text-white relative overflow-hidden shadow-xl">
          <div className="absolute -top-10 -right-10 w-48 h-48 bg-white/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="relative">
            <div className="text-xs font-semibold tracking-wider opacity-80 mb-2">{cardLabel}</div>
            <h2 className="text-xl sm:text-2xl font-semibold mb-2">{cardTitle}</h2>
            <p className="text-sm text-indigo-100/90 mb-5 sm:mb-6 max-w-md">{cardBody}</p>
            {sessionDone ? (
              <Link
                to="/training"
                className="inline-flex items-center gap-2 bg-white/15 hover:bg-white/25 backdrop-blur-sm text-white text-sm font-medium px-5 py-2.5 rounded-lg transition"
              >
                {ctaText}
              </Link>
            ) : (
              <Link
                to="/training"
                className="inline-flex items-center gap-2 bg-white text-indigo-700 hover:bg-indigo-50 text-sm font-semibold px-6 py-3 rounded-lg shadow-md transition"
              >
                {ctaText}
              </Link>
            )}
          </div>
        </div>

        {/* History link */}
        <Link
          to="/history"
          className="mt-6 flex items-center justify-between gap-3 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 hover:border-zinc-300 dark:hover:border-zinc-700 transition group"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-600 dark:text-zinc-400">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-semibold">Past conversations</div>
              <div className="text-xs text-zinc-500 dark:text-zinc-400">Revisit your previous chats</div>
            </div>
          </div>
          <span className="text-zinc-400 dark:text-zinc-500 group-hover:text-zinc-700 dark:group-hover:text-zinc-300 transition">→</span>
        </Link>

        {/* Tip */}
        <div className="mt-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-5">
          <div className="text-xs font-semibold tracking-wider text-zinc-500 dark:text-zinc-400 mb-2">REMINDER</div>
          <p className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">
            <strong>Acknowledge before you act.</strong> A candidate who feels heard will accept "I'll get back to you" — one who doesn't, won't.
          </p>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, suffix, icon, accent }) {
  const accentClass =
    accent === "emerald" ? "text-emerald-600 dark:text-emerald-400" :
    accent === "amber"   ? "text-amber-600 dark:text-amber-400" :
    "";
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-3 sm:p-4">
      <div className="text-[10px] sm:text-[11px] font-semibold tracking-wider text-zinc-500 dark:text-zinc-400 uppercase mb-1 sm:mb-1.5">
        {label}
      </div>
      <div className="flex items-baseline flex-wrap gap-1 sm:gap-1.5">
        {icon && <span className="text-sm sm:text-base">{icon}</span>}
        <span className={`text-lg sm:text-xl font-semibold ${accentClass}`}>{value}</span>
        {suffix && <span className="text-[10px] sm:text-xs text-zinc-500 dark:text-zinc-400">{suffix}</span>}
      </div>
    </div>
  );
}

function greet() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

function today() {
  return new Date().toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });
}
