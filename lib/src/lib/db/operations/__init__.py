# Import functions from the sibling files relative to this folder
from .users import get_user_id

# (Optional but good practice) Explicitly define what is exported
__all__ = [
    "get_user_id",
]
