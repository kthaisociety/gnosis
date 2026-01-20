import logging
import os
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from gateway.routers.health_router import router as health_router
from gateway.routers.process_router import router as process_router

# TODO:
# ADD CONFIG
# FIX STYLING
# MISCS ROUTES (HEALTH CHECK, METRICS, AUTH, ETC.)
# Reconnect / Develop Logging
# Sanitize image filenames

# ISSUE: Debate to memory or to disk (leaning towards memory), implement request size limit (middleware w/ MAX_IMAGE_BYTES constant)
# Use logging.getLogger() instead of print
# ISSUE: Add catch exceptions mapped to appropriate 4xx/5xx codes for process_and_validate_image_bytes or query_vlm

# ISSUE: Add general error handling!!!!!!!

# Consider "response_model_exclude_none=True,", to omit None values in returned POST request JSON

# ProcessResponseFormat(**result) to skip FastAPi JSON serialization, RUN TIME OPTIMIZATION ;)

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

app = FastAPI(title=TITLE)
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
