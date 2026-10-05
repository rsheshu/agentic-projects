"""Direct tool smoke tests for FlightOps."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
import tools_inventory


def smoke_tests():
    print("\n get_flight_status(AI204):", tools_inventory.get_flight_status("AI204"))
    print("\n get_flight_status(AI203):", tools_inventory.get_flight_status("AI203"))
    print('\n search_passenger("Alice"):', tools_inventory.search_passenger("Alice"))
    print("\n maintenance_history(VT-ABC):", tools_inventory.maintenance_history("VT-ABC"))
    print("\n find_available_gate(B):", tools_inventory.find_available_gate("B"))
    print("\n get_weather(DEL):", tools_inventory.get_weather("DEL"))
    print("\n lookup_aircraft(A320):", tools_inventory.lookup_aircraft("A320"))
    print("\n get_weather(ERR):", tools_inventory.get_weather("ERR"))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        smoke_tests()
    else:
        smoke_tests()
