from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# ── Auth ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ResetPasswordTokenCheck(BaseModel):
    valid: bool
    email: Optional[str] = None


# ── Me (logged-in user) ───────────────────────────────
class MeStats(BaseModel):
    total_sessions: int
    completed_sessions: int
    streak: int
    completed_today: bool
    has_active_session_today: bool

class MeResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    stats: MeStats

class UpdateMeRequest(BaseModel):
    name: str


# ── User-facing chat history (no scores) ──────────────
class HistoryScenario(BaseModel):
    sender_name: str
    role_applied: str
    company_name: str
    message: str

class HistoryMessage(BaseModel):
    role: str
    content: str
    sequence_num: int
    created_at: datetime

class HistorySession(BaseModel):
    id: int
    date: date
    status: str
    scenario: HistoryScenario
    messages: List[HistoryMessage] = []

class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# ── Scenario ──────────────────────────────────────────
class ScenarioOut(BaseModel):
    id: int
    message: str
    sender_name: str
    role_applied: str
    company_name: str
    tone: str
    category: str
    difficulty: str

    class Config:
        orm_mode = True


class ScenarioRich(ScenarioOut):
    expected_points: List[str] = []
    ideal_response_tone: Optional[str] = None
    situation_type: Optional[str] = None


# ── Messages ──────────────────────────────────────────
class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    sequence_num: int
    created_at: datetime

    class Config:
        orm_mode = True


class EvaluationInline(BaseModel):
    acknowledge: float
    apology: float
    clarity: float
    reassurance: float
    overall: float
    decision: str
    points_hit: List[str] = []
    points_missed: List[str] = []

class MessageWithEvaluation(MessageOut):
    evaluation: Optional[EvaluationInline] = None


# ── Session ───────────────────────────────────────────
class SessionOut(BaseModel):
    id: int
    date: date
    status: str
    message_count: int
    scenario: ScenarioOut
    messages: List[MessageOut] = []

    class Config:
        orm_mode = True


class SendMessageRequest(BaseModel):
    content: str

class SendMessageResponse(BaseModel):
    ai_reply: str
    session_status: str   # active | completed
    message_count: int
    decision: str         # end | followup | counter


# ── Admin ─────────────────────────────────────────────
class UserSummary(BaseModel):
    id: int
    name: str
    email: str
    total_sessions: int
    avg_score: Optional[float]
    last_active: Optional[datetime]

    class Config:
        orm_mode = True


class CreateEmployeeRequest(BaseModel):
    name: str
    email: str
    password: str


class CreateEmployeeResponse(BaseModel):
    id: int
    name: str
    email: str


class SessionDetail(BaseModel):
    id: int
    date: date
    status: str
    message_count: int
    overall_score: Optional[float]
    daily_summary: Optional[str]
    scenario: ScenarioRich
    messages: List[MessageWithEvaluation]


class PersonaSummary(BaseModel):
    strengths: List[str] = []
    weaknesses: List[str] = []
    pattern: str = ""
    recommendation: str = ""
    source: str = "rule_based"


class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    total_sessions: int
    avg_score: Optional[float]
    avg_acknowledge: Optional[float]
    avg_apology: Optional[float]
    avg_clarity: Optional[float]
    avg_reassurance: Optional[float]
    streak: int = 0
    persona: Optional[PersonaSummary] = None
    sessions: List[SessionDetail] = []
