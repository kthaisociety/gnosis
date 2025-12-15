# Expose the connection pool getter
from .client import get_db_pool

# Expose the CRUD operations via import from .operations
## Can now be imported with from "lib.db import get_user_id" for easier imports
from .operations import get_user_id

__all__ = ["get_db_pool", "get_user_id"]
