## Student Details

**Name: Sheshachalam Ratnala**

**Roll Number: cert-aai-2026-06-0019**

**Email:rshesha.pm@gmail.com**


# Assignment 04: Project FlightOps

This project implements a hand-built tool-calling airline operations agent for the Assignment 04 FlightOps brief. The system uses plain Python control flow rather than an agent framework, and it follows the required tool-calling lifecycle: generate a goal and plan, call provider tools, process tool results, and reflect on the run.


## Memory and conflict policy

SkyVault now keeps a small on-disk memory store in `memory.json`. Facts are stored under stable keys and are loaded into the system prompt at the start of every run, so they persist across process restarts. The memory layer also exposes `remember` and `recall` as callable tools during a conversation.

Conflict rule: each key is unique; the newest write wins. If the same memory key is stored again with a different value, the older value is replaced instead of being kept alongside the new one. This is intentional and documented here so there is no silent duplication of conflicting facts.

## Architecture

- `data.py`: mock flight, aircraft, passenger, maintenance, and weather dictionaries.
- `tools.py`: six backend functions that read and return airline operational data.
- `schemas.py`: tool declarations used to tell the model what each tool does and what arguments it expects.
- `config.py`: environment-based configuration for the model provider.
- `agent.py`: provider integration, tool execution, and the multi-tool call loop.
- `planner.py`: generates a goal and a plan before the agent starts acting.
- `reflector.py`: evaluates whether the tool calls were necessary and how confident the answer should be.
- `main.py`: CLI entry point for a user question.
- `questions.txt` : Questions to be framed for the Flight operations 
- `results.txt`   : The logging of the results for each question.
-  `requirement.txt`  : requirement.txt for the library used

## Model provider

This project uses the local Ollama provider with the default model `gemma3:1b`. The provider call is isolated in [agent.py](agent.py), so the rest of the agent remains model-agnostic.

## How to run

1. Start Ollama:

   ```bash
   ollama list
   ollama serve
   ollama pull llama3.2
   ```
2. Configs:

  # Variabls 
   - USE_LAZY_SCHEMAS :  Enables the lazy schema

   ## env variables
   - LLM_URL
   - LL_MODEL
   - USE_LOCAL_FALLBACK

2. From this directory, run:

   ```bash
   python main.py "Is AI203 likely to depart on time?"
   python main.py --file questions.txt
   
   ```
   # check on the  results.txt for the results
   # Add questions in questions.txt for all types of questions
   # use USE_LAZY_SCHEMAS for the incomplete schemas

3. You can also run direct smoke tests for the tool backend:

   ```bash
   python app.py smoke
   ```

## Tool design and schema quality

The careful function descriptions in [schemas.py](schemas.py) are more effective than the deliberately vague lazy versions because they specify the exact operational context, the argument type, and the actual semantics of the tool. For example, `get_weather` is described as taking an airport code and returning visibility, wind, temperature, and condition, while `maintenance_history` is specifically tied to a tail number and aircraft inspection data. The model can distinguish these tools correctly when the description communicates the real-world action and the expected arguments.

## Final report answers

1. In Assignment 03, grounding meant retrieving the correct passage from a document, so the main risk was choosing the wrong passage. In this assignment, grounding means invoking the correct backend function with the right argument. The second form of grounding risks making a wrong operational decision, not just a wrong quote, because it can mislead flight planning, maintenance decisions, or crew actions. The danger is therefore more consequential and harder to detect from a simple “answer looks plausible” test.

2. If a parameter is renamed in the Python tool but not in the schema, the model will still request the older argument name. The agent will then call the Python function with a missing or unexpected parameter and raise a `TypeError`, which the tool handler converts into a structured error instead of crashing the app. A practical safeguard is to validate the schema against the function signature before each run, checking declared parameters against `inspect.signature` so mismatches are caught before a user asks a real operational question.

## Sample Error recorded

```json
Tool call log
{
  "calls": [
    {
      "tool": "maintenance_history",
      "args": {
        "tail_number": "VT-XYZ"
      },
      "result": {
        "status": "error",
        "message": "Invalid arguments: maintenance_history() got an unexpected keyword argument 'tail_number'"
      }
    }
  ]
}
```

3. Allowing the agent to cancel bookings or reassign gates changes the risk from read-only lookup to action-taking with financial and operational consequences. In prod scenario, this would require explicit authorization, a human confirmation step, audit logs, idempotency keys, and a dry-run preview before any destructive or scheduling-changing tool is allowed to execute autonomously. 
These safeguards reduce the chance that a mistaken tool call leads to an irreversible operational change.
This activity is no different from a regular software update and since the update makes system autonomous a robust gaurd rails will ensure to avoid any un-expected behaviour.

4. The quality of the function descriptions mattered more than the system prompt in this project. The specific observation was that the careful descriptions in [schemas.py](schemas.py) allowed the model to select the correct tool for airport weather, maintenance status, and flight state, whereas the lazy descriptions blurred those operational meanings and caused poorer tool choice. The system prompt helped, but the precise function schema was the dominant signal for accurate tool selection.

## Lazy schema no tools identified

``` text
 1. Goal: Answer the operational question with grounded backend facts.
 2. Plan: ['Identify which tool or tools are relevant.', 'Call the required tools in a sensible order.', 'Summarize the result in plain language.']
 Using lazy schemas:
 3. Final answer: I used the available backend tools to check the most relevant operational facts for your question.
 4. Reflection: Called tools: []. Unnecessary calls: []. Missing information: []. Confidence: high.
 5. Tool call log: {
  "calls": []
}
```

## Smoke test

The direct backend smoke test is implemented in [app.py](app.py). It checks each tool with realistic inputs and confirms that the tool layer works independently of the model.

## Example questions

- Is AI203 likely to depart on time?
- Find an empty gate in terminal B.
- Who is booked on AI204?
- What is the maintenance history for VT-XYZ?

## Notes

This implementation intentionally avoids external agent frameworks and uses plain Python function calls to demonstrate what a framework is automating behind the scenes.
