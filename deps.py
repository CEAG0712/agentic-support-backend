from typing import Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from rq import Queue

ticket_collection: Optional[AsyncIOMotorCollection] = None
job_queue: Optional[Queue] = None
