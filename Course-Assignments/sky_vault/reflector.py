"""Post-run reflective assessment of the agent's performance."""

from __future__ import annotations

from typing import Any, Dict, List


def reflect(run_log: Dict[str, Any]) -> Dict[str, Any]:
    calls = run_log.get("calls", [])
    called_tools = [call["tool"] for call in calls]
    unnecessary_calls = []
    seen = set()
    for call in calls:
        tool_name = call["tool"]
        if tool_name in seen:
            unnecessary_calls.append(tool_name)
        seen.add(tool_name)

    missing_information = []
    for call in calls:
        result = call.get("result", {})
        if result.get("status") == "error":
            missing_information.append({"tool": call["tool"], "error": result.get("message")})

    confidence = "high"
    if len(calls) > 3:
        confidence = "medium"
    if any(call.get("result", {}).get("status") == "error" for call in calls):
        confidence = "medium"
    if len(calls) > 5:
        confidence = "low"

    reflection = {
        "called_tools": called_tools,
        "unnecessary_calls": unnecessary_calls,
        "missing_information": missing_information,
        "confidence": confidence,
    }

    text = (
        f"Called tools: {called_tools}. "
        f"Unnecessary calls: {unnecessary_calls}. "
        f"Missing information: {missing_information}. "
        f"Confidence: {confidence}."
    )
    return {"reflection": reflection, "text": text}
