from pydantic import BaseModel, Field, field_validator
from typing import Optional
from typing_extensions import Annotated
from pydantic import StringConstraints
from datetime import datetime, timezone


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=2000)]

class HealthResponse(BaseModel):
    message: str

class TicketCreate(BaseModel):
    subject: NonEmptyStr
    description: NonEmptyStr
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: Optional[str] = None
    classification: Optional[str] = None
    updated_at: Optional[datetime]=None
    job_id: Optional[str] = None

    @field_validator("created_at", mode="before")
    @classmethod
    def ensure_tz(cls,v):
        if isinstance(v, datetime):
            return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        
        return v
    
class TicketOut(TicketCreate):
    id: str