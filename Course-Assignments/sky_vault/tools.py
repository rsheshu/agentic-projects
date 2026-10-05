"""Plain Python tool implementations for FlightOps.
1. Defines the tool functions that can be called by the FlightOps agent.
2. Each tool function returns a dictionary with a "status" key and other relevant information.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from data import Aircraft, Flights, Maintenance, Passengers, Weather
import memory

ToolFunction = Callable[..., Dict[str, Any]]
TOOL_REGISTRY: Dict[str, ToolFunction] = {}


def register_tool(function: ToolFunction) -> ToolFunction:
    TOOL_REGISTRY[function.__name__] = function
    return function


@register_tool
def get_flight_status(flight_number: str) -> Dict[str, Any]:
    flight = Flights.get(flight_number)
    if not flight:
        return {"status": "error", "message": f"Flight {flight_number} not found"}
    return {
        "status": "ok",
        "flight_number": flight["flight_number"],
        "state": flight["status"],
        "gate": flight["gate"],
        "departure_time": flight["departure_time"],
        "delay_minutes": flight.get("delay_minutes", 0),
        "tail_number": flight.get("tail_number"),
        "origin": flight.get("origin"),
        "destination": flight.get("destination"),
    }


@register_tool
def search_passenger(name: str) -> Dict[str, Any]:
    matches = [p for p in Passengers if name.lower() in p["name"].lower()]
    if not matches:
        return {"status": "error", "message": f"Passenger {name} not found"}
    return {"status": "ok", "matches": matches}


@register_tool
def maintenance_history(tail_number: str) -> Dict[str, Any]:
    maintenance = Maintenance.get(tail_number)
    if not maintenance:
        return {"status": "error", "message": f"Tail number {tail_number} not found"}
    return {"status": "ok", "tail_number": tail_number, **maintenance}


@register_tool
def find_available_gate(terminal: str = "A") -> Dict[str, Any]:
    terminal_key = (terminal or "A").strip()
    normalized = terminal_key.upper()
    if normalized.startswith("TERMINAL "):
        normalized = normalized.replace("TERMINAL ", "")
    if normalized in {"1", "A"}:
        terminal_code = "A"
    elif normalized in {"2", "B"}:
        terminal_code = "B"
    elif normalized in {"3", "C"}:
        terminal_code = "C"
    else:
        terminal_code = normalized[:1] if normalized else "A"

    used = {flight["gate"] for flight in Flights.values()}
    candidates = [f"{terminal_code}{i:02d}" for i in range(1, 30)]
    for gate in candidates:
        if gate not in used:
            return {"status": "ok", "gate": gate, "terminal": terminal_code}
    return {"status": "error", "message": f"No available gate in terminal {terminal_code}"}


@register_tool
def get_weather(airport: str) -> Dict[str, Any]:
    if airport == "ERR":
        return {"status": "error", "message": "Weather service unavailable"}
    weather = Weather.get(airport)
    if not weather:
        return {"status": "error", "message": f"Weather for airport {airport} not found"}
    return {"status": "ok", "airport": airport, **weather}


@register_tool
def lookup_aircraft(ac_type: str) -> Dict[str, Any]:
    aircraft = Aircraft.get(ac_type)
    if not aircraft:
        return {"status": "error", "message": f"Aircraft type {ac_type} not found"}
    return {"status": "ok", **aircraft}


@register_tool
def remember(key: str, value: Any, source: str = "system") -> Dict[str, Any]:
    return memory.remember(key, value, source)


@register_tool
def recall(query: str) -> Dict[str, Any]:
    return memory.recall(query)


def list_tools() -> List[str]:
    return list(TOOL_REGISTRY)
