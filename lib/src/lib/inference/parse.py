import json
import re
from typing import Any, Literal, Tuple

from lib.models.vlm import VLMResponseFormat

VLMFormat = Literal["json", "html", "text"]


def raw_to_text(raw: Any) -> str:
    if hasattr(raw, "model_dump_json"):
        return raw.model_dump_json(exclude_none=True)
    if hasattr(raw, "model_dump"):
        return json.dumps(raw.model_dump(exclude_none=True))
    if isinstance(raw, dict):
        return json.dumps(raw)
    return str(raw)


# Normalize gRPC or Modal output to VLMResponseFormat.
def normalize_vlm_response(raw: Any, inference_time_ms: float) -> VLMResponseFormat:
    if raw is None:
        return VLMResponseFormat(text=None, format=None, inference_time_ms=inference_time_ms)
    text = raw_to_text(raw)
    if not (text and isinstance(text, str) and text.strip()):
        return VLMResponseFormat(text=None, format=None, inference_time_ms=inference_time_ms)
    fmt = detect_format(text)
    return VLMResponseFormat(text=text, format=fmt, inference_time_ms=inference_time_ms)


def detect_format(text: str | None) -> VLMFormat:
    if text is None or not isinstance(text, str):
        return "text"
    s = text.strip()
    if not s:
        return "text"
    try:
        json.loads(s)
        return "json"
    except (json.JSONDecodeError, TypeError):
        pass
    if s.lstrip().lower().startswith("<!doctype") or re.search(
        r"</[a-zA-Z][\w:-]*\s*>", s
    ):
        return "html"
    return "text"


def parse_vlm_text(text: str | None) -> Tuple[VLMFormat, Any]:
    if text is None:
        return ("text", "")
    fmt = detect_format(text)
    if fmt == "json":
        return ("json", json.loads(text.strip()))
    return (fmt, text)
