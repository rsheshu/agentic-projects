"""Environment configuration for the FlightOps provider."""

import os

LLM_URL = os.getenv("LLM_URL", "http://localhost:11434/api/chat")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
USE_LOCAL_FALLBACK = os.getenv("USE_LOCAL_FALLBACK", "true").lower() in {"1", "true", "yes", "on"}
USE_LAZY_SCHEMAS = False
