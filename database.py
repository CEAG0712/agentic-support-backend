import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "ticketing")

_client = AsyncIOMotorClient(MONGO_URI)
_db = _client[DB_NAME]

def get_ticket_collection():
    """
    Accessor used by app startup to wire deps.ticket_collection.
    Keeping this as a function helps with testing and future refactors.
    """
    return _db["tickets"]  

async def ping_db() -> bool:
    """
    Lightweight readiness check so we can prove Mongo is reachable.
    """
    try:
        await _client.admin.command("ping")
        return True
    except Exception:
        return False