from fastapi import FastAPI, HTTPException
from bson import ObjectId
from models import HealthResponse, TicketCreate, TicketOut
from database import ticket_collection
from models import TicketCreate, TicketOut

app = FastAPI()

@app.get('/health', response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse(message="Agentic Backend Up and Running")

@app.post("/ticket", response_model=TicketOut)
async def create_ticket(ticket: TicketCreate):
    ticket_dict = ticket.model_dump()
    result = await ticket_collection.insert_one(ticket_dict)
    return TicketOut(id=str(result.inserted_id), **ticket_dict)

@app.get("/ticket/{id}", response_model=TicketOut)
async def get_ticket(id: str):
    ticket = await ticket_collection.find_one({"_id": ObjectId(id)})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketOut(id=str(ticket["_id"]), **ticket)

