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
