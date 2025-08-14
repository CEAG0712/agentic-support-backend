import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "ticketing")

_client = MongoClient(MONGO_URI)

_db = _client[DB_NAME]
tickets = _db["tickets"]

_RULES = [
    ("auth", ("login", "password", "reset", "2fa", "otp")),
    ("billing", ("payment", "invoice", "refund", "charge", "card")),
    ("account", ("profile", "email", "username", "account")),
]

def _classify_text(subject: str, description:str) -> str:
    text = f"{subject} {description}".lower()
    
    for label, keywords in _RULES:
        if any(k in text for k in keywords):
            return label
    
    return "general"

def classify_ticket(ticket_id: str) -> dict:
        """
    Worker entrypoint. Given a string id:
    1) Load the ticket
    2) Compute classification
    3) Update status, classification, updated_at
    4) Return a small result payload (visible in job.result)
    """
        oid = ObjectId(ticket_id)

        doc = tickets.find_one({"_id":oid})
        if not doc:
             return {"ok":False, "reason":"not_found", "ticket_id": ticket_id}
        
        label = _classify_text(doc.get("subject", ""), doc.get("description", ""))

        now = datetime.now(timezone.utc)
        update = {
             "$set":{
                  "status":"classified",
                  "classification": label,
                  "updated_at": now
             }
        }

        tickets.update_one({"_id":oid}, update)

        return {"ok":True, "ticket_id":ticket_id, "classification":label}