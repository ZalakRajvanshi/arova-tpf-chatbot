import { useNavigate } from "react-router-dom";

export default function SessionDoneModal({ open, onClose, senderName }) {
  const navigate = useNavigate();
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-zinc-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-slide-up">
        {/* Hero */}
        <div className="bg-gradient-to-br from-emerald-500 to-teal-600 px-6 pt-7 pb-6 text-white text-center">
          <div className="w-14 h-14 mx-auto mb-3 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 6L9 17l-5-5" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold">Conversation complete</h2>
          <p className="text-sm text-emerald-50/90 mt-1">
            You wrapped up today's session with {senderName || "the candidate"}.
          </p>
        </div>

        {/* Body */}
        <div className="px-6 py-5">
          <p className="text-sm text-zinc-600 dark:text-zinc-400 text-center leading-relaxed">
            That's all for today. Come back tomorrow for a fresh scenario.
            <br />
            <span className="text-zinc-500 dark:text-zinc-500">
              You can review this conversation anytime in History.
            </span>
          </p>

          <div className="flex gap-2 mt-5">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2.5 rounded-lg border border-zinc-200 dark:border-zinc-700 text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition"
            >
              Stay here
            </button>
            <button
              onClick={() => navigate("/home")}
              className="flex-1 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold transition shadow-sm"
            >
              Go to Home →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
