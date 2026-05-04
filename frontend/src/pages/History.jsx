import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import Header from "../components/Header";
import ChatBubble from "../components/ChatBubble";

export default function History() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openId, setOpenId] = useState(null);

  useEffect(() => {
    api.get("/me/history")
      .then(({ data }) => setSessions(data))
      .finally(() => setLoading(false));
  }, []);

  const open = sessions.find((s) => s.id === openId);

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

      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 sm:py-8 animate-fade-in">
        <div className="mb-5 sm:mb-6">
          <h1 className="text-xl sm:text-2xl font-semibold">Conversation history</h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
            Read-only archive. You can revisit past chats but can't continue them.
          </p>
        </div>

        {loading ? (
          <Card>Loading your history...</Card>
        ) : sessions.length === 0 ? (
          <Card>
            No conversations yet. Start today's scenario to build your history.
          </Card>
        ) : open ? (
          <ConversationView session={open} onBack={() => setOpenId(null)} />
        ) : (
          <ChatList sessions={sessions} onOpen={setOpenId} />
        )}
      </div>
    </div>
  );
}

function ChatList({ sessions, onOpen }) {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl overflow-hidden divide-y divide-zinc-100 dark:divide-zinc-800">
      {sessions.map((s) => (
        <button
          key={s.id}
          onClick={() => onOpen(s.id)}
          className="w-full flex items-center gap-3 px-4 py-3.5 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition text-left"
        >
          {/* Avatar */}
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-pink-500 to-orange-500 flex items-center justify-center text-white font-semibold flex-shrink-0">
            {s.scenario.sender_name?.[0]?.toUpperCase() || "?"}
          </div>

          {/* Body */}
          <div className="flex-1 min-w-0">
            <div className="flex items-baseline justify-between gap-2">
              <div className="text-sm font-semibold truncate">{s.scenario.sender_name}</div>
              <div className="text-[11px] text-zinc-500 dark:text-zinc-400 flex-shrink-0">
                {formatDate(s.date)}
              </div>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
              <span className="truncate">{s.scenario.role_applied}</span>
              <span className="opacity-50">·</span>
              <span className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-medium text-[10px]">
                {s.scenario.company_name}
              </span>
            </div>
            <div className="text-xs text-zinc-500 dark:text-zinc-400 truncate mt-1">
              {s.scenario.message}
            </div>
          </div>

          {/* Status pill */}
          <div className="flex-shrink-0">
            {s.status === "completed" ? (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 font-semibold border border-emerald-200 dark:border-emerald-900/50 uppercase tracking-wider">
                Done
              </span>
            ) : (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 font-semibold border border-amber-200 dark:border-amber-900/50 uppercase tracking-wider">
                In Progress
              </span>
            )}
          </div>
        </button>
      ))}
    </div>
  );
}

function ConversationView({ session, onBack }) {
  const sc = session.scenario;
  return (
    <div className="animate-fade-in">
      <button
        onClick={onBack}
        className="text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition mb-4"
      >
        ← Back to all conversations
      </button>

      {/* Scenario card */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 mb-5">
        <div className="flex items-start gap-3 mb-3">
          <div className="w-11 h-11 rounded-full bg-gradient-to-br from-pink-500 to-orange-500 flex items-center justify-center text-white font-semibold flex-shrink-0">
            {sc.sender_name?.[0]?.toUpperCase() || "?"}
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-zinc-900 dark:text-zinc-100">{sc.sender_name}</div>
            <div className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5 flex flex-wrap items-center gap-1.5">
              <span>{sc.role_applied}</span>
              <span className="opacity-50">·</span>
              <span className="px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-medium">
                {sc.company_name}
              </span>
              <span className="opacity-50">·</span>
              <span>{formatDate(session.date)}</span>
            </div>
          </div>
        </div>
        <p className="text-[14px] leading-relaxed text-zinc-700 dark:text-zinc-300">{sc.message}</p>
      </div>

      {/* Messages */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5">
        {session.messages.length === 0 ? (
          <div className="text-center text-sm text-zinc-400 py-6">No replies in this conversation.</div>
        ) : (
          session.messages.map((m, i) => (
            <ChatBubble
              key={i}
              role={m.role}
              content={m.content}
              senderName={m.role === "ai" ? sc.sender_name : null}
            />
          ))
        )}

        {session.status === "completed" && (
          <div className="text-center text-[11px] text-zinc-400 dark:text-zinc-500 mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800 uppercase tracking-wider font-semibold">
            Conversation ended
          </div>
        )}
      </div>
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

function formatDate(iso) {
  const d = new Date(iso);
  const today = new Date(); today.setHours(0,0,0,0);
  const yesterday = new Date(today); yesterday.setDate(today.getDate() - 1);
  const dDate = new Date(d); dDate.setHours(0,0,0,0);

  if (dDate.getTime() === today.getTime()) return "Today";
  if (dDate.getTime() === yesterday.getTime()) return "Yesterday";
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}
