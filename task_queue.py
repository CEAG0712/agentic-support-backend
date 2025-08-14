import os
from dotenv import load_dotenv
from redis import Redis
from rq import Queue

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis = Redis.from_url(REDIS_URL)

def get_job_queue() -> Queue:
    """
    Accessor used by app lifespan to wire deps.job_queue.
    Keeping creation here centralizes configuration and keeps handlers clean.
    """
    return Queue("agentic", connection=_redis)