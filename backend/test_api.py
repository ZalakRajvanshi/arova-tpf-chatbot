"""
Integration tests using FastAPI TestClient (no server needed).
Run: python test_api.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from unittest.mock import patch

# Mock the AI evaluator so we don't burn OpenAI credits during testing
def fake_evaluate(scenario_message, expected_points, ideal_response_tone, conversation_history, user_message, round_num):
    return {
        "acknowledge": 0.8,
        "apology": 0.7,
        "clarity": 0.85,
        "reassurance": 0.75,
        "overall": 0.78,
        "decision": "end" if round_num >= 2 else "followup",
        "reply": "Thanks for the update — that works for me. I'll wait to hear back.",
    }

def fake_summary(scenario_message, conversation):
    return "The trainee acknowledged the concern, apologised for the delay, and gave a clear timeline. Strong response overall."

import services.ai_evaluator as ai_mod
ai_mod.evaluate = fake_evaluate
ai_mod.generate_daily_summary = fake_summary

# Also patch them where they were imported
import routers.session as sess_mod
sess_mod.evaluate = fake_evaluate
sess_mod.generate_daily_summary = fake_summary

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import User
from auth import hash_password

client = TestClient(app)
errors = []

def ok(label, condition, detail=""):
    if condition:
        print(f"  [PASS]  {label}")
    else:
        print(f"  [FAIL]  {label}  <- {detail}")
        errors.append(label)

def section(title):
    print(f"\n{'-'*52}")
    print(f"  {title}")
    print(f"{'-'*52}")


# ── 0. Ensure test employee exists + clean today's session ──
from datetime import date as _date
import models as _models

db = SessionLocal()
test_email = "test@1234"
if not db.query(User).filter(User.email == test_email).first():
    db.add(User(
        email=test_email,
        password_hash=hash_password("test6789*"),
        name="Test Employee",
        role="employee",
    ))
    db.commit()

# Wipe today's session for test user so we can re-test cleanly
test_user = db.query(User).filter(User.email == test_email).first()
existing_sess = db.query(_models.Session).filter(
    _models.Session.user_id == test_user.id,
    _models.Session.date == _date.today(),
).all()
for s in existing_sess:
    db.query(_models.Evaluation).filter(_models.Evaluation.session_id == s.id).delete()
    db.query(_models.Message).filter(_models.Message.session_id == s.id).delete()
    db.delete(s)
db.commit()
db.close()


# ── 1. Health check ───────────────────────────────────
section("1. Health Check")
r = client.get("/")
ok("Server responds 200", r.status_code == 200)
ok("Returns ok status", r.json().get("status") == "ok")


# ── 2. Admin login ────────────────────────────────────
section("2. Admin Login")
r = client.post("/auth/login", json={
    "email": "abhay@theproductfolks.com",
    "password": "admin@1234"
})
ok("Login returns 200", r.status_code == 200, r.text)
admin_token = r.json().get("access_token", "")
ok("Token received", bool(admin_token))
ok("Role is admin", r.json().get("role") == "admin")
admin_h = {"Authorization": f"Bearer {admin_token}"}


# ── 3. Employee login ─────────────────────────────────
section("3. Employee Login")
r = client.post("/auth/login", json={"email": test_email, "password": "test6789*"})
ok("Returns 200", r.status_code == 200, r.text)
emp_token = r.json().get("access_token", "")
ok("Token received", bool(emp_token))
ok("Role is employee", r.json().get("role") == "employee")
emp_h = {"Authorization": f"Bearer {emp_token}"}


# ── 4. Auth guards ────────────────────────────────────
section("4. Auth Guards")
r = client.post("/auth/login", json={"email": test_email, "password": "wrong"})
ok("Wrong password -> 401", r.status_code == 401)

r = client.get("/session/today")
ok("No token -> 401", r.status_code == 401)

r = client.get("/admin/users", headers=emp_h)
ok("Employee cannot hit admin routes -> 403", r.status_code == 403)


# ── 5. Today's scenario ───────────────────────────────
section("5. Today's Scenario")
r = client.get("/session/today", headers=emp_h)
ok("Returns 200", r.status_code == 200, r.text)
sess = r.json()
ok("Has session id", "id" in sess)
ok("Has scenario", "scenario" in sess)
ok("Status is active", sess.get("status") == "active")
ok("Scenario has message", bool(sess.get("scenario", {}).get("message")))
ok("Scenario has company_name", bool(sess.get("scenario", {}).get("company_name")))

scenario_msg = sess.get("scenario", {}).get("message", "")
print(f"\n     Scenario : \"{scenario_msg[:90]}...\"")

# Calling again returns the same session (idempotent)
r2 = client.get("/session/today", headers=emp_h)
ok("Second call returns same session", r2.json().get("id") == sess.get("id"))


# ── 6. Send message + AI evaluation ──────────────────
section("6. Send Message + AI Evaluation  [calls OpenAI]")
r = client.post("/session/message", headers=emp_h, json={
    "content": "Hi, thank you for reaching out. I understand your concern and I apologise for the delay. Let me check with the team right now and get back to you with a clear update by end of day."
})
ok("Returns 200", r.status_code == 200, r.text)
msg = r.json()
ok("Has ai_reply", bool(msg.get("ai_reply")))
ok("Decision is valid", msg.get("decision") in ["end", "followup", "counter"])
ok("message_count incremented", msg.get("message_count", 0) >= 2)
ok("session_status present", msg.get("session_status") in ["active", "completed"])

print(f"\n     Decision   : {msg.get('decision')}")
print(f"     AI reply   : \"{str(msg.get('ai_reply', ''))[:100]}...\"")
print(f"     Msg count  : {msg.get('message_count')}")


# ── 7. Completed session locks ────────────────────────
section("7. Session Lock After Completion")
# Force-complete by hammering until done
status = msg.get("session_status")
for i in range(4):
    if status == "completed":
        break
    r = client.post("/session/message", headers=emp_h, json={
        "content": "Thank you for your patience. I have now spoken with the hiring team and they will contact you within 2 business days with a full update. Apologies again for the wait."
    })
    if r.status_code == 200:
        status = r.json().get("session_status")
    else:
        break

if status == "completed":
    r = client.post("/session/message", headers=emp_h, json={"content": "one more"})
    ok("Completed session rejects further messages -> 400", r.status_code == 400)
else:
    print("  [SKIP]  Session not yet completed (AI kept giving followups)")


# ── 8. Admin users list ───────────────────────────────
section("8. Admin — Users List")
r = client.get("/admin/users", headers=admin_h)
ok("Returns 200", r.status_code == 200, r.text)
users = r.json()
ok("Returns a list", isinstance(users, list))
ok("Contains test user", any(u["email"] == test_email for u in users))
ok("Each user has avg_score field", all("avg_score" in u for u in users))


# ── 9. Admin user profile ─────────────────────────────
section("9. Admin — User Profile")
db = SessionLocal()
test_user_id = db.query(User).filter(User.email == test_email).first().id
db.close()

r = client.get(f"/admin/user/{test_user_id}", headers=admin_h)
ok("Returns 200", r.status_code == 200, r.text)
profile = r.json()
ok("Has sessions list", isinstance(profile.get("sessions"), list))
ok("Has score breakdown fields", all(k in profile for k in ["avg_acknowledge", "avg_clarity", "avg_reassurance"]))
if profile.get("sessions"):
    s = profile["sessions"][0]
    ok("Session has daily_summary", "daily_summary" in s)
    ok("Session has overall_score", "overall_score" in s)
    ok("Session has messages", "messages" in s)


# ── Summary ───────────────────────────────────────────
print(f"\n{'='*52}")
if not errors:
    print("  All tests passed.")
else:
    print(f"  {len(errors)} test(s) failed:")
    for e in errors:
        print(f"    - {e}")
print(f"{'='*52}\n")