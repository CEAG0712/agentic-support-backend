from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uuid
from models import HealthResponse, TicketCreate
import deps
from database import get_ticket_collection, ping_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app:FastAPI):
    deps.ticket_collection = get_ticket_collection()
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

@app.post("/tickets")
async def preview_create_ticket(ticket:TicketCreate):
    return {"received":True, "ticket":ticket.model_dump()}