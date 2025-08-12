from fastapi import FastAPI

app = FastAPI(title="Agentic Support Backend")

@app.get("/health")
def healt():
    return {"message": "Agentic Support Backend up and running"}