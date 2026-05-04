import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import auth, session, admin, me

app = FastAPI(title="TPF Communication Training API", version="1.0.0")

# CORS — comma-separated list in CORS_ORIGINS env var.
# Defaults to local Vite dev server.
_cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [o.strip() for o in _cors_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(me.router)
app.include_router(session.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "TPF Training API is running"}