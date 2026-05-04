import os
import json
import time
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda: None
from apify_client import ApifyClient
from openai import OpenAI

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINKEDIN_PROFILE = "https://www.linkedin.com/in/suhasmotwani/"
OUTPUT_FILE = "scenarios.json"
TONE_FILE = "tone_profile.json"


# ─────────────────────────────────────────────
# STEP 1: Scrape all posts from LinkedIn profile
# ─────────────────────────────────────────────

def scrape_posts():
    print("\n[Step 1] Scraping LinkedIn posts...")
    client = ApifyClient(APIFY_TOKEN)

    run_input = {
        "targetUrls": [LINKEDIN_PROFILE],
        "maxPosts": 0,           # 0 = all posts
        "maxComments": 0,
        "includeReposts": True,
        "includeQuotePosts": True,
        "postNestedReactions": False,
        "postNestedComments": False,
    }

    run = client.actor("harvestapi/linkedin-profile-posts").call(run_input=run_input)

    posts = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        text = item.get("text") or item.get("content") or ""
        if text.strip():
            posts.append({
                "text": text.strip(),
                "url": item.get("url", ""),
                "posted_at": item.get("postedAt") or item.get("publishedAt", ""),
                "likes": item.get("likesCount", 0),
                "comments": item.get("commentsCount", 0),
            })

    print(f"  Scraped {len(posts)} posts with text content.")
    return posts


# ─────────────────────────────────────────────
# STEP 2: Extract founder's tone & philosophy
# ─────────────────────────────────────────────

def extract_tone_profile(posts, ai_client):
    print("\n[Step 2] Extracting tone profile from posts...")

    # Use top 30 posts (most engagement = most representative)
    sample = sorted(posts, key=lambda p: p.get("likes", 0), reverse=True)[:30]
    combined = "\n\n---\n\n".join([p["text"] for p in sample])

    prompt = f"""You are analyzing LinkedIn posts from Suhas Motwani, a founder, to understand his communication philosophy — especially around hiring, candidates, and professional communication.

Here are his posts:
{combined}

Analyze and return a JSON with:
{{
  "tone_descriptors": ["list of words describing his tone, e.g. direct, empathetic, no-nonsense"],
  "core_values": ["what he values in professional communication"],
  "hiring_philosophy": ["his specific views on hiring, candidates, recruiters"],
  "language_patterns": ["phrases or patterns he commonly uses"],
  "what_good_looks_like": ["how he defines or expects excellent HR/candidate communication"],
  "what_bad_looks_like": ["communication mistakes or failures he calls out"]
}}

Return only valid JSON."""

    response = ai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    tone = json.loads(response.choices[0].message.content)
    print(f"  Tone: {tone.get('tone_descriptors', [])}")
    print(f"  Core values: {tone.get('core_values', [])}")
    return tone


# ─────────────────────────────────────────────
# STEP 3: Convert each post to a training scenario
# ─────────────────────────────────────────────

def convert_post_to_scenario(post, tone_profile, ai_client):
    prompt = f"""You are building an HR communication training system. The training is based on the communication philosophy of Suhas Motwani.

His communication style:
- Tone: {", ".join(tone_profile.get("tone_descriptors", []))}
- Core values: {", ".join(tone_profile.get("core_values", []))}
- Hiring philosophy: {", ".join(tone_profile.get("hiring_philosophy", []))}
- What good communication looks like: {", ".join(tone_profile.get("what_good_looks_like", []))}

LinkedIn post:
\"\"\"{post["text"]}\"\"\"

Task: Can this post be turned into a realistic training scenario where an HR employee must respond to a candidate or client message?

Rules:
- The scenario must simulate a real message from a candidate, job seeker, or client
- It must require an HR employee to respond professionally
- It must be based on a real situation from the post (not generic)

If YES → convert it.
If NO → return {{"usable": false}}

Return JSON:
{{
  "usable": true,
  "message": "The scenario message written in first person, as if a real candidate/client sent it. Natural, slightly emotional, open-ended.",
  "sender_name": "A realistic Indian first name",
  "role_applied": "Job role relevant to the scenario (e.g. Product Manager, Frontend Developer)",
  "tone": "one of: frustrated_candidate | confused_candidate | concerned_candidate | ghosted_candidate | professional_client | angry_client",
  "category": "one of: delay | ghosting | process_confusion | offer_issue | rejection | feedback_request | general",
  "expected_points": ["list from: acknowledge, apologize, clarify, reassure, provide_timeline, explain_process, show_empathy"],
  "ideal_response_tone": "1 sentence on how Suhas would expect the HR to respond based on his philosophy",
  "difficulty": "easy | medium | hard",
  "source_url": "{post['url']}"
}}"""

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.5,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"    Error converting post: {e}")
        return {"usable": False}


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────

def run_pipeline():
    if not APIFY_TOKEN:
        print("ERROR: APIFY_TOKEN not set in .env")
        return
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set in .env")
        return

    ai_client = OpenAI(api_key=OPENAI_API_KEY)

    # Step 1: Scrape
    posts = scrape_posts()
    if not posts:
        print("No posts found. Check the profile URL or Apify token.")
        return

    # Step 2: Tone profile
    tone_profile = extract_tone_profile(posts, ai_client)
    with open(TONE_FILE, "w", encoding="utf-8") as f:
        json.dump(tone_profile, f, indent=2)
    print(f"  Tone profile saved to {TONE_FILE}")

    # Step 3: Convert posts to scenarios
    print(f"\n[Step 3] Converting {len(posts)} posts to scenarios...")
    scenarios = []
    skipped = 0

    for i, post in enumerate(posts):
        if len(post["text"]) < 80:
            skipped += 1
            continue

        result = convert_post_to_scenario(post, tone_profile, ai_client)

        if result.get("usable"):
            scenarios.append(result)
            print(f"  [{i+1}/{len(posts)}] ✓  [{result.get('category')}] {result.get('message', '')[:60]}...")
        else:
            print(f"  [{i+1}/{len(posts)}] ✗  Not usable")

        time.sleep(0.4)  # avoid OpenAI rate limits

    # Save output
    output = {
        "source_profile": LINKEDIN_PROFILE,
        "total_posts_scraped": len(posts),
        "total_scenarios": len(scenarios),
        "tone_profile": tone_profile,
        "scenarios": scenarios,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'─'*50}")
    print(f"  Posts scraped     : {len(posts)}")
    print(f"  Posts skipped     : {skipped} (too short)")
    print(f"  Scenarios created : {len(scenarios)}")
    print(f"  Output saved to   : {OUTPUT_FILE}")
    print(f"  Tone profile at   : {TONE_FILE}")
    print(f"{'─'*50}\n")


if __name__ == "__main__":
    run_pipeline()