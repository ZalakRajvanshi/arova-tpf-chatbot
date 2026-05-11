import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

if DATABASE_URL.startswith("sqlite"):
    # Local dev — SQLite in same process
    engine_kwargs = {
        "connect_args": {"check_same_thread": False},
    }
else:
    # Production (Postgres / Supabase pooler) — proper connection pool
    # so multiple concurrent users don't wait for connections.
    engine_kwargs = {
        "pool_size": 10,            # permanent connections kept open
        "max_overflow": 10,         # extra burst connections allowed
        "pool_pre_ping": True,      # validates each connection before use
        "pool_recycle": 1800,       # recycle every 30 min (Supabase drops idle ones)
        "pool_timeout": 10,         # wait max 10s for a free connection
    }

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
