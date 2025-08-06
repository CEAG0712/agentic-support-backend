from fastapi import FastAPI

app = FastAPI()

@app.get('/health')
def read_root():
    return {"message":"Scaffold Agentic Backend"}