import json
from typing import List, Union

from lib.models.vlm import TableOutput


# Convert VLM output (JSON) to 2D table format for metrics
def parse_vlm_output_to_table(
    json_str: str, schema_name: str
) -> List[List[Union[str, float]]]:
    if schema_name == "TableOutput":
        data = json.loads(json_str)
        output = TableOutput(**data)
        return vlm_table_output_to_table(output)
    raise ValueError(f"Unknown schema: {schema_name}")


# Convert TableOutput to 2D table
# Format:
# [
#   ["x_label", "y_label"],
#   ["x1", y1],
#   ["x2", y2],
#   ...
# ]
def vlm_table_output_to_table(output: TableOutput) -> List[List[Union[str, float]]]:
    x_label = output.x_label or "x"
    y_label = output.y_label or "y"
    table = [[x_label, y_label]]
    for point in output.data:
        table.append([f"{point.x:g}", point.y])
    return table
