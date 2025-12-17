# CRUD operations for neondb
from ..client import get_db_pool


###### EXAMPLE ###########
def get_user_id(user_id):
    pool = get_db_pool()

    with pool.connection() as conn:
        with conn.cursor as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id))
            return cur.fetchone()
