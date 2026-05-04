import os
import json
import time
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda: None
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TONE_FILE = "tone_profile.json"
OUTPUT_FILE = "scenarios.json"

# ─────────────────────────────────────────────────────────────
# TPF CONTEXT — what The Product Folks team actually does
# ─────────────────────────────────────────────────────────────

TPF_CONTEXT = """
The Product Folks (TPF) is a product management community with 250,000+ members.
Their team manages talent recruitment — they list PM and tech roles from companies like
Swiggy, Zomato, Paytm, Pine Labs, BharatPe, Zepto, Google, Razorpay, Meesho, CRED, and others.
Candidates apply or get referred to these roles through the TPF platform.

The TPF recruiter team:
- Screens and shortlists candidates for client companies
- Schedules and coordinates interviews between candidates and companies
- Communicates updates, feedback, and decisions to candidates
- Manages relationships with hiring companies
- Handles their own internal team hiring too
"""

# ─────────────────────────────────────────────────────────────
# 15 SITUATION TYPES — real scenarios the TPF team handles
# ─────────────────────────────────────────────────────────────

SITUATION_TYPES = [
    {
        "id": "no_update_after_applying",
        "description": "Candidate applied for a role via TPF job board 1-3 weeks ago and has received no response at all.",
        "companies": ["Swiggy", "Zomato", "Paytm", "BharatPe", "Pine Labs", "Meesho"],
        "roles": ["Senior Product Manager", "Product Manager", "Associate PM", "Growth PM"],
        "tone": "concerned_candidate",
        "category": "delay",
        "difficulty": "easy",
        "count": 5,
    },
    {
        "id": "post_interview_silence",
        "description": "Candidate completed one or more interview rounds arranged by TPF but has received no feedback for 1-2 weeks.",
        "companies": ["Zepto", "CRED", "Razorpay", "Google", "PhonePe"],
        "roles": ["Senior PM", "Product Manager", "Principal PM"],
        "tone": "frustrated_candidate",
        "category": "delay",
        "difficulty": "medium",
        "count": 5,
    },
    {
        "id": "competing_offer_urgency",
        "description": "Candidate is in TPF's hiring pipeline but has received an offer from another company and needs a decision urgently.",
        "companies": ["Swiggy", "Zomato", "Meesho", "Paytm"],
        "roles": ["Product Manager", "Senior PM", "Growth PM"],
        "tone": "concerned_candidate",
        "category": "offer_issue",
        "difficulty": "hard",
        "count": 4,
    },
    {
        "id": "referral_process_confusion",
        "description": "Candidate clicked 'Get Referred' on TPF job board but doesn't understand the next steps or hasn't heard anything.",
        "companies": ["BharatPe", "Pine Labs", "Pocket FM", "Razorpay"],
        "roles": ["Product Manager", "Associate PM"],
        "tone": "confused_candidate",
        "category": "process_confusion",
        "difficulty": "easy",
        "count": 4,
    },
    {
        "id": "offer_letter_delay",
        "description": "Candidate verbally accepted the offer 1-2 weeks ago but has not received the formal offer letter.",
        "companies": ["Zepto", "CRED", "Swiggy", "PhonePe"],
        "roles": ["Senior PM", "Product Manager"],
        "tone": "concerned_candidate",
        "category": "offer_issue",
        "difficulty": "medium",
        "count": 4,
    },
    {
        "id": "rejection_feedback_request",
        "description": "Candidate was rejected and is reaching out to understand why, asking for specific feedback to improve.",
        "companies": ["Google", "Razorpay", "CRED", "BharatPe"],
        "roles": ["Senior PM", "Principal PM", "Product Manager"],
        "tone": "concerned_candidate",
        "category": "feedback_request",
        "difficulty": "medium",
        "count": 4,
    },
    {
        "id": "interview_cancelled_no_reschedule",
        "description": "Interview scheduled by TPF got cancelled by the company with no rescheduling or explanation.",
        "companies": ["Meesho", "Zomato", "Pine Labs", "Paytm"],
        "roles": ["Product Manager", "Senior PM"],
        "tone": "frustrated_candidate",
        "category": "process_confusion",
        "difficulty": "medium",
        "count": 4,
    },
    {
        "id": "ghosted_mid_process",
        "description": "Candidate was actively communicating with the TPF recruiter but the recruiter suddenly stopped responding.",
        "companies": ["Swiggy", "BharatPe", "Zepto", "Razorpay"],
        "roles": ["Senior PM", "Growth PM", "Associate PM"],
        "tone": "ghosted_candidate",
        "category": "ghosting",
        "difficulty": "hard",
        "count": 4,
    },
    {
        "id": "salary_mismatch",
        "description": "Candidate received an offer but the salary is significantly lower than what was discussed or expected during the process.",
        "companies": ["CRED", "PhonePe", "Meesho", "Pine Labs"],
        "roles": ["Senior PM", "Product Manager", "Principal PM"],
        "tone": "frustrated_candidate",
        "category": "offer_issue",
        "difficulty": "hard",
        "count": 4,
    },
    {
        "id": "role_no_longer_listed",
        "description": "Candidate applied for a role that has now disappeared from the TPF job board. They are confused and worried.",
        "companies": ["Zomato", "Swiggy", "Paytm", "BharatPe"],
        "roles": ["Product Manager", "Senior PM"],
        "tone": "confused_candidate",
        "category": "process_confusion",
        "difficulty": "easy",
        "count": 3,
    },
    {
        "id": "notice_period_issue",
        "description": "Candidate received an offer but the company wants an immediate joiner while the candidate has a 2-3 month notice period.",
        "companies": ["Zepto", "Razorpay", "CRED", "PhonePe"],
        "roles": ["Senior PM", "Principal PM"],
        "tone": "concerned_candidate",
        "category": "offer_issue",
        "difficulty": "medium",
        "count": 3,
    },
    {
        "id": "client_candidate_no_show",
        "description": "A hiring company (TPF's client) is frustrated because a candidate TPF referred did not show up to the scheduled interview.",
        "companies": ["Swiggy", "Zomato", "Meesho", "Paytm"],
        "roles": ["PM Lead", "Senior PM"],
        "tone": "angry_client",
        "category": "general",
        "difficulty": "hard",
        "count": 3,
    },
    {
        "id": "client_profile_mismatch",
        "description": "A hiring company says the candidates TPF is sending don't match the role requirements and they are frustrated.",
        "companies": ["BharatPe", "CRED", "Razorpay", "Google"],
        "roles": ["Senior PM", "Principal PM"],
        "tone": "professional_client",
        "category": "general",
        "difficulty": "hard",
        "count": 3,
    },
    {
        "id": "internal_team_delayed_feedback",
        "description": "A TPF team member has been waiting for performance review feedback or role clarity from their manager for weeks.",
        "companies": ["The Product Folks"],
        "roles": ["Community Manager", "Talent Associate", "Operations Manager"],
        "tone": "concerned_candidate",
        "category": "delay",
        "difficulty": "medium",
        "count": 3,
    },
    {
        "id": "candidate_reapplying_after_rejection",
        "description": "Candidate was rejected a few months ago and is now reapplying for the same or similar role, asking if they will be considered.",
        "companies": ["Swiggy", "Zepto", "CRED", "BharatPe"],
        "roles": ["Product Manager", "Senior PM"],
        "tone": "concerned_candidate",
        "category": "feedback_request",
        "difficulty": "medium",
        "count": 3,
    },
]


