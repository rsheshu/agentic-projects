"""Command-line entry point for FlightOps.
1. Run a single question with the agent
2. Run a questionnaire from a text file with one question per line. 
3. Log the results to results.txt.
4. Runs the agent with tool calling and a multi-tool loop.
5. Uses a hand-built planner and reflector to generate a plan and reflect on the results.
6. Uses the FlightOps provider with a set of tools for airline operations.
7. Uses LAZY schemas for the tools to check the LLM's ability to handle tool calls without full schema definitions.

"""


from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
import agent
import planner
import reflector

from agent import log_to_file
DEFAULT_QUESTION_FILE = Path(__file__).with_name("questions.txt")

def log_questionnaire_result(question: str, result: dict) -> None:
    """Append the question and answer for a questionnaire run to results.txt."""
    answer = result.get("answer", "")
    tool_log = json.dumps(result.get("log", {}), indent=2)
    entry = (
        f"\n===== Question =====\n"
        f"{question}\n\n"
        f"Answer:\n{answer}\n\n"
        f"Tool log:\n{tool_log}\n"
        f"{'-' * 80}\n"
    )
    log_to_file(entry)

def load_questions(file_path: str | None = None) -> list[str]:
    path = Path(file_path) if file_path else DEFAULT_QUESTION_FILE
    if not path.exists():
        return []

    questions: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            cleaned = line.strip()
            if cleaned and not cleaned.startswith("#"):
                questions.append(cleaned)
    return questions


def run_question(question: str):
    print("Goal:")
    goal_plan = planner.generate_goal_and_plan(question)
    print(goal_plan["goal"])
    log_to_file(f"\n 1. Goal: {goal_plan['goal']}")

    print("Plan:")
    for index, step in enumerate(goal_plan["plan"], start=1):
        print(f"{index}. {step}")

    log_to_file(f"\n 2. Plan: {goal_plan['plan']}")

    result = agent.run_agent(question)
    print("\nFinal answer:")
    print(result["answer"])
    log_to_file(f"\n 3. Final answer: {result['answer']}")

    reflection = reflector.reflect(result["log"])
    print("\nReflection:")
    print(reflection["text"])
    log_to_file(f"\n 4. Reflection: {reflection['text']}")

    print("\nTool call log:")
    print(json.dumps(result["log"], indent=2))
    log_to_file(f"\n 5. Tool call log: {json.dumps(result['log'], indent=2)}")
    return result


def run_questionnaire(file_path: str | None = None):
    questions = load_questions(file_path)
    if not questions:
        print(f"No questions found in {DEFAULT_QUESTION_FILE.name}. Add questions one per line.")
        return

    for index, question in enumerate(questions, start=1):
        print(f"\n===== Question {index} =====")
        print(question)
        result = run_question(question)
        log_questionnaire_result(question, result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the FlightOps tool-calling agent.")
    #parser.add_argument("question", nargs="?", default="Is AI203 likely to depart on time?", help="Single user question to answer.")
    #parser.add_argument("question", nargs="?", default="What is booking seat for Alice?", help="Single user question to answer.")
    parser.add_argument("question", nargs="?", help="Single user question to answer.")
    parser.add_argument("--file", dest="questions_file", help="Path to a text file containing one question per line.")
    args = parser.parse_args()
    print(args.question)

    if args.question:
        run_question(args.question)
    else:
        run_questionnaire(args.questions_file)
