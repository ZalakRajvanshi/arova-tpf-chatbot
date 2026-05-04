from datetime import date, timedelta
from sqlalchemy.orm import Session
import models


def calculate_streak(user_id: int, db: Session) -> int:
    """Number of consecutive days (ending today or yesterday) with a completed session."""
    rows = db.query(models.Session.date).filter(
        models.Session.user_id == user_id,
        models.Session.status == "completed",
    ).all()
    completed = {r[0] for r in rows}
    if not completed:
        return 0

    today = date.today()
    yesterday = today - timedelta(days=1)

    if today in completed:
        cursor = today
    elif yesterday in completed:
        cursor = yesterday
    else:
        return 0

    streak = 0
    while cursor in completed:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def session_completed_today(user_id: int, db: Session) -> bool:
    return db.query(models.Session).filter(
        models.Session.user_id == user_id,
        models.Session.date == date.today(),
        models.Session.status == "completed",
    ).first() is not None
