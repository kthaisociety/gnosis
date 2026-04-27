from typing import Optional
import datetime
from fastapi import HTTPException

from ..client import get_db_pool


def create_api_key(name: str, key_hash: str, expires_at: Optional[datetime.datetime]):
    pool = get_db_pool()

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO api_keys (key_hash, name, expires_at)
                            VALUES (%s, %s, %s)
                            RETURNING id, created_at""",
                (key_hash, name, expires_at),
            )
            row = cur.fetchone()
            conn.commit()
            return row


def list_api_keys():
    pool = get_db_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, name, created_at, expires_at, last_used_at, is_active
                       FROM api_keys
                       ORDER BY created_at DESC"""
            )
            rows = cur.fetchall()
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "created_at": row[2],
                    "expires_at": row[3],
                    "last_used_at": row[4],
                    "is_active": row[5],
                }
                for row in rows
            ]


def revoke_api_key(key_id: str):
    pool = get_db_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE api_keys SET is_active = FALSE WHERE id = %s", (key_id,)
            )
            conn.commit()


def get_api_key(key_hash: str):
    pool = get_db_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id FROM api_keys
                         WHERE key_hash = %s AND is_active = TRUE
                         AND (expires_at IS NULL OR expires_at > NOW())""",
                (key_hash,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(
                    status_code=401, detail="Invalid or expired API key"
                )

            cur.execute(
                "UPDATE api_keys SET last_used_at = NOW() WHERE id = %s", (row[0],)
            )
            conn.commit()
            return row[0]
