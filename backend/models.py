from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="employee")  # employee | admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("Session", back_populates="user")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    sender_name = Column(String)
    role_applied = Column(String)
    company_name = Column(String)
    tone = Column(String)
    category = Column(String)
    situation_type = Column(String)
    expected_points = Column(JSON)
    ideal_response_tone = Column(Text)
    difficulty = Column(String, default="medium")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("Session", back_populates="scenario")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, default="active")  # active | completed
    message_count = Column(Integer, default=0)
    daily_summary = Column(Text, nullable=True)
    overall_score = Column(Float, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date"),)

    user = relationship("User", back_populates="sessions")
    scenario = relationship("Scenario", back_populates="sessions")
    messages = relationship("Message", back_populates="session", order_by="Message.sequence_num")
    evaluations = relationship("Evaluation", back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user | ai
    content = Column(Text, nullable=False)
    sequence_num = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session", back_populates="messages")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    acknowledge = Column(Float, default=0.0)
    apology = Column(Float, default=0.0)
    clarity = Column(Float, default=0.0)
    reassurance = Column(Float, default=0.0)
    overall = Column(Float, default=0.0)
    decision = Column(String)  # end | followup | counter
    ai_reply = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session", back_populates="evaluations")


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())