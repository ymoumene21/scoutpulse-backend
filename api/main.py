from fastapi import FastAPI

# FastAPI() creates the application object — this is the thing uvicorn runs.
app = FastAPI()

# async def: this function can be paused/resumed by the event loop.
# It doesn't need to await anything yet (no DB, no network) — but declaring
# it async now means it'll integrate cleanly once it does.
@app.get("/health")
async def health_check():
    return {"status": "ok"}