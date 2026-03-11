"""
Logger — Prompt & Response Tracking

Structured logger that records every AI interaction:
  - Prompt content (system + user)
  - Raw AI response
  - Latency, token count, model name
  - Validation status

Logs are written to backend/logs/ as JSONL files (one JSON object per line)
for easy ingestion into analytics tools.
"""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Standard Python logging setup (used by all modules)
# ---------------------------------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


# ---------------------------------------------------------------------------
# Structured AI Interaction Logger
# ---------------------------------------------------------------------------

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

PROMPT_LOG_FILE = LOGS_DIR / "prompt_interactions.jsonl"
ERROR_LOG_FILE = LOGS_DIR / "errors.jsonl"


class PromptLogger:
    """
    Writes structured JSONL logs for every AI prompt/response cycle.

    Each log entry captures enough context to:
    - Replay or debug a specific generation
    - Track token usage and cost over time
    - Audit AI outputs for quality control
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger("prompt_logger")

    def log_interaction(
        self,
        proposal_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
        latency_seconds: float = 0.0,
        validation_passed: bool = True,
        error_message: str | None = None,
    ) -> None:
        """
        Log a completed AI interaction summary to JSONL.

        Args:
            proposal_id:        The generated proposal UUID.
            prompt_tokens:      Number of tokens in the input prompt.
            completion_tokens:  Number of tokens in the AI response.
            model:              Model identifier used (e.g., 'gpt-4o').
            latency_seconds:    Round-trip time for the AI call.
            validation_passed:  Whether the JSON validator accepted the output.
            error_message:      Error description if validation failed.
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "proposal_id": proposal_id,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency_seconds": round(latency_seconds, 3),
            "validation_passed": validation_passed,
            "error_message": error_message,
            # Estimated cost at ~$0.005 per 1k tokens (GPT-4o — adjust as needed)
            "estimated_cost_usd": round((prompt_tokens + completion_tokens) / 1000 * 0.005, 6),
        }
        self._write_jsonl(PROMPT_LOG_FILE, entry)
        self._logger.info(
            "AI interaction logged | proposal=%s | tokens=%d | model=%s | valid=%s",
            proposal_id,
            entry["total_tokens"],
            model,
            validation_passed,
        )

    def log_full_prompt(
        self,
        proposal_id: str,
        system_prompt: str,
        user_prompt: str,
        raw_response: str,
    ) -> None:
        """
        Log the full prompt and response content for debugging.
        
        WARNING: This logs potentially sensitive client data. Enable only in DEBUG mode.
        Only call this method when LOG_LEVEL=DEBUG.
        """
        if LOG_LEVEL != "DEBUG":
            return

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "proposal_id": proposal_id,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "raw_response": raw_response,
        }
        debug_log_file = LOGS_DIR / "prompt_full_debug.jsonl"
        self._write_jsonl(debug_log_file, entry)

    def log_error(self, proposal_id: str, error: Exception, context: dict | None = None) -> None:
        """Log a processing error to the errors JSONL file."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "proposal_id": proposal_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
        }
        self._write_jsonl(ERROR_LOG_FILE, entry)
        self._logger.error(
            "Error during proposal generation | proposal=%s | error=%s: %s",
            proposal_id,
            type(error).__name__,
            str(error),
        )

    @staticmethod
    def _write_jsonl(file_path: Path, entry: dict) -> None:
        """Append a JSON line to the target JSONL file (thread-safe for single process)."""
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as exc:
            logging.getLogger("prompt_logger").warning(
                "Failed to write log entry to %s: %s", file_path, exc
            )
