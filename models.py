from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class HealthResponse(BaseModel):
    message: str

class TicketCreate(BaseModel):
    subject: str
    description: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class TicketOut(TicketCreate):
    id: str