"""Persistent memory store for SkyVault.

Conflict rule: each memory key is unique and the latest write wins.
If the same key is stored again with a different value, the newer value replaces the older one.
This keeps the memory file deterministic and prevents duplicate conflicting facts from piling up.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

MEMORY_PATH = Path(__file__).with_name("memory.json")


def _load_memory() -> Dict[str, Dict[str, Any]]:
    if not MEMORY_PATH.exists():
        return {}
    try:
        with MEMORY_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return {}
    if isinstance(data, dict):
        return {str(key): value for key, value in data.items() if isinstance(value, dict)}
    return {}


def _save_memory(data: Dict[str, Dict[str, Any]]) -> None:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    print (f"Saving memory to {MEMORY_PATH} with {len(data)} entries.")
    with MEMORY_PATH.open("a", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def clear_memory() -> None:
    _save_memory({})


def remember(key: str, value: Any, source: str = "user") -> Dict[str, Any]:
    normalized_key = str(key).strip()
    if not normalized_key:
        raise ValueError("Memory key cannot be empty.")

    memory = _load_memory()
    memory[normalized_key] = {
        "value": value,
        "source": str(source or "unknown"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_memory(memory)
    return {
        "status": "ok",
        "key": normalized_key,
        "value": value,
        "source": str(source or "unknown"),
    }


def recall(query: str) -> Dict[str, Any]:
    query_text = (query or "").strip()
    if not query_text:
        return {}

    query_lower = query_text.lower()
    for key, entry in _load_memory().items():
        if not isinstance(entry, dict):
            continue
        value = str(entry.get("value", ""))
        key_lower = str(key).lower()
        value_lower = value.lower()
        if (
            query_lower == key_lower
            or query_lower in key_lower
            or key_lower in query_lower
            or query_lower == value_lower
            or ("terminal" in query_lower and "terminal" in key_lower and query_lower.split() == ["terminal"])
        ):
            return {
                "key": key,
                "value": entry.get("value"),
                "source": entry.get("source", "unknown"),
                "updated_at": entry.get("updated_at"),
            }
    return {}


def get_memory_snapshot() -> Dict[str, Dict[str, Any]]:
    return _load_memory()


def load_memory_summary() -> str:
    entries = _load_memory()
    if not entries:
        return "No remembered facts yet."

    lines = ["Stored facts from previous runs:"]
    for key, entry in entries.items():
        if not isinstance(entry, dict):
            continue
        value = entry.get("value")
        source = entry.get("source", "unknown")
        lines.append(f"- {key}: {value} (source: {source})")
    return "\n".join(lines)