# ─────────────────────────────────────────────────────────────
# GENERATE scenarios for one situation type
# ─────────────────────────────────────────────────────────────

def generate_for_situation(situation, tone_profile, ai_client):
    prompt = f"""You are generating realistic training scenarios for The Product Folks (TPF) HR team.

ABOUT TPF:
{TPF_CONTEXT}

SUHAS MOTWANI'S COMMUNICATION STANDARDS (used to evaluate responses):
- Tone: {", ".join(tone_profile.get("tone_descriptors", []))}
- Core values: {", ".join(tone_profile.get("core_values", []))}
- Hiring philosophy: {", ".join(tone_profile.get("hiring_philosophy", []))}
- What good looks like: {", ".join(tone_profile.get("what_good_looks_like", []))}
- What bad looks like: {", ".join(tone_profile.get("what_bad_looks_like", []))}

SITUATION TO GENERATE:
{situation["description"]}

Generate {situation["count"]} different, realistic scenarios for this situation.
Use different names, companies from {situation["companies"]}, and slightly different wording each time.
Make each message feel like a real person typed it — natural, slightly emotional, not formal.
Keep messages short: 2-4 sentences max.

Return JSON:
{{
  "scenarios": [
    {{
      "message": "The message written in first person as if a real candidate/client is sending it to the TPF team",
      "sender_name": "A realistic Indian first name",
      "role_applied": "The job role (use roles from {situation["roles"]})",
      "company_name": "The company name from the list",
      "tone": "{situation["tone"]}",
      "category": "{situation["category"]}",
      "expected_points": ["2-4 items from: acknowledge, apologize, clarify, reassure, provide_timeline, explain_process, show_empathy, set_expectations"],
      "ideal_response_tone": "One sentence: how a TPF recruiter following Suhas's philosophy should respond",
      "difficulty": "{situation["difficulty"]}"
    }}
  ]
}}"""

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.8,
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("scenarios", [])
    except Exception as e:
        print(f"    Error: {e}")
        return []


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def run():
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set in .env")
        return

    with open(TONE_FILE, "r", encoding="utf-8") as f:
        tone_profile = json.load(f)

    print(f"Tone profile loaded: {tone_profile.get('tone_descriptors')}\n")

    ai_client = OpenAI(api_key=OPENAI_API_KEY)
    all_scenarios = []

    for i, situation in enumerate(SITUATION_TYPES):
        print(f"[{i+1}/{len(SITUATION_TYPES)}] Generating: {situation['id']} ({situation['count']} scenarios)...")
        scenarios = generate_for_situation(situation, tone_profile, ai_client)

        for s in scenarios:
            s["situation_type"] = situation["id"]

        all_scenarios.extend(scenarios)
        print(f"  ✓ Got {len(scenarios)} scenarios (total so far: {len(all_scenarios)})")
        time.sleep(0.5)

    output = {
        "total_scenarios": len(all_scenarios),
        "tone_profile": tone_profile,
        "tpf_context": TPF_CONTEXT.strip(),
        "scenarios": all_scenarios,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'─'*50}")
    print(f"  Total scenarios generated : {len(all_scenarios)}")
    print(f"  Saved to                  : {OUTPUT_FILE}")
    print(f"{'─'*50}\n")


if __name__ == "__main__":
    run()