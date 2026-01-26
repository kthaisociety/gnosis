import logging
import os
from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from gateway.routers.health_router import router as health_router
from gateway.routers.process_router import (
    router as process_router,
    start_worker,
    QUEUE_ENABLED,
)


from gateway.config import config

TITLE = config.TITLE
HOST = config.HOST
PORT = config.PORT
WORKERS = config.WORKERS

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gateway")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if QUEUE_ENABLED:
        start_worker()
    yield


app = FastAPI(title=TITLE, lifespan=lifespan)
app.include_router(health_router)
app.include_router(process_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    detail = str(exc) or "Internal Server Error. Please check logs."
    return JSONResponse(
        status_code=500,
        content={"detail": detail},
    )


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


def serve() -> None:
    logger.info(f"Starting {TITLE} on {HOST}:{PORT} with {WORKERS} workers")

    uvicorn.run(
        app="gateway.server:app",
        host=HOST,
        port=PORT,
        workers=WORKERS,
        reload=False,
        http="auto",
        loop="auto",
    )


if __name__ == "__main__":
    serve()
