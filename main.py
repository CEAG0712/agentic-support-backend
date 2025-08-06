from fastapi import FastAPI
from models import HealthResponse

app = FastAPI()

@app.get('/health', response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse(message="Agentic Backend Up and Running")