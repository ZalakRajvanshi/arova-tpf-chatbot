from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import date
from typing import List
import models, schemas, auth
from database import get_db
from services.streak import calculate_streak, session_completed_today

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=schemas.MeResponse)
def get_me(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    sessions = db.query(models.Session).filter(models.Session.user_id == current_user.id).all()
    completed = [s for s in sessions if s.status == "completed"]

    today_active = db.query(models.Session).filter(
        models.Session.user_id == current_user.id,
        models.Session.date == date.today(),
        models.Session.status == "active",
    ).first() is not None

    return schemas.MeResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        stats=schemas.MeStats(
            total_sessions=len(sessions),
            completed_sessions=len(completed),
            streak=calculate_streak(current_user.id, db),
            completed_today=session_completed_today(current_user.id, db),
            has_active_session_today=today_active,
        ),
    )


@router.patch("", response_model=schemas.MeResponse)
def update_me(
    request: schemas.UpdateMeRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    name = request.name.strip()
    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters.")
    current_user.name = name
    db.commit()
    return get_me(current_user, db)


# ── User's own past chat history (read-only, no scores) ──
@router.get("/history", response_model=List[schemas.HistorySession])
def get_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(models.Session)
        .options(joinedload(models.Session.scenario), joinedload(models.Session.messages))
        .filter(models.Session.user_id == current_user.id)
        .order_by(models.Session.date.desc())
        .all()
    )

    out: List[schemas.HistorySession] = []
    for s in sessions:
        sc = s.scenario
        out.append(schemas.HistorySession(
            id=s.id,
            date=s.date,
            status=s.status,
            scenario=schemas.HistoryScenario(
                sender_name=sc.sender_name or "",
                role_applied=sc.role_applied or "",
                company_name=sc.company_name or "",
                message=sc.message or "",
            ),
            messages=[
                schemas.HistoryMessage(
                    role=m.role,
                    content=m.content,
                    sequence_num=m.sequence_num,
                    created_at=m.created_at,
                )
                for m in sorted(s.messages, key=lambda x: x.sequence_num)
            ],
        ))
    return out


