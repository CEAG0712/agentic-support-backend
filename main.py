from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uuid
from models import HealthResponse, TicketCreate, TicketOut
import deps
from database import get_ticket_collection, ping_db
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from bson import ObjectId                      
from bson.errors import InvalidId    
from task_queue import get_job_queue            


@asynccontextmanager
async def lifespan(app:FastAPI):
    deps.ticket_collection = get_ticket_collection()
    deps.job_queue = get_job_queue()
    yield


app = FastAPI(title="Agentic Support Backend", lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc:RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error":{
                "type":"validation_error",
                "details":exc.errors(),
                "request_id":str(uuid.uuid4())
            }
        }
    )



@app.get("/health", response_model=HealthResponse)
def healt():
    return {"message": "Agentic Support Backend up and running"}

@app.get("/health/db")
async def health_db():
    ok = await ping_db()
    status_code = 200 if ok else 503

    return JSONResponse(status_code=status_code, content={"mongo_ok": ok})

@app.get("/health/queue")
async def health_queue():
    try:
        ok = deps.job_queue.connection.ping()
    except Exception:
        ok = False
    return JSONResponse(status_code=(200 if ok else 503), content={"redis_ok":ok})

@app.post("/tickets")
async def preview_create_ticket(ticket:TicketCreate):
    now = datetime.now(timezone.utc)
    doc = ticket.model_dump()

    doc.update({
        "subject": doc["subject"].strip(),      # normalize: trimmed (constraints already trimmed, this is belt & suspenders)
        "description": doc["description"].strip(),
        "status": "new",                        # lifecycle starts as "new"
        "classification": None,                 # will be filled by the async worker later
        "created_at": now,                      # authoritative server-side timestamp
        "updated_at": None,                     # no updates yet
        "job_id": None                          # will be filled when we enque
    })
    result = await deps.ticket_collection.insert_one(doc)
    ticket_id = str(result.inserted_id)
    return {"ticket_id": ticket_id, "status": "new"}


@app.get("/tickets/{id}", response_model=TicketOut)
async def get_ticket(id:str):
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ticket id format")
    
    doc = await deps.ticket_collection.find_one({"_id":oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)

    return TicketOut(**doc)