"""
Generates a single seed.sql file you can paste into Supabase's SQL Editor.
No DB connection needed — just runs locally.

Usage:
    python generate_sql.py

Output: backend/seed.sql
"""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(__file__))

# Use passlib directly so this script doesn't pull in database.py / .env
from passlib.context import CryptContext
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(p): return _pwd.hash(p)

SCENARIOS_FILE = os.path.join(os.path.dirname(__file__), "../pipeline/scenarios.json")
OUTPUT = os.path.join(os.path.dirname(__file__), "seed.sql")

ADMIN_EMAIL = "abhay@theproductfolks.com"
ADMIN_PASSWORD = "admin@1234"
ADMIN_NAME = "Abhay"

TEST_EMAIL = "test@1234"
TEST_PASSWORD = "test6789*"
TEST_NAME = "Test User"


def esc(s):
    """Escape a Python string for SQL single-quoted literal."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def json_literal(obj):
    """Pass a Python object as a JSONB literal string."""
    return "'" + json.dumps(obj).replace("'", "''") + "'::jsonb"


def main():
    with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenarios = data.get("scenarios", [])

    admin_hash = hash_password(ADMIN_PASSWORD)
    test_hash = hash_password(TEST_PASSWORD)

    out = []

    out.append("-- TPF Communication Training — full seed (Postgres)")
    out.append("-- Paste this into Supabase SQL Editor and click Run.")
    out.append("")

    # Drop in dependency order (safe to re-run)
    out.append("DROP TABLE IF EXISTS evaluations CASCADE;")
    out.append("DROP TABLE IF EXISTS messages CASCADE;")
    out.append("DROP TABLE IF EXISTS password_resets CASCADE;")
    out.append("DROP TABLE IF EXISTS sessions CASCADE;")
    out.append("DROP TABLE IF EXISTS scenarios CASCADE;")
    out.append("DROP TABLE IF EXISTS users CASCADE;")
    out.append("")

    # ── Tables ─────────────────────────────────────────
    out.append("""CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  name VARCHAR NOT NULL,
  role VARCHAR DEFAULT 'employee',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ix_users_email ON users(email);""")
    out.append("")

    out.append("""CREATE TABLE scenarios (
  id SERIAL PRIMARY KEY,
  message TEXT NOT NULL,
  sender_name VARCHAR,
  role_applied VARCHAR,
  company_name VARCHAR,
  tone VARCHAR,
  category VARCHAR,
  situation_type VARCHAR,
  expected_points JSONB,
  ideal_response_tone TEXT,
  difficulty VARCHAR DEFAULT 'medium',
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);""")
    out.append("")

    out.append("""CREATE TABLE sessions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
  date DATE NOT NULL,
  status VARCHAR DEFAULT 'active',
  message_count INTEGER DEFAULT 0,
  daily_summary TEXT,
  overall_score FLOAT,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  CONSTRAINT uq_user_date UNIQUE (user_id, date)
);""")
    out.append("")

    out.append("""CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id),
  role VARCHAR NOT NULL,
  content TEXT NOT NULL,
  sequence_num INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);""")
    out.append("")

    out.append("""CREATE TABLE evaluations (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id),
  message_id INTEGER NOT NULL REFERENCES messages(id),
  acknowledge FLOAT DEFAULT 0,
  apology FLOAT DEFAULT 0,
  clarity FLOAT DEFAULT 0,
  reassurance FLOAT DEFAULT 0,
  overall FLOAT DEFAULT 0,
  decision VARCHAR,
  ai_reply TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);""")
    out.append("")

    out.append("""CREATE TABLE password_resets (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  token VARCHAR UNIQUE NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ix_password_resets_user_id ON password_resets(user_id);
CREATE INDEX ix_password_resets_token ON password_resets(token);""")
    out.append("")

    # ── Users ──────────────────────────────────────────
    out.append("-- Users")
    out.append(
        f"INSERT INTO users (email, password_hash, name, role) VALUES "
        f"({esc(ADMIN_EMAIL)}, {esc(admin_hash)}, {esc(ADMIN_NAME)}, 'admin');"
    )
    out.append(
        f"INSERT INTO users (email, password_hash, name, role) VALUES "
        f"({esc(TEST_EMAIL)}, {esc(test_hash)}, {esc(TEST_NAME)}, 'employee');"
    )
    out.append("")

    # ── Scenarios ──────────────────────────────────────
    out.append(f"-- Scenarios ({len(scenarios)} rows)")
    for s in scenarios:
        out.append(
            "INSERT INTO scenarios (message, sender_name, role_applied, company_name, "
            "tone, category, situation_type, expected_points, ideal_response_tone, "
            "difficulty, active) VALUES ("
            f"{esc(s.get('message',''))}, "
            f"{esc(s.get('sender_name',''))}, "
            f"{esc(s.get('role_applied',''))}, "
            f"{esc(s.get('company_name',''))}, "
            f"{esc(s.get('tone',''))}, "
            f"{esc(s.get('category',''))}, "
            f"{esc(s.get('situation_type',''))}, "
            f"{json_literal(s.get('expected_points', []))}, "
            f"{esc(s.get('ideal_response_tone',''))}, "
            f"{esc(s.get('difficulty','medium'))}, "
            "TRUE);"
        )
    out.append("")

    # Final verify queries
    out.append("-- Sanity check")
    out.append("SELECT count(*) AS users FROM users;")
    out.append("SELECT count(*) AS scenarios FROM scenarios;")

    text = "\n".join(out) + "\n"
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"OK — wrote {OUTPUT}")
    print(f"Scenarios: {len(scenarios)}")
    print(f"Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"Test : {TEST_EMAIL} / {TEST_PASSWORD}")
    print()
    print("Next: open Supabase → SQL Editor → New query → paste contents of seed.sql → Run.")


if __name__ == "__main__":
    main()
