from lib.models.vlm import TableOutput
from lib.utils.log import get_logger

logger = get_logger(__name__)


def get_schema(schema_name: str | None):
    if not schema_name:
        return None
    elif schema_name == "TableOutput":
        return TableOutput
    logger.warn(f"schema {schema_name} not found")
    return None