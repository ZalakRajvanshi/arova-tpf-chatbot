"""
Generate a per-user persona summary for admin view.
Uses AI when available; falls back to a rule-based summary.
"""
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _classify_pattern(sessions):
    if not sessions:
        return "Not enough data yet."
    rounds = [s.message_count // 2 for s in sessions if s.message_count]
    if not rounds:
        return "Not enough data yet."
    avg_rounds = sum(rounds) / len(rounds)
    if avg_rounds <= 1.5:
        return "Direct communicator — usually wraps up in one round."
    if avg_rounds <= 2.5:
        return "Balanced — typically takes two rounds to close."
    return "Detailed — tends to use the full conversation length."


def _rule_based_persona(scores: dict, sessions):
    sorted_dims = sorted(scores.items(), key=lambda x: x[1] or 0, reverse=True)
    strong = [k for k, v in sorted_dims[:2] if (v or 0) >= 0.65]
    weak = [k for k, v in sorted_dims[-2:] if (v or 0) < 0.65]

    pretty = {
        "acknowledge": "Acknowledgement",
        "apology": "Apology",
        "clarity": "Clarity",
        "reassurance": "Reassurance",
    }

    return {
        "strengths": [f"Consistently strong on {pretty[k]}" for k in strong] or ["Building consistency across all dimensions."],
        "weaknesses": [f"Could improve on {pretty[k]}" for k in weak] or ["No major gaps yet."],
        "pattern": _classify_pattern(sessions),
        "recommendation": (
            f"Focus on {pretty[weak[0]]} in upcoming scenarios."
            if weak else "Keep refining tone and adapt to harder difficulty levels."
        ),
        "source": "rule_based",
    }


def _ai_persona(scores: dict, sessions, daily_summaries: list):
    summary_block = "\n".join(f"- {s}" for s in daily_summaries[-5:] if s)
    prompt = f"""Analyze this HR trainee's recent training sessions and write a brief persona for their manager.

Average scores (0-1):
- Acknowledge: {scores.get('acknowledge', 0):.2f}
- Apology:     {scores.get('apology', 0):.2f}
- Clarity:     {scores.get('clarity', 0):.2f}
- Reassurance: {scores.get('reassurance', 0):.2f}

Recent session summaries:
{summary_block}

Return JSON only:
{{
  "strengths":      ["2-3 short specific strengths (one line each)"],
  "weaknesses":     ["2-3 short specific gaps (one line each)"],
  "pattern":        "one sentence describing their communication style",
  "recommendation": "one specific action to focus on next"
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    data = json.loads(response.choices[0].message.content)
    data["source"] = "ai"
    return data


def generate_persona(sessions, evaluations) -> dict | None:
    """Returns None if there isn't enough data. Otherwise a persona dict."""
    if len(sessions) < 2:
        return None

    scores = {
        "acknowledge": _avg([e.acknowledge for e in evaluations]),
        "apology": _avg([e.apology for e in evaluations]),
        "clarity": _avg([e.clarity for e in evaluations]),
        "reassurance": _avg([e.reassurance for e in evaluations]),
    }
    summaries = [s.daily_summary for s in sessions if s.daily_summary]

    try:
        return _ai_persona(scores, sessions, summaries)
    except Exception:
        return _rule_based_persona(scores, sessions)


def _avg(vals):
    cleaned = [v for v in vals if v is not None]
    return sum(cleaned) / len(cleaned) if cleaned else 0.0
