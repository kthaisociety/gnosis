import os
import psycopg
from dotenv import load_dotenv
from .log import get_logger

load_dotenv()
logger = get_logger(__name__)


class DB:
    def __init__(self, conn_str: str = None):
        self.conn_str = conn_str or os.getenv("DATABASE_URL")

    def test_connection(self) -> bool:
        try:
            with psycopg.connect(self.conn_str) as conn:
                conn.execute("SELECT 1")
            logger.info("Database test connection sucessful!")
            return True
        except Exception as e:
            logger.error(f"Could not connect to database ({e})")
            return False
