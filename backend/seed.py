"""
Run once to:
1. Create all DB tables
2. Load scenarios from pipeline/scenarios.json
3. Create a default admin user
"""
import sys
import json
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from database import engine, SessionLocal
from models import Base, Scenario, User, Session as SessionModel, Message, Evaluation
from auth import hash_password


def cascade_delete_user(db, user):
    session_ids = [s.id for s in db.query(SessionModel).filter(SessionModel.user_id == user.id).all()]
    if session_ids:
        db.query(Evaluation).filter(Evaluation.session_id.in_(session_ids)).delete(synchronize_session=False)
        db.query(Message).filter(Message.session_id.in_(session_ids)).delete(synchronize_session=False)
        db.query(SessionModel).filter(SessionModel.user_id == user.id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()

SCENARIOS_FILE = os.path.join(os.path.dirname(__file__), "../pipeline/scenarios.json")
ADMIN_EMAIL = "abhay@theproductfolks.com"
ADMIN_PASSWORD = "admin@1234"
OLD_ADMIN_EMAIL = "admin@theproductfolks.com"  # legacy — remove if found

TEST_EMAIL = "test@1234"
TEST_PASSWORD = "test6789*"
OLD_TEST_EMAIL = "testuser@theproductfolks.com"  # legacy — remove if found


def seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Load scenarios
    with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing = db.query(Scenario).count()
    if existing == 0:
        scenarios = data.get("scenarios", [])
        for s in scenarios:
            db.add(Scenario(
                message=s.get("message", ""),
                sender_name=s.get("sender_name", ""),
                role_applied=s.get("role_applied", ""),
                company_name=s.get("company_name", ""),
                tone=s.get("tone", ""),
                category=s.get("category", ""),
                situation_type=s.get("situation_type", ""),
                expected_points=s.get("expected_points", []),
                ideal_response_tone=s.get("ideal_response_tone", ""),
                difficulty=s.get("difficulty", "medium"),
                active=True,
            ))
        db.commit()
        print(f"  Loaded {len(scenarios)} scenarios.")
    else:
        print(f"  Scenarios already loaded ({existing} found), skipping.")

    # Remove legacy admin if present
    legacy = db.query(User).filter(User.email == OLD_ADMIN_EMAIL).first()
    if legacy:
        cascade_delete_user(db, legacy)
        print(f"  Removed legacy admin: {OLD_ADMIN_EMAIL}")

    # Create or refresh the real admin
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not admin:
        db.add(User(
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            name="Abhay",
            role="admin",
        ))
        db.commit()
        print(f"  Admin user created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    else:
        admin.password_hash = hash_password(ADMIN_PASSWORD)
        admin.name = "Abhay"
        admin.role = "admin"
        db.commit()
        print(f"  Admin user updated: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")

    # Remove legacy test user if present
    legacy_test = db.query(User).filter(User.email == OLD_TEST_EMAIL).first()
    if legacy_test:
        cascade_delete_user(db, legacy_test)
        print(f"  Removed legacy test user: {OLD_TEST_EMAIL}")

    # Create or refresh the test user
    test_user = db.query(User).filter(User.email == TEST_EMAIL).first()
    if not test_user:
        db.add(User(
            email=TEST_EMAIL,
            password_hash=hash_password(TEST_PASSWORD),
            name="Test User",
            role="employee",
        ))
        db.commit()
        print(f"  Test user created: {TEST_EMAIL} / {TEST_PASSWORD}")
    else:
        test_user.password_hash = hash_password(TEST_PASSWORD)
        test_user.name = "Test User"
        test_user.role = "employee"
        db.commit()
        print(f"  Test user updated: {TEST_EMAIL} / {TEST_PASSWORD}")

    db.close()
    print("Done.")


if __name__ == "__main__":
    seed()