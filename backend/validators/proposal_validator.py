"""
Validators — Proposal JSON Output Validator

Validates the structured JSON output received from the AI model.
Uses jsonschema for schema enforcement + additional semantic checks.

This layer acts as a contract enforcement boundary between the AI service
and the domain entities — preventing bad data from entering the application.
"""
import json
import jsonschema
from typing import Any

# ---------------------------------------------------------------------------
# JSON Schema — defines the exact structure the AI must return
# ---------------------------------------------------------------------------
PROPOSAL_OUTPUT_SCHEMA: dict = {
    "type": "object",
    "required": [
        "executive_summary",
        "problem_statement",
        "proposed_solution",
        "key_benefits",
        "implementation_timeline",
        "budget_allocation",
        "cost_breakdown",
        "impact_positioning_summary",
        "terms_and_conditions",
        "call_to_action",
    ],
    "properties": {
        "executive_summary": {
            "type": "string",
            "minLength": 50,
            "maxLength": 2000,
            "description": "High-level overview of the proposal.",
        },
        "problem_statement": {
            "type": "string",
            "minLength": 30,
            "maxLength": 1500,
        },
        "proposed_solution": {
            "type": "string",
            "minLength": 50,
            "maxLength": 2000,
        },
        "key_benefits": {
            "type": "array",
            "items": {"type": "string", "minLength": 5},
            "minItems": 2,
            "maxItems": 10,
        },
        "implementation_timeline": {
            "type": "string",
            "minLength": 20,
            "maxLength": 1000,
        },
        "sustainable_product_mix": {
            "type": "array",
            "items": {"type": "string", "minLength": 5},
            "minItems": 1,
            "maxItems": 6,
            "description": "Recommended product/service combinations.",
        },
        "budget_allocation": {
            "type": "string",
            "minLength": 30,
            "maxLength": 1000,
            "description": "Breakdown of budget allocation across components.",
        },
        "cost_breakdown": {
            "type": "string",
            "minLength": 30,
            "maxLength": 1500,
            "description": "Detailed estimated costs and pricing breakdown.",
        },
        "impact_positioning_summary": {
            "type": "string",
            "minLength": 30,
            "maxLength": 1500,
            "description": "Expected ROI and business impact.",
        },
        "terms_and_conditions": {
            "type": "string",
            "minLength": 20,
            "maxLength": 2000,
        },
        "call_to_action": {
            "type": "string",
            "minLength": 10,
            "maxLength": 500,
        },
    },
    "additionalProperties": True,  # Allow extra fields from AI (non-breaking)
}

# Singleton validator instance (compiled once for performance)
_validator = jsonschema.Draft7Validator(PROPOSAL_OUTPUT_SCHEMA)


def validate_proposal_json(data: Any) -> None:
    """
    Validate AI-generated proposal JSON against the schema.

    Args:
        data: Parsed JSON object (dict) from the AI response.

    Raises:
        ValueError: With a human-readable message listing all validation errors.
    """
    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a JSON object from AI, got {type(data).__name__}. "
            "Ensure the AI model is configured with response_format=json_object."
        )

    errors = sorted(_validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        messages = [f"  • [{'.'.join(str(p) for p in e.absolute_path) or 'root'}] {e.message}" for e in errors]
        raise ValueError(
            "AI response failed schema validation:\n" + "\n".join(messages)
        )

    # Semantic checks beyond what jsonschema can express
    _check_semantic_quality(data)


def _check_semantic_quality(data: dict) -> None:
    """
    Additional semantic validation rules.
    These guard against AI responses that technically pass schema but are clearly wrong.
    """
    placeholder_phrases = [
        "[insert", "[your company", "lorem ipsum", "placeholder",
        "{{", "}}", "TODO", "TBD",
    ]
    fields_to_check = [
        "executive_summary", "problem_statement", "proposed_solution",
        "implementation_timeline", "call_to_action",
    ]
    for field in fields_to_check:
        value = data.get(field, "")
        if isinstance(value, str):
            for phrase in placeholder_phrases:
                if phrase.lower() in value.lower():
                    raise ValueError(
                        f"Field '{field}' contains placeholder text: '{phrase}'. "
                        "The AI may not have generated real content."
                    )


def parse_and_validate(raw_content: str) -> dict:
    """
    Convenience helper: parse a raw JSON string then validate it.

    Args:
        raw_content: Raw string from the AI response (may contain surrounding text).

    Returns:
        Validated dictionary.

    Raises:
        ValueError: On JSON parse failure or schema violation.
    """
    # Attempt to extract JSON if model accidentally wrapped it in markdown
    content = raw_content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])  # strip ```json ... ``` fences

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse AI output as JSON: {exc}") from exc

    validate_proposal_json(data)
    return data
