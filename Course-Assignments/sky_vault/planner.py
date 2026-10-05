"""Goal and plan generation for FlightOps."""

from __future__ import annotations


def generate_goal_and_plan(user_question: str) -> dict:
    question = (user_question or "").lower()

    if any(token in question for token in ["store","remember"]):
        return {
            "goal": "Store the provided information in memory.",
            "plan": [
                "Identify the key and value to be stored.",
                "Call the 'remember' tool with the identified key and value.",
                "Confirm the information has been stored.",
            ],
        }

    if any(token in question for token in ["depart on time", "likely to depart", "on time"]):
        return {
            "goal": "Determine whether the flight can depart on time.",
            "plan": [
                "Check weather at the departure airport.",
                "Check maintenance history for the aircraft tail number.",
                "Check gate availability.",
                "Check the flight status for the requested flight.",
                "Synthesize an answer about departure reliability.",
            ],
        }

    if any(token in question for token in ["gate", "empty gate", "open gate", "available gate"]):
        return {
            "goal": "Find an available gate for the requested terminal.",
            "plan": [
                "Identify the relevant terminal.",
                "Call the gate lookup tool.",
                "Report the first available gate.",
            ],
        }

    if "passenger" in question or "booking" in question:
        return {
            "goal": "Find the passenger or booking information requested by the user.",
            "plan": [
                "Identify the passenger name or flight details.",
                "Search the booking records.",
                "Return the matched passenger information clearly.",
            ],
        }

    return {
        "goal": "Answer the operational question with grounded backend facts.",
        "plan": [
            "Identify which tool or tools are relevant.",
            "Call the required tools in a sensible order.",
            "Summarize the result in plain language.",
        ],
    }
