Production-style FastAPI service used to learn backend architecture (API + async jobs + Mongo + Redis).

## Quickstart
1) Create venv and install deps:
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   cp .env.example .env  # configure if needed

2) (Infra will be started later in Step 3 when Mongo is wired.)

3) Run tests (will be added by Day 5):
   pytest -q

## Conventions
- Python 3.11, pinned dependencies
- Twelve-Factor config via environment variables
- Small, atomic commits; descriptive messages

# Agentic Support Backend

A production-style FastAPI service that powers a minimal AI-driven support ticket system.  
Implements ticket creation, async classification jobs (Redis + RQ), MongoDB persistence, and job status queries.

---

## Quickstart (10 minutes to green)

### 1. Clone & setup
```bash
git clone https://github.com/<your-username>/agentic-support-backend.git
cd agentic-support-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

2. Start infra (Mongo, Redis, Mongo Express)

docker compose up -d mongo redis mongo-express

3. Run the API (auto-reloads on code change)
uvicorn main:app --reload --port 8000

Health: http://localhost:8000/health → {"message":"ok"}

DB health: http://localhost:8000/health/db

Queue health: http://localhost:8000/health/queue

4. Run the worker (in a separate terminal)
source .venv/bin/activate
rq worker agentic --url "$REDIS_URL"

5. Test the flow
# Create a ticket
curl -X POST http://localhost:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{"subject":"Reset link expired","description":"Cannot log in"}'

# Response
{"ticket_id":"...","job_id":"...","status":"queued"}

# Query job status
curl http://localhost:8000/jobs/<job_id>

# Get ticket (after worker runs)
curl http://localhost:8000/tickets/<ticket_id>

6. Run tests

pytest -q

