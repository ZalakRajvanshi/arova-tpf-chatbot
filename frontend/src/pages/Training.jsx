import { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import ChatBubble from "../components/ChatBubble";
import Header from "../components/Header";
import SessionDoneModal from "../components/SessionDoneModal";

export default function Training() {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showDoneModal, setShowDoneModal] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => { loadSession(); }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, sending]);

  // Auto-grow textarea up to a cap
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 180) + "px";
  }, [input]);

  const loadSession = async () => {
    try {
      const { data } = await api.get("/session/today");
      setSession(data);
      setMessages(data.messages || []);
    } catch {
      setError("Could not load today's scenario.");
    } finally {
      setLoading(false);
    }
  };

  const onPaste = (e) => {
    e.preventDefault();
    setError("Pasting is disabled. Please type your response.");
    setTimeout(() => setError(""), 2500);
  };

  const send = async () => {
    if (!input.trim() || sending || session?.status === "completed") return;
    setSending(true);
    setError("");
    const text = input.trim();
    const userMsg = { id: `u-${Date.now()}`, role: "user", content: text, sequence_num: messages.length + 1 };
    setMessages((p) => [...p, userMsg]);
    setInput("");

    try {
      const { data } = await api.post("/session/message", { content: text });
      setMessages((p) => [...p, { id: `a-${Date.now()}`, role: "ai", content: data.ai_reply, sequence_num: messages.length + 2 }]);
      if (data.session_status === "completed") {
        setSession((s) => ({ ...s, status: "completed" }));
        // Show the modal after a small delay so the user sees the AI's closing message first
        setTimeout(() => setShowDoneModal(true), 1400);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Could not send message.");
      setMessages((p) => p.slice(0, -1));
      setInput(text);
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="h-screen flex flex-col overflow-hidden">
        <Header />
        <div className="flex-1 flex items-center justify-center text-zinc-400 text-sm">
          Loading today's scenario...
        </div>
      </div>
    );
  }

  const scenario = session?.scenario;
  const isCompleted = session?.status === "completed";
  const initials = scenario?.sender_name?.[0]?.toUpperCase() || "?";

  return (
    <div className="h-screen flex flex-col overflow-hidden">
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

      {/* Single scrollable area: scenario + chat together */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-4 sm:py-6">
          {/* Scenario card — scrolls with content */}
          <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-4 sm:p-5 shadow-sm mb-5 sm:mb-6 animate-fade-in">
            <div className="flex items-start gap-3 mb-3">
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-pink-500 to-orange-500 flex items-center justify-center text-white font-semibold flex-shrink-0">
                {initials}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-zinc-900 dark:text-zinc-100">{scenario?.sender_name}</div>
                <div className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5 flex flex-wrap items-center gap-1.5">
                  <span>{scenario?.role_applied}</span>
                  <span className="opacity-50">·</span>
                  <span className="px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-medium">
                    {scenario?.company_name}
                  </span>
                </div>
              </div>
            </div>
            <p className="text-[14px] leading-relaxed text-zinc-700 dark:text-zinc-300">{scenario?.message}</p>
          </div>

          {/* Chat */}
          {messages.length === 0 && !sending && (
            <div className="text-center text-sm text-zinc-400 dark:text-zinc-600 py-8">
              Type your response below to begin.
            </div>
          )}
          {messages.map((m) => (
            <ChatBubble
              key={m.id}
              role={m.role}
              content={m.content}
              senderName={m.role === "ai" ? scenario?.sender_name : null}
            />
          ))}
          {sending && (
            <div className="flex justify-start mb-4 animate-fade-in">
              <div className="bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-zinc-400 dark:bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-1.5 h-1.5 bg-zinc-400 dark:bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-1.5 h-1.5 bg-zinc-400 dark:bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input — WhatsApp-style, integrated, doesn't push the page */}
      <div className="bg-zinc-50 dark:bg-zinc-950 border-t border-zinc-200 dark:border-zinc-800 flex-shrink-0">
        <div className="max-w-3xl mx-auto px-3 sm:px-4 py-2.5 sm:py-3">
          {error && (
            <div className="text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/40 px-3 py-1.5 rounded-md mb-2 animate-fade-in">
              {error}
            </div>
          )}

          {isCompleted ? (
            <div className="text-center py-3">
              <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">That's all for today.</div>
              <div className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                Come back tomorrow for a new scenario.{" "}
                <Link to="/home" className="text-indigo-600 dark:text-indigo-400 font-medium">Go home →</Link>
              </div>
            </div>
          ) : (
            <div className="flex items-end gap-2">
              <div className="flex-1 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-3xl px-4 py-2.5 focus-within:border-indigo-400 dark:focus-within:border-indigo-500 transition">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onPaste={onPaste}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      send();
                    }
                  }}
                  rows={1}
                  placeholder="Type your reply..."
                  style={{ minHeight: "24px", maxHeight: "180px" }}
                  className="w-full bg-transparent text-sm resize-none focus:outline-none leading-relaxed overflow-y-auto placeholder-zinc-400 dark:placeholder-zinc-500"
                  disabled={sending}
                />
              </div>
              <button
                onClick={send}
                disabled={sending || !input.trim()}
                aria-label="Send"
                className="w-11 h-11 flex items-center justify-center bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white rounded-full transition disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0 shadow-sm"
              >
                <SendIcon />
              </button>
            </div>
          )}
        </div>
      </div>

      <SessionDoneModal
        open={showDoneModal}
        onClose={() => setShowDoneModal(false)}
        senderName={scenario?.sender_name}
      />
    </div>
  );
}

function SendIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 2L11 13" />
      <path d="M22 2L15 22L11 13L2 9L22 2Z" />
    </svg>
  );
}
