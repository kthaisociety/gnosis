from eval.db import create_dataset
from lib.db import close_db_pool

try:
    create_dataset("example")
finally:
    close_db_pool()
