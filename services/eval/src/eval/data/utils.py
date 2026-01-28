import json
from typing import List, Union

from lib.models.vlm import VLMTableOutput


# Convert VLM output (JSON) to 2D table format for metrics
def parse_vlm_output_to_table(
    json_str: str, schema_name: str
) -> List[List[Union[str, float]]]:
    if schema_name == "VLMTableOutput":
        data = json.loads(json_str)
        output = VLMTableOutput(**data)
        return vlm_table_output_to_table(output)
    raise ValueError(f"Unknown schema: {schema_name}")


# Convert VLMTableOutput to 2D table
# Format:
# [
#   ["", "y_label"],
#   ["x1", y1],
#   ["x2", y2],
#   ...
# ]
def vlm_table_output_to_table(output: VLMTableOutput) -> List[List[Union[str, float]]]:
    y_label = output.y_label or "y"
    table = [["", y_label]]
    for point in output.data:
        table.append([str(point.x), point.y])
    return table
