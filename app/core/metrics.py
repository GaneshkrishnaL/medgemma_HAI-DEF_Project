import json
import time
from pathlib import Path

LOG_PATH = Path("metrics_log.jsonl")

def log_event(event: dict):
    event = dict(event)
    event["ts"] = time.time()
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def has_required_sections(text: str) -> bool:
    required = [
        "Plain-language summary",
        "Questions to ask a doctor",
        "Red flags",
        "What this is based on",
    ]
    t = text.lower()
    return all(r.lower() in t for r in required)

def groundedness_proxy(answer: str, pasted_text: str | None) -> float:
    """
    Very simple proxy: if user provided text, do we quote it / reference it?
    (You can replace this later with a stronger rubric or judge model.)
    """
    if not pasted_text or not pasted_text.strip():
        return 1.0
    return 1.0 if ("USER-PROVIDED" in answer or "based on" in answer.lower() or '"' in answer) else 0.0
