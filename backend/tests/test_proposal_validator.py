"""
Unit Tests — Proposal JSON Validator

Tests the validation layer that guards AI output before it enters the domain.
No AI service needed — tests use hardcoded JSON payloads.
Run with: pytest tests/test_proposal_validator.py -v
"""
import pytest
from validators.proposal_validator import validate_proposal_json, parse_and_validate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_PAYLOAD = {
    "executive_summary": (
        "Acme Corp is at a critical juncture in its growth trajectory. "
        "Our AI Proposal Generator will help your sales team close deals 3x faster "
        "by eliminating manual document creation and delivering consistently compelling proposals."
    ),
    "problem_statement": (
        "Your team spends an average of 8 hours per proposal, creating inconsistent documents "
        "that fail to resonate with enterprise buyers. This directly impacts win rates and revenue."
    ),
    "proposed_solution": (
        "Our platform uses GPT-4 to generate tailored proposals in under 2 minutes. "
        "It integrates with your CRM, auto-fills client-specific data, and applies "
        "your brand voice consistently across every document."
    ),
    "key_benefits": [
        "Reduce proposal creation time from 8 hours to 15 minutes",
        "Increase win rates by up to 40% with personalized content",
        "Eliminate formatting inconsistencies across your sales team",
    ],
    "implementation_timeline": (
        "Week 1: Platform setup and CRM integration. "
        "Week 2-3: Team onboarding and template customization. "
        "Week 4: First live proposals generated. Month 2-3: Full team adoption and analytics review."
    ),
    "budget_allocation": (
        "Primary investment will be allocated toward platform subscription (50%), "
        "implementation and training (35%), and ongoing support (15%) to ensure "
        "your team has the resources needed for rapid adoption and success."
    ),
    "cost_breakdown": (
        "Platform subscription: $5,000/month. Implementation and onboarding: $15,000 (one-time). "
        "Dedicated support and training: $2,000/month. Total first-year investment: $89,000. "
        "Year 2 and beyond: $84,000 annually."
    ),
    "impact_positioning_summary": (
        "Your team can expect to reduce proposal creation time by 80-90%, freeing up "
        "approximately 30+ hours per week. This translates to approximately 15,000+ annual "
        "hours saved, enabling your sales team to focus on strategy and relationship building. "
        "Based on industry benchmarks, this efficiency can increase deal velocity by 40-50%."
    ),
    "terms_and_conditions": (
        "Payment is due monthly in advance. Either party may terminate with 30 days written notice. "
        "All client data is processed in accordance with GDPR. "
        "99.5% SLA uptime guaranteed, with credits for downtime exceeding threshold."
    ),
    "call_to_action": (
        "Schedule a 30-minute demo this week and see your first AI-generated proposal live. "
        "Reply to this email or book directly at calendly.com/b2b-ai — we have slots available Thursday."
    ),
}


# ---------------------------------------------------------------------------
# Happy Path
# ---------------------------------------------------------------------------

class TestValidPayload:
    def test_valid_payload_passes(self):
        """A well-formed payload should not raise."""
        validate_proposal_json(VALID_PAYLOAD)  # Should not raise

    def test_parse_and_validate_json_string(self):
        """parse_and_validate should handle a valid JSON string."""
        import json
        result = parse_and_validate(json.dumps(VALID_PAYLOAD))
        assert result["executive_summary"] == VALID_PAYLOAD["executive_summary"]

    def test_parse_and_validate_strips_markdown_fences(self):
        """parse_and_validate should strip ```json ... ``` fences from AI output."""
        import json
        raw = "```json\n" + json.dumps(VALID_PAYLOAD) + "\n```"
        result = parse_and_validate(raw)
        assert "executive_summary" in result

    def test_extra_fields_are_allowed(self):
        """additionalProperties=True — extra AI fields should not cause failure."""
        payload = {**VALID_PAYLOAD, "extra_field": "some extra info from AI"}
        validate_proposal_json(payload)  # Should not raise


# ---------------------------------------------------------------------------
# Missing Required Fields
# ---------------------------------------------------------------------------

class TestMissingFields:
    @pytest.mark.parametrize("missing_field", [
        "executive_summary",
        "problem_statement",
        "proposed_solution",
        "key_benefits",
        "implementation_timeline",
        "terms_and_conditions",
        "call_to_action",
    ])
    def test_missing_required_field_raises(self, missing_field: str):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != missing_field}
        with pytest.raises(ValueError, match="schema validation"):
            validate_proposal_json(payload)


# ---------------------------------------------------------------------------
# Type Violations
# ---------------------------------------------------------------------------

class TestTypeViolations:
    def test_key_benefits_must_be_list(self):
        payload = {**VALID_PAYLOAD, "key_benefits": "not a list"}
        with pytest.raises(ValueError):
            validate_proposal_json(payload)

    def test_executive_summary_must_be_string(self):
        payload = {**VALID_PAYLOAD, "executive_summary": 12345}
        with pytest.raises(ValueError):
            validate_proposal_json(payload)

    def test_non_dict_input_raises(self):
        with pytest.raises(ValueError, match="Expected a JSON object"):
            validate_proposal_json(["this", "is", "a", "list"])

    def test_none_input_raises(self):
        with pytest.raises(ValueError, match="Expected a JSON object"):
            validate_proposal_json(None)


# ---------------------------------------------------------------------------
# Length Violations
# ---------------------------------------------------------------------------

class TestLengthViolations:
    def test_executive_summary_too_short(self):
        payload = {**VALID_PAYLOAD, "executive_summary": "Too short."}
        with pytest.raises(ValueError):
            validate_proposal_json(payload)

    def test_key_benefits_too_few_items(self):
        payload = {**VALID_PAYLOAD, "key_benefits": ["Only one benefit"]}
        with pytest.raises(ValueError):
            validate_proposal_json(payload)


# ---------------------------------------------------------------------------
# Semantic / Placeholder Checks
# ---------------------------------------------------------------------------

class TestSemanticChecks:
    def test_placeholder_text_raises(self):
        payload = {**VALID_PAYLOAD, "executive_summary": "A" * 50 + " [insert company name here] " + "B" * 50}
        with pytest.raises(ValueError, match="placeholder text"):
            validate_proposal_json(payload)

    def test_lorem_ipsum_raises(self):
        payload = {**VALID_PAYLOAD, "proposed_solution": "Lorem ipsum dolor sit amet " * 5}
        with pytest.raises(ValueError, match="placeholder text"):
            validate_proposal_json(payload)

    def test_todo_text_raises(self):
        payload = {**VALID_PAYLOAD, "call_to_action": "TODO: write a real call to action here."}
        with pytest.raises(ValueError, match="placeholder text"):
            validate_proposal_json(payload)


# ---------------------------------------------------------------------------
# JSON Parse Error Handling
# ---------------------------------------------------------------------------

class TestJsonParsing:
    def test_invalid_json_string_raises(self):
        with pytest.raises(ValueError, match="Failed to parse"):
            parse_and_validate("this is not json at all")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse_and_validate("")
