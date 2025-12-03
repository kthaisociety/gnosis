import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routers.health_router import router as health_router
from app.routers.process_router import router as process_router

TITLE = os.getenv("TITLE", "The Gnosis API")

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


app = FastAPI(title=TITLE)

# Routers
app.include_router(health_router)
app.include_router(process_router)


# Redirect root URL to docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


def serve() -> None:
    import uvicorn

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))
    WORKERS = int(os.getenv("WORKERS", "1"))

    uvicorn.run(
        app="app.server:app",
        host=HOST,
        port=PORT,
        workers=WORKERS,
        reload=False,
        http="auto",
        loop="auto",
    )


if __name__ == "__main__":
    serve()
