"""Tool descriptions for the FlightOps agent."""

TOOL_DECLARATIONS = [
    {
        "name": "get_flight_status",
        "description": "Return the current operational status, gate, departure time, delay, and tail number for a specific flight number such as AI203.",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_number": {
                    "type": "string",
                    "description": "Flight number code, for example AI203 or AI204.",
                }
            },
            "required": ["flight_number"],
        },
    },
    {
        "name": "search_passenger",
        "description": "Find a passenger by full or partial name and return their booking reference, seat, and flight to support customer-service queries.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Full or partial passenger name such as Alice or Kumar.",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "maintenance_history",
        "description": "Return the last inspection date, total hours flown, and any outstanding maintenance issues for a specific aircraft tail number.",
        "parameters": {
            "type": "object",
            "properties": {
                "tail_number": {
                    "type": "string",
                    "description": "Aircraft tail number such as VT-ABC.",
                }
            },
            "required": ["tail_number"],
        },
    },
    {
        "name": "find_available_gate",
        "description": "Find a currently unused gate number in a requested terminal, such as A or B, for a flight assignment.",
        "parameters": {
            "type": "object",
            "properties": {
                "terminal": {
                    "type": "string",
                    "description": "Terminal letter such as A, B, or C. Defaults to A if omitted.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_weather",
        "description": "Return airport weather conditions including visibility, wind, temperature, and condition for an airport code such as DEL or BOM.",
        "parameters": {
            "type": "object",
            "properties": {
                "airport": {
                    "type": "string",
                    "description": "Airport IATA code such as DEL, BOM, HYD, or BLR.",
                }
            },
            "required": ["airport"],
        },
    },
    {
        "name": "lookup_aircraft",
        "description": "Return dimensions, seating capacity, and fuel figures for a specific aircraft type such as A320 or A321.",
        "parameters": {
            "type": "object",
            "properties": {
                "ac_type": {
                    "type": "string",
                    "description": "Aircraft type such as A320 or A321.",
                }
            },
            "required": ["ac_type"],
        },
    },
    {
        "name": "remember",
        "description": "Store a fact learned during this run or from the user so it can be used in future runs. The latest value for the same key overwrites the previous one.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Stable fact name such as prefers_terminal or favorite_gate."},
                "value": {"type": "string", "description": "The fact value to persist."},
                "source": {"type": "string", "description": "The origin of the fact, typically 'user' or 'system'."},
            },
            "required": ["key", "value"],
        },
    },
    {
        "name": "recall",
        "description": "Look up a previously stored fact by key or a text query. Returns the most relevant remembered fact if one matches.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A key name or a short text snippet to find a matching remembered fact."}
            },
            "required": ["query"],
        },
    },
]

# A deliberately vague version for comparison in the README.
TOOL_DECLARATIONS_LAZY = [
    {
        "name": "get_weather",
        "description": "Gets weather data.",
        "parameters": {
            "type": "object",
            "properties": {"airport": {"type": "string"}},
            "required": ["airport"],
        },
    },
    {
        "name": "get_flight_status",
        "description": "Gets flight info.",
        "parameters": {
            "type": "object",
            "properties": {"flight_number": {"type": "string"}},
            "required": ["flight_number"],
        },
    },

    {
        "name": "get_flight_data",
        "description": "Gets maintenance details.",
        "parameters": {
            "type": "object",
            "properties": {"tail_number": {"type": "string"}},
            "required": ["tail_number"],
        },
    },
]
