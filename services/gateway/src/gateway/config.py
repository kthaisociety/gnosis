import os
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# Also try root of monorepo if not found (or just load again)
root_env = Path(__file__).parent.parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=root_env)

logger = logging.getLogger("gateway.config")

class Config:
    # -- Core --
    TITLE: str = os.getenv("TITLE", "The Gnosis API")
    PROD: bool = os.getenv("PROD", "false").lower() == "true"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    LOGGING_LEVEL: str = os.getenv("LOGGING_LEVEL", "INFO")

    # -- gRPC / VLM Server --
    SERVER_IP: str = os.getenv("SERVER_IP", "127.0.0.1")
    GRPC_PORT: str = os.getenv("GRPC_PORT", "50051")

    # -- Redis Queue --
    QUEUE_ENABLED: bool = os.getenv("QUEUE_ENABLED", "false").lower() == "true"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    QUEUE_KEY: str = os.getenv("QUEUE_KEY", "jobs")
    MAX_QUEUE_SIZE: int = int(os.getenv("MAX_QUEUE_SIZE", "100"))
    RESULT_PREFIX: str = os.getenv("RESULT_PREFIX", "result_")
    JOB_TIMEOUT_S: int = int(os.getenv("JOB_TIMEOUT_S", "480"))
    RESULT_TTL_SECONDS: int = int(os.getenv("RESULT_TTL_SECONDS", "120"))
    RESULT_POLL_INTERVAL_S: float = float(os.getenv("RESULT_POLL_INTERVAL_S", "0.02"))

    # -- Rate Limiting --
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", str(QUEUE_ENABLED)).lower() == "true"
    RATE_LIMIT_PER_IP_PER_MIN: int = int(os.getenv("RATE_LIMIT_PER_IP_PER_MIN", "10"))
    RATE_LIMIT_GLOBAL_PER_MIN: int = int(os.getenv("RATE_LIMIT_GLOBAL_PER_MIN", "60"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

    # -- Modal --
    MODAL_TOKEN_ID: Optional[str] = os.getenv("MODAL_TOKEN_ID")
    MODAL_TOKEN_SECRET: Optional[str] = os.getenv("MODAL_TOKEN_SECRET")

    # -- Image Handling --
    MAX_IMAGE_SIZE_BYTES: int = int(os.getenv("MAX_IMAGE_SIZE_BYTES", "20971520"))

    @classmethod
    def validate(cls):
        """Validate critical environment variables and log them."""
        logger.info("--- Gateway Configuration ---")
        logger.info(f"TITLE: {cls.TITLE}")
        logger.info(f"HOST: {cls.HOST}")
        logger.info(f"PORT: {cls.PORT}")
        logger.info(f"WORKERS: {cls.WORKERS}")
        logger.info(f"LOGGING_LEVEL: {cls.LOGGING_LEVEL}")
        logger.info(f"SERVER_IP: {cls.SERVER_IP}")
        logger.info(f"GRPC_PORT: {cls.GRPC_PORT}")
        logger.info(f"QUEUE_ENABLED: {cls.QUEUE_ENABLED}")
        
        if cls.QUEUE_ENABLED:
            logger.info(f"REDIS_URL: {cls.REDIS_URL}")
            logger.info(f"QUEUE_KEY: {cls.QUEUE_KEY}")
            logger.info(f"MAX_QUEUE_SIZE: {cls.MAX_QUEUE_SIZE}")
        
        logger.info(f"RATE_LIMIT_ENABLED: {cls.RATE_LIMIT_ENABLED}")
        if cls.RATE_LIMIT_ENABLED:
            logger.info(f"RATE_LIMIT_PER_IP_PER_MIN: {cls.RATE_LIMIT_PER_IP_PER_MIN}")
            logger.info(f"RATE_LIMIT_GLOBAL_PER_MIN: {cls.RATE_LIMIT_GLOBAL_PER_MIN}")

        if not cls.MODAL_TOKEN_ID or not cls.MODAL_TOKEN_SECRET:
            logger.warning("MODAL_TOKEN_ID or MODAL_TOKEN_SECRET not set. Modal runner will fail if used.")
        else:
            logger.info("Modal credentials found.")

        logger.info(f"MAX_IMAGE_SIZE_BYTES: {cls.MAX_IMAGE_SIZE_BYTES}")
        logger.info("-----------------------------")

# Initialize and validate
config = Config()
config.validate()
