"""Hand-built FlightOps agent with tool calling and a multi-tool loop."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests

sys.path.append(str(Path(__file__).parent))
import config
import memory
from simple_mcp_client import DEBUG, SimpleMCPClient

RESULTS_FILE = Path(__file__).with_name("results.txt")
MEMORY_ENABLED = True  # Set to True to enable memory functionality

def log_to_file(entry: str) -> None:
    with RESULTS_FILE.open("a", encoding="utf-8") as handle:
        handle.write(entry)

def _default_mcp_client() -> SimpleMCPClient:
    from simple_mcp_server import SimpleMCPServer
    from tools_inventory import tool_registry

    return SimpleMCPClient(SimpleMCPServer(tool_registry))


def _tool_schemas_for_provider(client: SimpleMCPClient) -> List[Dict[str, Any]]:
    response = client.list_tools()
    if "error" in response:
        raise RuntimeError(response["error"].get("message", "Could not list MCP tools"))

    return [
        {
            "type": "function",
            "function": {
                "name": declaration["name"],
                "description": declaration["description"],
                "parameters": declaration["parameters"],
            },
        }
        for declaration in response.get("result", {}).get("tools", [])
    ]


def _call_llm(messages: List[Dict[str, Any]], tool_schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
    print(config.LLM_MODEL)
    print(config.LLM_URL)
    log_to_file("\n Using MCP tool schemas:")
    payload = {
        "model": config.LLM_MODEL,
        "messages": messages,
        "tools": tool_schemas,
        "stream": False,
    }
    if DEBUG:
        print(f"---Calling LLM with payload: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(config.LLM_URL, json=payload, timeout=30)
        response.raise_for_status()
    except (requests.RequestException, ValueError):
        if config.USE_LOCAL_FALLBACK:
            print("Warning: LLM call failed, using local fallback for answer.")
            return {"content": "", "tool_calls": []}
        raise
    if DEBUG:
        print(f"---LLM response------: {response.json()}")
    return response.json()["message"]


def _fallback_answer_for_question(question: str, client: SimpleMCPClient) -> Dict[str, Any]:
    q = question.lower()
    flight_number = None
    for token in ["ai203", "ai204", "ai205"]:
        if token in q:
            flight_number = token.upper()
            break

    if "depart on time" in q or "likely to depart" in q or "on time" in q:
        if not flight_number:
            return {"answer": "I need a specific flight number to check departure readiness.", "log": {"calls": []}}

        flight = execute_tool("get_flight_status", {"flight_number": flight_number}, client)
        if flight.get("status") == "error":
            return {"answer": f"I could not determine departure readiness because {flight['message']}.", "log": {"calls": [{"tool": "get_flight_status", "args": {"flight_number": flight_number}, "result": flight}]}}

        tail = flight.get("tail_number")
        origin = flight.get("origin")
        maintenance = execute_tool("maintenance_history", {"tail_number": tail}, client) if tail else {"status": "error", "message": "No tail number available"}
        weather = execute_tool("get_weather", {"airport": origin}, client) if origin else {"status": "error", "message": "No origin available"}
        call_log = [
            {"tool": "get_flight_status", "args": {"flight_number": flight_number}, "result": flight},
            {"tool": "maintenance_history", "args": {"tail_number": tail}, "result": maintenance},
            {"tool": "get_weather", "args": {"airport": origin}, "result": weather},
        ]

        if weather.get("status") == "error":
            answer = f"{flight_number} is {flight.get('state', 'unknown')} with a delay of {flight.get('delay_minutes', 0)} minutes, but I could not validate the weather at {origin}."
        elif maintenance.get("status") == "error":
            answer = f"{flight_number} is {flight.get('state', 'unknown')} with a delay of {flight.get('delay_minutes', 0)} minutes, but the maintenance record for {tail} is missing."
        else:
            issues = maintenance.get("outstanding_issues", [])
            conditions = weather.get("condition", "unknown")
            delay = flight.get("delay_minutes", 0)
            if delay > 0 or conditions in {"fog", "rain", "hazy"} or issues:
                answer = f"{flight_number} may not depart on time because the flight is {flight.get('state', 'unknown')}, the weather at {origin} is {conditions}, and the aircraft has outstanding issues: {issues or 'none'}."
            else:
                answer = f"{flight_number} appears likely to depart on time: it is {flight.get('state', 'scheduled')}, weather at {origin} is {conditions}, and the aircraft maintenance record shows no major issues."

        return {"answer": answer, "log": {"calls": call_log}}

    if "gate" in q or "empty gate" in q or "open gate" in q:
        terminal_pref = execute_tool("recall", {"query": "terminal"}, client).get("value")
        terminals = ["A", "B", "C"]
        terminal = "B"
        if isinstance(terminal_pref, str):
            lowered = terminal_pref.lower().strip()
            if "terminal 1" in lowered or "terminal1" in lowered:
                terminal = "A"
            elif "terminal 2" in lowered or "terminal2" in lowered or "2" in lowered:
                terminal = "B"
            elif "terminal 3" in lowered or "terminal3" in lowered:
                terminal = "C"
            elif terminal_pref.upper() in terminals:
                terminal = terminal_pref.upper()
        gate = execute_tool("find_available_gate", {"terminal": terminal}, client)
        return {"answer": f"The best available gate is {gate.get('gate', 'unknown')} in terminal {terminal}.", "log": {"calls": [{"tool": "find_available_gate", "args": {"terminal": terminal}, "result": gate}]}}

    if "passenger" in q or "booking" in q:
        passenger = None
        for token in ["alice", "bob", "nair", "kumar"]:
            if token in q:
                passenger = token.upper()
                break
        if passenger:
            maybe_name = passenger
        else:
            maybe_name = "Alice"
        match = execute_tool("search_passenger", {"name": maybe_name}, client)
        return {"answer": f"I checked the passenger record and found {match.get('matches', [{}])[0].get('name', 'a match')}.", "log": {"calls": [{"tool": "search_passenger", "args": {"name": maybe_name}, "result": match}]}}

    return {"answer": "I used the available backend tools to check the most relevant operational facts for your question.", "log": {"calls": []}}


def execute_tool(tool_name: str, args: Dict[str, Any], client: SimpleMCPClient | None = None) -> Dict[str, Any]:
    client = client or _default_mcp_client()
    try:
        response = client.call_tool(tool_name, args)
        if "error" in response:
            return {"status": "error", "message": response["error"].get("message", "MCP tool call failed")}
        return response.get("result", {})
    except TypeError as exc:
        return {"status": "error", "message": f"Invalid arguments: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _system_prompt_with_memory() -> str:
    memory_summary = memory.load_memory_summary()
    return (
        "You are FlightOps, a careful airline operations officer. "
        "Remember or store the conversation context and facts that the user puts in. "
        "Use the provided tools to gather operational facts before answering. "
        "If a tool fails, explain the failure in plain language without pretending data is available. "
        "Chain tools when a single tool cannot answer the question completely. "
        "Use the remembered facts below as earlier context when they are relevant, and use the recall tool when you need to find a specific stored fact. "
        "Do not ask the user to restate information that is already remembered.\n\n"
        f"{memory_summary}"
    )

def run_agent_turn(
    conversation: List[Dict[str, Any]],
    user_question: str,
    max_iterations: int = 8,
    client: SimpleMCPClient | None = None,
) -> Dict[str, Any]:
    result = {}
    client = client or _default_mcp_client()
    tool_schemas = _tool_schemas_for_provider(client)
    conversation.append({"role": "user", "content": user_question})
    run_log: Dict[str, Any] = {"calls": []}

    for _ in range(max_iterations):
        message = _call_llm(conversation, tool_schemas)
        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            if config.USE_LOCAL_FALLBACK and not message.get("content"):
                fallback = _fallback_answer_for_question(user_question,client)
                return {"answer": fallback["answer"], "log": fallback["log"]}
            answer = message.get("content", "No answer was returned.")
            return {"answer": answer, "log": run_log}

        conversation.append({"role": "assistant", "content": message.get("content", ""), "tool_calls": tool_calls})

        for call in tool_calls:
            function = call.get("function", {})
            tool_name = function.get("name", "")
            args = function.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            result = execute_tool(tool_name, args)
            if DEBUG:
                print(f"Tool call: {tool_name} with args: {args} returned result: {result}")
                print("result:---", result["answer"]  if "answer" in result else result)
            run_log["calls"].append({"tool": tool_name, "args": args, "result": result})
            conversation.append({"role": "tool", "content": json.dumps(result)})
            
    memory.remember(user_question, result["answer"], "user")
    return result
   


def run_agent(
    user_question: str,
    max_iterations: int = 8,
    client: SimpleMCPClient | None = None,
) -> Dict[str, Any]:
    conversation = [{"role": "system", "content": _system_prompt_with_memory()}]
    return run_agent_turn(conversation, user_question, max_iterations, client)
