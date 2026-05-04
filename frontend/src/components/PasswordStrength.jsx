/**
 * Live password-strength meter.
 * Scores 0-4 based on length + character variety.
 */
export default function PasswordStrength({ password }) {
  if (!password) return null;

  const score = scoreOf(password);
  const meta = LEVELS[score];

  return (
    <div className="mt-2 animate-fade-in">
      {/* Bar */}
      <div className="flex gap-1">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className={`flex-1 h-1 rounded-full transition-colors ${
              i <= score - 1 ? meta.barClass : "bg-zinc-200 dark:bg-zinc-800"
            }`}
          />
        ))}
      </div>
      {/* Label + tip */}
      <div className="flex items-center justify-between mt-1.5">
        <span className={`text-xs font-medium ${meta.textClass}`}>{meta.label}</span>
        {meta.tip && (
          <span className="text-[11px] text-zinc-500 dark:text-zinc-400">{meta.tip}</span>
        )}
      </div>
    </div>
  );
}

const LEVELS = [
  null, // never used
  { label: "Weak",   barClass: "bg-red-500",     textClass: "text-red-600 dark:text-red-400",       tip: "Try 8+ chars with a mix" },
  { label: "Fair",   barClass: "bg-amber-500",   textClass: "text-amber-600 dark:text-amber-400",   tip: "Add a number or symbol" },
  { label: "Good",   barClass: "bg-lime-500",    textClass: "text-lime-600 dark:text-lime-400",     tip: "Almost there" },
  { label: "Strong", barClass: "bg-emerald-500", textClass: "text-emerald-600 dark:text-emerald-400", tip: "Looks great" },
];

function scoreOf(p) {
  if (!p || p.length < 4) return 1;
  let s = 0;
  if (p.length >= 8) s++;
  if (p.length >= 12) s++;
  const variety =
    (/[a-z]/.test(p) ? 1 : 0) +
    (/[A-Z]/.test(p) ? 1 : 0) +
    (/[0-9]/.test(p) ? 1 : 0) +
    (/[^A-Za-z0-9]/.test(p) ? 1 : 0);
  if (variety >= 2) s++;
  if (variety >= 3) s++;
  // Clamp to 1-4
  return Math.max(1, Math.min(4, s));
}
