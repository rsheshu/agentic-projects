"""Mock backend data for FlightOps."""

Flights = {
    "AI203": {
        "flight_number": "AI203",
        "status": "scheduled",
        "gate": "B12",
        "departure_time": "2026-08-23T15:30:00",
        "delay_minutes": 0,
        "tail_number": "VT-ABC",
        "origin": "DEL",
        "destination": "BOM",
    },
    "AI204": {
        "flight_number": "AI204",
        "status": "boarding",
        "gate": "A05",
        "departure_time": "2026-08-23T16:00:00",
        "delay_minutes": 10,
        "tail_number": "VT-XYZ",
        "origin": "DEL",
        "destination": "BLR",
    },
    "AI205": {
        "flight_number": "AI205",
        "status": "delayed",
        "gate": "C07",
        "departure_time": "2026-08-23T17:15:00",
        "delay_minutes": 45,
        "tail_number": "VT-MNO",
        "origin": "HYD",
        "destination": "GOI",
    },
}

Aircraft = {
    "A320": {
        "type": "A320",
        "dimensions": "37.57m x 34.10m",
        "capacity": 180,
        "fuel_capacity_l": 23860,
        "seat_pitch_in": 31,
    },
    "A321": {
        "type": "A321",
        "dimensions": "44.51m x 34.44m",
        "capacity": 220,
        "fuel_capacity_l": 32000,
        "seat_pitch_in": 30,
    },
}

Passengers = [
    {"name": "Alice Kumar", "booking_ref": "ABC123", "seat": "12A", "flight": "AI203"},
    {"name": "Bob Singh", "booking_ref": "DEF456", "seat": "22C", "flight": "AI204"},
    {"name": "Priya Nair", "booking_ref": "GHI789", "seat": "08D", "flight": "AI205"},
]

Maintenance = {
    "VT-ABC": {
        "last_inspection": "2026-08-10",
        "hours_flown": 1240,
        "outstanding_issues": [],
    },
    "VT-XYZ": {
        "last_inspection": "2026-07-30",
        "hours_flown": 980,
        "outstanding_issues": ["brake_check"],
    },
    "VT-MNO": {
        "last_inspection": "2026-08-12",
        "hours_flown": 1605,
        "outstanding_issues": ["cargo_door inspection"],
    },
}

Weather = {
    "DEL": {"visibility_km": 10, "wind_kts": 8, "temperature_c": 34, "condition": "clear"},
    "BOM": {"visibility_km": 2, "wind_kts": 5, "temperature_c": 29, "condition": "fog"},
    "HYD": {"visibility_km": 6, "wind_kts": 12, "temperature_c": 31, "condition": "hazy"},
    "BLR": {"visibility_km": 8, "wind_kts": 10, "temperature_c": 27, "condition": "clear"},
    "GOI": {"visibility_km": 4, "wind_kts": 15, "temperature_c": 28, "condition": "rain"},
}
