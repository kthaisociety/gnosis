import os
import logging

# FastAPI Imports
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from gateway.routers.health_router import router as health_router
from gateway.routers.process_router import router as process_router, start_worker

API_TITLE = os.getenv("API_TITLE", "The Gnosis API")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gateway")

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_worker()
    yield

app = FastAPI(title=API_TITLE, lifespan=lifespan)
app.include_router(health_router)
app.include_router(process_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please check logs."},
    )

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


TITLE = os.getenv("TITLE", "The Gnosis API")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
WORKERS = int(os.getenv("WORKERS", "1"))

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


# (DEV) Run server with reload option
if __name__ == "__main__":
    serve()
    uvicorn.run("server:app", port=8000, reload=True)
