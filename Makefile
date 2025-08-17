# Makefile

# Target: run tests
test:
	pytest -q --maxfail=1 --disable-warnings -v

# Target: start API locally
run:
	uvicorn main:app --reload --port 8000

worker:
	rq worker agentic --url "$$REDIS_URL"


# Target: bring up infra (mongo + redis + mongo-express)
infra:
	docker compose up -d mongo redis mongo-express

# Target: stop infra
down:
	docker compose down
