import { useState } from "react";

/**
 * Logo lives at: frontend/public/logo.png
 * If missing, falls back to a styled "TPF" mark.
 */
export default function Logo({ size = 28, className = "" }) {
  const [errored, setErrored] = useState(false);

  if (errored) {
    return (
      <div
        className={`inline-flex items-center justify-center font-bold tracking-tight ${className}`}
        style={{
          width: size,
          height: size,
          fontSize: size * 0.4,
          background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
          color: "#fff",
          borderRadius: size * 0.25,
        }}
      >
        TPF
      </div>
    );
  }

  return (
    <img
      src="/logo.png"
      alt="The Product Folks"
      onError={() => setErrored(true)}
      style={{ height: size, width: "auto" }}
      className={className}
    />
  );
}
