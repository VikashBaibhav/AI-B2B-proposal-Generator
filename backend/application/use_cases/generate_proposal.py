"""
Use Case — Generate Proposal

Orchestrates the full proposal generation flow:
  1. Load and render the prompt template
  2. Call the AI service (via abstraction)
  3. Validate the JSON output
  4. Map the response to domain entities
  5. Persist the proposal

Depends only on domain interfaces — no concrete SDK imports.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from domain.entities.proposal import (
    Client, Proposal, PricingTier, ProposalStatus,
)
from domain.interfaces.ai_service import AIService, AIRequest, AIServiceError
from domain.interfaces.proposal_repository import ProposalRepository

from application.use_cases.calculate_pricing import (
    PricingInput, calculate_pricing,
)

# Paths are relative to the backend root directory
PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def _clean_json_string(raw: str) -> str:
    """Strip markdown code fences and extra whitespace from an AI response."""
    text = raw.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop the opening fence line
        lines = lines[1:]
        # Drop the closing fence (last line that is just ```)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _load_prompt(template_name: str, variables: dict) -> str:
    """
    Load a prompt template from the prompts/ directory and fill in variables.
    Templates use {variable_name} placeholders.
    """
    template_path = PROMPTS_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    template = template_path.read_text(encoding="utf-8")
    return template.format(**variables)


def _calculate_total_annual_value(tiers: list[PricingTier]) -> float:
    """Calculate the total annual contract value from all tiers."""
    return sum(tier.annual_value for tier in tiers)


def _apply_budget_constraint(proposal: Proposal) -> None:
    """
    Enforce budget limit constraint on pricing tiers.
    
    If budget_limit_usd is set and total cost exceeds it, 
    scales all pricing tiers proportionally while maintaining their relative values.
    
    Updates proposal.pricing_tiers in-place.
    """
    if not proposal.client.budget_limit_usd or not proposal.pricing_tiers:
        return
    
    total_annual_value = _calculate_total_annual_value(proposal.pricing_tiers)
    
    # If total cost is within budget, no adjustment needed
    if total_annual_value <= proposal.client.budget_limit_usd:
        return
    
    # Calculate scaling factor
    scale_factor = proposal.client.budget_limit_usd / total_annual_value
    
    # Scale all tiers proportionally
    for tier in proposal.pricing_tiers:
        # Scale base price and setup fee
        tier.base_price_usd = round(tier.base_price_usd * scale_factor, 2)
        tier.setup_fee_usd = round(tier.setup_fee_usd * scale_factor, 2)
        # Note: effective_price and annual_value are computed properties,
        # so they automatically reflect the new scaled values


def _map_ai_response_to_proposal(
    proposal: Proposal,
    ai_json: dict,
    ai_model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> Proposal:
    """Map the validated AI JSON response onto the Proposal entity."""
    proposal.executive_summary = ai_json.get("executive_summary", "")
    proposal.problem_statement = ai_json.get("problem_statement", "")
    proposal.proposed_solution = ai_json.get("proposed_solution", "")
    proposal.key_benefits = ai_json.get("key_benefits", [])
    proposal.implementation_timeline = ai_json.get("implementation_timeline", "")
    proposal.terms_and_conditions = ai_json.get("terms_and_conditions", "")
    proposal.call_to_action = ai_json.get("call_to_action", "")
    
    # New features
    proposal.sustainable_product_mix = ai_json.get("sustainable_product_mix", [])
    proposal.budget_allocation = ai_json.get("budget_allocation", "")
    proposal.cost_breakdown = ai_json.get("cost_breakdown", "")
    proposal.impact_positioning_summary = ai_json.get("impact_positioning_summary", "")

    proposal.status = ProposalStatus.GENERATED
    proposal.ai_model_used = ai_model
    proposal.prompt_tokens_used = prompt_tokens
    proposal.completion_tokens_used = completion_tokens
    proposal.updated_at = datetime.now(timezone.utc).isoformat()

    return proposal


class GenerateProposalUseCase:
    """
    Orchestrates B2B proposal generation.

    Constructor dependencies are injected — the use case is never responsible
    for constructing its own dependencies (Dependency Inversion Principle).
    """

    def __init__(
        self,
        ai_service: AIService,
        proposal_repository: ProposalRepository,
    ) -> None:
        self._ai_service = ai_service
        self._repo = proposal_repository

    async def execute(self, client: Client, contract_duration_months: int = 12) -> Proposal:
        """
        Generate a complete B2B proposal for the given client.

        Args:
            client: The Client domain entity describing the prospect.
            contract_duration_months: Duration used for pricing calculation.

        Returns:
            A fully populated and persisted Proposal entity.

        Raises:
            AIServiceError: If the AI call fails.
            ValueError: If the AI response fails validation.
        """
        now = datetime.now(timezone.utc).isoformat()
        proposal = Proposal(
            proposal_id=str(uuid.uuid4()),
            client=client,
            title=f"Proposal for {client.company_name}",
            status=ProposalStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )

        # 1. Calculate pricing (pure business logic — no AI needed)
        pricing_output = calculate_pricing(
            PricingInput(
                client=client,
                requested_features=[],
                contract_duration_months=contract_duration_months,
            )
        )
        proposal.pricing_tiers = pricing_output.tiers

        # 2. Build the prompt (render template with client context)
        user_prompt = _load_prompt(
            "proposal_generation.txt",
            {
                "company_name": client.company_name,
                "industry": client.industry.value,
                "company_size": client.company_size,
                "pain_points": ", ".join(client.pain_points) or "Not specified",
                "goals": ", ".join(client.goals) or "Not specified",
                "budget_limit_usd": f"${client.budget_limit_usd:,.2f}" if client.budget_limit_usd else "Not specified",
                "recommended_tier": pricing_output.recommended_tier,
                "pricing_notes": "; ".join(pricing_output.notes) or "None",
            },
        )

        system_prompt = (
            "You are an expert B2B sales consultant. Generate a professional proposal "
            "as a valid JSON object following the schema provided. Be specific, persuasive, "
            "and tailored to the client's industry and pain points."
        )

        # 3. Call AI service
        ai_request = AIRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.4,
            max_tokens=8192,
            response_format="json_object",
        )
        ai_response = await self._ai_service.generate(ai_request)

        # 4. Parse and validate the JSON response
        # Only raise if the model was explicitly cut off by the token limit.
        # "stop" (or None/"") means normal completion — always proceed.
        if ai_response.finish_reason == "max_tokens":
            raise ValueError(
                "AI response was cut off by the token limit. "
                "Try using shorter pain points / goals, or contact support."
            )

        cleaned_content = _clean_json_string(ai_response.content)
        try:
            ai_json = json.loads(cleaned_content)
        except json.JSONDecodeError as exc:
            # Log first 500 chars to help diagnose without exposing full content
            preview = cleaned_content[:500].replace("\n", " ")
            raise ValueError(
                f"AI returned non-JSON content: {exc}. Response preview: {preview!r}"
            ) from exc

        # Import here to avoid circular dependencies at module level
        from validators.proposal_validator import validate_proposal_json
        validate_proposal_json(ai_json)  # Raises ValueError on schema violation

        # 5. Map AI response to entity
        proposal = _map_ai_response_to_proposal(
            proposal,
            ai_json,
            ai_response.model,
            ai_response.prompt_tokens,
            ai_response.completion_tokens,
        )

        # 5.5. Apply budget constraint if budget limit is provided
        _apply_budget_constraint(proposal)

        # 6. Persist and return
        return await self._repo.save(proposal)
