from typing import Callable, Dict, Any, List
import json

import memory
from data import Aircraft, Flights, Maintenance, Passengers, Weather
from tools_registry import ToolDescription, ToolRegistry

tool_registry = ToolRegistry()

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


def search_passenger(name: str) -> Dict[str, Any]:
    matches = [p for p in Passengers if name.lower() in p["name"].lower()]
    if not matches:
        return {"status": "error", "message": f"Passenger {name} not found"}
    return {"status": "ok", "matches": matches}


def maintenance_history(tail_number: str) -> Dict[str, Any]:
    maintenance = Maintenance.get(tail_number)
    if not maintenance:
        return {"status": "error", "message": f"Tail number {tail_number} not found"}
    return {"status": "ok", "tail_number": tail_number, **maintenance}


def get_weather(airport: str) -> Dict[str, Any]:
    if airport == "ERR":
        return {"status": "error", "message": "Weather service unavailable"}
    weather = Weather.get(airport)
    if not weather:
        return {"status": "error", "message": f"Weather for airport {airport} not found"}
    return {"status": "ok", "airport": airport, **weather}


def lookup_aircraft(ac_type: str) -> Dict[str, Any]:
    aircraft = Aircraft.get(ac_type)
    if not aircraft:
        return {"status": "error", "message": f"Aircraft type {ac_type} not found"}
    return {"status": "ok", **aircraft}


def remember(key: str, value: Any, source: str = "system") -> Dict[str, Any]:
    return memory.remember(key, value, source)


def recall(query: str) -> Dict[str, Any]:
    return memory.recall(query)


tool_registry.register_tools(
    [
        ToolDescription(
            name="find_available_gate",
            description="Find a currently unused gate number in a requested terminal, such as A or B, for a flight assignment.",
            parameters={
                "type": "object",
                "properties": {
                    "terminal": {
                        "type": "string",
                    "description": "Terminal letter such as A, B, or C. Defaults to A if omitted.",
                }
            },
            "required": [],
        },
            handler=find_available_gate,
        ),
        ToolDescription(
            name="get_flight_status",
            description="Return the current operational status, gate, departure time, delay, and tail number for a specific flight number such as AI203.",
            parameters={
                "type": "object",
                "properties": {
                    "flight_number": {
                        "type": "string",
                        "description": "Flight number code, for example AI203 or AI204.",
                    }
                },
                "required": ["flight_number"],
            },
            handler=get_flight_status,
        ),
        ToolDescription(
            name="search_passenger",
            description="Find a passenger by full or partial name and return their booking reference, seat, and flight to support customer-service queries.",
            parameters= {
                "type": "object",
                "properties": {
                "name": {
                    "type": "string",
                    "description": "The passenger name or partial name to search for",
                }
            },
             "required": ["name"],
            },
            handler=search_passenger,
        ),
        ToolDescription(
            name="maintenance_history",
            description= "Return the last inspection date, total hours flown, and any outstanding maintenance issues for a specific aircraft tail number.",
            parameters =  {
            "type": "object",
            "properties": {
                "tail_number": {
                    "type": "string",
                    "description": "Aircraft tail number such as VT-ABC.",
                }
            },
            "required": ["tail_number"],
        },
            handler=maintenance_history,
        ),
        ToolDescription(
            name="get_weather",
            description="Return airport weather conditions including visibility, wind, temperature, and condition for an airport code such as DEL or BOM.",
            parameters= {
            "type": "object",
            "properties": {
                "airport": {
                    "type": "string",
                    "description": "Airport IATA code such as DEL, BOM, HYD, or BLR.",
                }
            },
            "required": ["airport"],
        },
            handler=get_weather,
        ),
        ToolDescription(
            name="lookup_aircraft",
        description= "Return dimensions, seating capacity, and fuel figures for a specific aircraft type such as A320 or A321.",
        parameters= {
            "type": "object",
            "properties": {
                "ac_type": {
                    "type": "string",
                    "description": "Aircraft type such as A320 or A321.",
                }
            },
            "required": ["ac_type"],
        },
            handler=lookup_aircraft,
        ),
        ToolDescription(
            name="remember",
            description="Store a fact for use in future runs",
            parameters={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The stable name of the fact to remember",
                    },
                    "value": {
                        "type": "object",
                        "description": "The value to store",
                    },
                    "source": {
                        "type": "string",
                        "description": "The origin of the fact",
                    },
                },
                "required": ["key", "value","source"],
            },
            handler=remember,
        ),
        ToolDescription(
            name="recall",
            description="Look up a previously stored fact by key or a text query. Returns the most relevant remembered fact if one matches.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A key name or a short text snippet to find a matching remembered fact.",
                    }
                },
                "required": ["query"],
            },
            handler=recall,
        ),
    ]
)