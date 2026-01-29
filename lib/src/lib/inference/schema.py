from lib.models.vlm import TableOutput


def get_schema(schema_name: str | None):
    if not schema_name:
        return None
    elif schema_name == "TableOutput":
        return TableOutput
    else:
        raise Exception(f"schema {schema_name} not found")
