# Deployment Guide — Vercel + Render + Supabase

## Overview

| Layer | Service | URL after deploy |
|---|---|---|
| Frontend (React) | **Vercel** | `https://your-app.vercel.app` |
| Backend (FastAPI) | **Render** | `https://your-app.onrender.com` |
| Database (Postgres) | **Supabase** | (connection string only) |

Time required: ~30 minutes the first time.

---

## Prerequisites

- [ ] GitHub account, with this repo pushed (or fork/upload)
- [ ] OpenAI API key (with credits)
- [ ] Working local setup (verify `seed.py` runs and `npm run dev` works)

---

## Step 1 — Supabase (Database, ~5 min)

1. Go to [supabase.com](https://supabase.com) → **Start your project** → sign in with GitHub
2. **New Project**
   - Name: `tpf-training` (or whatever)
   - Database password: generate a strong one — **save it somewhere safe**
   - Region: nearest to you
   - Plan: **Free**
3. Wait ~2 min for the project to initialize
4. Go to **Project Settings → Database → Connection string → URI**
5. Copy the URI. It looks like:
   ```
   postgresql://postgres.xxx:[YOUR-PASSWORD]@aws-0-region.pooler.supabase.com:5432/postgres
   ```
   Replace `[YOUR-PASSWORD]` with the password you saved.
6. **Save this** — you'll paste it as `DATABASE_URL` in Render.

---

## Step 2 — Seed the production database (~3 min)

You need to load your 56 scenarios + create the admin user against Supabase.

From your local machine:

```bash
cd backend

# Set the production DB URL temporarily for this terminal
# Windows PowerShell:
$env:DATABASE_URL = "postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:5432/postgres"
# macOS/Linux:
# export DATABASE_URL="postgresql://..."

# Run seed (creates tables, loads scenarios, creates admin + test users)
python seed.py
```

You should see:
```
Creating tables...
  Loaded 56 scenarios.
  Admin user created: abhay@theproductfolks.com / admin@1234
  Test user created: test@1234 / test6789*
Done.
```

Verify in Supabase: **Table Editor** → you should see `users`, `scenarios`, `sessions`, `messages`, `evaluations`, `password_resets`.

---

## Step 3 — Render (Backend, ~10 min)

1. Push your code to GitHub if you haven't:
   ```bash
   cd com-chatbot
   git init
   git add .
   git commit -m "ready to deploy"
   gh repo create com-chatbot --public --source=. --remote=origin --push
   ```
   (or do this manually via github.com)

2. Go to [render.com](https://render.com) → sign in with GitHub
3. **New → Web Service** → pick your `com-chatbot` repo
4. Settings:
   - **Name**: `tpf-backend` (this becomes part of your URL)
   - **Region**: nearest
   - **Branch**: `master` or `main`
   - **Root directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free**

5. Click **Advanced** → add these environment variables:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | (your Supabase URI from Step 1) |
   | `OPENAI_API_KEY` | your OpenAI key |
   | `JWT_SECRET` | a long random string (generate with `openssl rand -hex 32`) |
   | `JWT_EXPIRE_HOURS` | `24` |
   | `CORS_ORIGINS` | `http://localhost:5173` (you'll add Vercel URL here in step 4) |
   | `RESET_LINK_BASE` | `http://localhost:5173/reset-password` (update later) |

6. Click **Create Web Service**. Build takes ~3-5 min.

7. When done, copy your URL — looks like `https://tpf-backend.onrender.com`. **Save this.**

8. Test: visit `https://tpf-backend.onrender.com/` — should return `{"status":"ok",...}`

---

## Step 4 — Vercel (Frontend, ~5 min)

1. Go to [vercel.com](https://vercel.com) → sign in with GitHub
2. **Add New → Project** → pick your `com-chatbot` repo
3. Settings:
   - **Framework preset**: Vite (auto-detected)
   - **Root directory**: `frontend`
   - **Build command**: `npm run build` (auto)
   - **Output directory**: `dist` (auto)

4. **Environment Variables** — add this one:

   | Key | Value |
   |---|---|
   | `VITE_API_URL` | `https://tpf-backend.onrender.com` (your Render URL from Step 3) |

5. Click **Deploy**. Takes ~2 min.

6. When done, copy your URL — looks like `https://com-chatbot-xxx.vercel.app`. **Save this.**

---

## Step 5 — Update CORS in Render (~2 min)

Now that you have your Vercel URL, allow it on the backend:

1. Go to Render → your backend service → **Environment**
2. Edit `CORS_ORIGINS`:
   ```
   http://localhost:5173,https://com-chatbot-xxx.vercel.app
   ```
   (your actual Vercel URL)
3. Edit `RESET_LINK_BASE`:
   ```
   https://com-chatbot-xxx.vercel.app/reset-password
   ```
4. Click **Save Changes** — Render auto-restarts the service

---

## Step 6 — Test end-to-end

1. Open your Vercel URL
2. Sign in as admin: `abhay@theproductfolks.com` / `admin@1234`
3. Add an employee
4. Sign out, sign in as that employee
5. Start today's conversation
6. Verify the chat works end-to-end

If the **first request takes 30 seconds**, that's expected — Render free tier spins down after 15 min of inactivity. Subsequent requests are instant.

---

## Optional polish

### Custom domain (free on both Vercel and Render)
- Vercel: Settings → Domains → add `app.theproductfolks.com`
- Render: Settings → Custom Domain → add `api.theproductfolks.com`
- Update CORS_ORIGINS and VITE_API_URL accordingly

### Real password reset emails
Currently, reset links print to Render's logs. To send real emails:
- Sign up for [SendGrid](https://sendgrid.com) (100 emails/day free)
- Get API key
- Update `backend/routers/auth.py` `forgot_password()` to call SendGrid instead of `print(link)`

### Keep the backend warm (avoid cold starts)
Free option: use [UptimeRobot](https://uptimerobot.com) — set up a 5-min HTTPS check on your Render URL. Keeps the dyno awake during business hours.

---

## Common issues

**"CORS error" in browser console**
Your Vercel URL isn't in `CORS_ORIGINS`. Fix in Render → Environment.

**"Failed to fetch" / network error on login**
`VITE_API_URL` is wrong on Vercel. Should be your Render URL with `https://` and no trailing slash.

**Backend won't start, "no module named 'psycopg2'"**
Verify `psycopg2-binary` is in `backend/requirements.txt` and Render has rebuilt.

**Login works locally but not in prod**
JWT_SECRET differs between local and prod. Tokens issued locally won't work in prod. Sign in fresh.

---

## Files this deploy uses

- `frontend/vercel.json` — SPA rewrites (so `/training` etc. don't 404 on refresh)
- `frontend/.env.example` — template for `VITE_API_URL`
- `backend/.env.example` — template for all backend env vars
- `backend/requirements.txt` — includes `psycopg2-binary` for Postgres
- `backend/main.py` — CORS reads from `CORS_ORIGINS` env var
- `backend/routers/auth.py` — reset links use `RESET_LINK_BASE` env var
