export default function ChatBubble({ role, content, senderName }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4 animate-slide-up`}>
      <div className="max-w-[78%]">
        {!isUser && senderName && (
          <div className="text-xs text-zinc-500 dark:text-zinc-400 mb-1.5 ml-3 font-medium">
            {senderName}
          </div>
        )}
        <div
          className={`px-4 py-2.5 rounded-2xl text-[14px] leading-relaxed whitespace-pre-wrap shadow-sm ${
            isUser
              ? "bg-indigo-600 text-white rounded-br-md"
              : "bg-white text-zinc-900 border border-zinc-200 rounded-bl-md dark:bg-zinc-800 dark:text-zinc-100 dark:border-zinc-700"
          }`}
        >
          {content}
        </div>
      </div>
    </div>
  );
}
