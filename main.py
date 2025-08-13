from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uuid
from models import HealthResponse, TicketCreate


app = FastAPI(title="Agentic Support Backend")

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

@app.get("/health")
def healt():
    return {"message": "Agentic Support Backend up and running"}


@app.post("/tickets")
async def preview_create_ticket(ticket:TicketCreate):
    return {"received":True, "ticket":ticket.model_dump()}