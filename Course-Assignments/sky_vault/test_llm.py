

"""Command-line conversational runner for one FlightOps session."""

from __future__ import annotations

import argparse

import agent
import planner
import reflector


def run_conversation() -> None:
    """Keep one conversation alive until the user exits or sends EOF."""
    conversation = [{"role": "system", "content": agent._system_prompt_with_memory()}]
    print("SkyVault is ready. Type 'exit' or 'quit' to end the session.")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        if question.__contains__("remember") or question.__contains__("store"):
            result = agent.run_agent(question)
            break        

        print("Goal:")
        goal_plan = planner.generate_goal_and_plan(question)
        print(goal_plan["goal"])
        result = agent.run_agent(question)
        print("\nSkyVault Response")
        print(result["answer"])
        print()
        reflection = reflector.reflect(result["log"])
        print("\nReflection:")
        print(reflection["text"])


if __name__ == "__main__":
    argparse.ArgumentParser(description="Run one conversational SkyVault session.").parse_args()
    run_conversation()