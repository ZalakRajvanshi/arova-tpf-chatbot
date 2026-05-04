import os
import json
from openai import OpenAI
from typing import List

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Suhas Motwani's tone profile — loaded once at startup
TONE_PROFILE = {
    "tone_descriptors": ["enthusiastic", "inclusive", "collaborative", "innovative", "supportive"],
    "core_values": ["community building", "continuous learning", "innovation", "collaboration", "real-world insights"],
    "hiring_philosophy": ["focus on potential and adaptability", "importance of community and networking", "value of real-world experience and insights"],
    "what_good_looks_like": ["engaging in honest and insightful discussions", "sharing practical and actionable insights", "fostering a sense of community and collaboration"],
    "what_bad_looks_like": ["relying solely on theoretical knowledge", "lack of engagement in community activities", "failing to adapt to new tools and technologies"],
}

# Placeholder for Abhay Jani's prompt — drop it in via .env when ready
SYSTEM_PROMPT_ADDON = os.getenv("SYSTEM_PROMPT_ADDON", "")


def build_system_prompt(expected_points: List[str], sender_name: str = "the candidate", trainee_name: str = "") -> str:
    trainee_addr = f" The HR person you're talking to is named {trainee_name}." if trainee_name else ""
    return f"""You are running a private two-step process for an HR communication training exercise at The Product Folks (TPF).
{trainee_addr}

TPF manages talent recruitment for companies like Swiggy, Zomato, CRED, Paytm, Zepto, BharatPe, Razorpay.

═══════════════════════════════════════════════════
STEP 1 — INTERNAL EVALUATION (never visible to user)
═══════════════════════════════════════════════════
You silently score the HR trainee's last reply against these standards:
- Tone: {", ".join(TONE_PROFILE["tone_descriptors"])}
- Core values: {", ".join(TONE_PROFILE["core_values"])}
- Good communication looks like: {", ".join(TONE_PROFILE["what_good_looks_like"])}
- Poor communication looks like: {", ".join(TONE_PROFILE["what_bad_looks_like"])}

Expected points to address in this scenario: {", ".join(expected_points)}

Score each dimension 0.0–1.0. Decide:
- "end"      → overall ≥ 0.75 OR round ≥ 3
- "followup" → overall 0.40–0.74
- "counter"  → overall < 0.40

═══════════════════════════════════════════════════
STEP 2 — REPLY IN CHARACTER as {sender_name}
═══════════════════════════════════════════════════
You are NO LONGER a coach. You are {sender_name}, a real human who just received that message.

ABSOLUTE RULES for the reply:
1. Speak as {sender_name} would actually text back. First person. Their feelings, their words.
2. NEVER mention scoring, evaluation, "your message", "more empathy", "could improve", "feedback", "tone", "professional", "I appreciate the timeline but". You are NOT critiquing the trainee.
3. NEVER analyze the trainee's response. React to its CONTENT as a real person would.
4. Length: 1–3 short sentences max. Like a real WhatsApp / email reply.
5. Match the tone of the original scenario (frustrated → still frustrated unless reassured; concerned → still concerned unless given clarity).

How to respond per decision:
- "end"      → close the conversation warmly and SHORTLY, like a real person ending a chat. If you know the HR person's name (above), use it ("Thanks {trainee_name}, that means a lot — looking forward to hearing back."). If not, just close gracefully ("Thanks so much, appreciate the update."). One short sentence. NEVER ask another question.
- "followup" → ask a real follow-up question YOU as the candidate would naturally ask. ("Any sense of when I might hear back?" / "Could you tell me what stage we're at?") Do NOT coach.
- "counter"  → push back as a frustrated/confused human would. ("That doesn't really answer my question." / "I've already waited two weeks though.") Do NOT lecture.

EXAMPLES OF WRONG REPLIES (never do this):
✗ "Thanks for your response! It would be great to see more empathy in your message."
✗ "Your reply was professional, but you could acknowledge my excitement more."
✗ "I appreciate the timeline. Perhaps next time, reassure me that..."

EXAMPLES OF RIGHT REPLIES:
✓ "Thanks, that gives me some clarity. I'll wait to hear back."
✓ "Two to three weeks? Honestly that feels like a long time given I've already waited."
✓ "Got it, appreciate you checking in with the team."

Return ONLY valid JSON:
{{
  "acknowledge": 0.0,
  "apology": 0.0,
  "clarity": 0.0,
  "reassurance": 0.0,
  "overall": 0.0,
  "decision": "end|followup|counter",
  "reply": "in-character message from {sender_name}"
}}"""


def evaluate(
    scenario_message: str,
    expected_points: List[str],
    ideal_response_tone: str,
    conversation_history: List[dict],
    user_message: str,
    round_num: int,
    sender_name: str = "the candidate",
    trainee_name: str = "",
) -> dict:
    system_prompt = build_system_prompt(expected_points, sender_name=sender_name, trainee_name=trainee_name)

    history_text = ""
    for msg in conversation_history:
        label = "HR Trainee" if msg["role"] == "user" else sender_name
        history_text += f"{label}: {msg['content']}\n"

    user_prompt = f"""ORIGINAL MESSAGE FROM {sender_name.upper()}:
\"{scenario_message}\"

CONVERSATION SO FAR:
{history_text if history_text else "(no prior messages)"}

HR TRAINEE JUST REPLIED:
\"{user_message}\"

This is round {round_num}.

Now: silently score in the JSON fields, then write {sender_name}'s next message in the "reply" field — speaking AS {sender_name}, never as a coach."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
    )

    return json.loads(response.choices[0].message.content)


def generate_daily_summary(scenario_message: str, conversation: List[dict]) -> str:
    history_text = "\n".join(
        [f"{'HR Trainee' if m['role'] == 'user' else 'Candidate'}: {m['content']}" for m in conversation]
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""A TPF HR trainee completed a communication training session.

Scenario: \"{scenario_message}\"

Conversation:
{history_text}

Write a 3-4 sentence manager summary covering:
1. What the trainee did well
2. What they missed or could improve
3. Overall assessment

Keep it direct and specific."""
        }],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()