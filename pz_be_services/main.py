from fastapi import FastAPI

app = FastAPI(title="Project Zero Backend Service")


@app.get("/health")
async def health():
    return {"status": "running"}
