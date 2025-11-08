from fastapi import FastAPI
import asyncio
from app.api.routes import router
from app.workers.sync_worker import run_sync_worker

app = FastAPI(title="Permissions Service")
app.include_router(router)

_stop_event: asyncio.Event | None = None
_worker_task: asyncio.Task | None = None


@app.on_event("startup")
async def startup_event():
    global _stop_event, _worker_task
    _stop_event = asyncio.Event()
    _worker_task = asyncio.create_task(run_sync_worker(_stop_event))


@app.on_event("shutdown")
async def shutdown_event():
    global _stop_event, _worker_task
    if _stop_event:
        _stop_event.set()
    if _worker_task:
        try:
            await _worker_task
        except Exception:
            pass
