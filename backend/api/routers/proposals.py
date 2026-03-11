"""
API Router — Proposals

FastAPI route handlers for proposal generation and retrieval.
Translates HTTP requests → domain calls → HTTP responses.
All business logic lives in the use cases, not here.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from api.schemas.proposal_schema import (
    GenerateProposalRequest,
    ProposalResponse,
    PricingTierResponse,
    ErrorResponse,
)
from domain.entities.proposal import Client, IndustryType, Proposal
from domain.interfaces.ai_service import AIServiceError
from application.use_cases.generate_proposal import GenerateProposalUseCase
from infrastructure.ai.gemini_service import GeminiService
from infrastructure.repositories.in_memory_repository import InMemoryProposalRepository
from logger.prompt_logger import PromptLogger

router = APIRouter(prefix="/api/proposals", tags=["Proposals"])

# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------

# In a real app, use a proper DI container (e.g., dependency-injector library).
# For simplicity, singletons are created here.
_repository = InMemoryProposalRepository()
_prompt_logger = PromptLogger()


def get_use_case() -> GenerateProposalUseCase:
    ai_service = GeminiService()
    return GenerateProposalUseCase(ai_service=ai_service, proposal_repository=_repository)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _map_proposal_to_response(proposal: Proposal) -> ProposalResponse:
    """Convert a domain Proposal entity to its HTTP response schema."""
    pricing_tiers = [
        PricingTierResponse(
            tier_name=t.tier_name,
            base_price_usd=t.base_price_usd,
            effective_price=t.effective_price,
            setup_fee_usd=t.setup_fee_usd,
            discount_percentage=t.discount_percentage,
            billing_cycle=t.billing_cycle,
            annual_value=t.annual_value,
            features=t.features,
        )
        for t in proposal.pricing_tiers
    ]
    return ProposalResponse(
        proposal_id=proposal.proposal_id,
        title=proposal.title,
        status=proposal.status.value,
        company_name=proposal.client.company_name,
        industry=proposal.client.industry.value,
        executive_summary=proposal.executive_summary,
        problem_statement=proposal.problem_statement,
        proposed_solution=proposal.proposed_solution,
        key_benefits=proposal.key_benefits,
        implementation_timeline=proposal.implementation_timeline,
        terms_and_conditions=proposal.terms_and_conditions,
        call_to_action=proposal.call_to_action,
        sustainable_product_mix=proposal.sustainable_product_mix,
        budget_allocation=proposal.budget_allocation,
        cost_breakdown=proposal.cost_breakdown,
        impact_positioning_summary=proposal.impact_positioning_summary,
        pricing_tiers=pricing_tiers,
        created_at=proposal.created_at,
        ai_model_used=proposal.ai_model_used,
        prompt_tokens_used=proposal.prompt_tokens_used,
        completion_tokens_used=proposal.completion_tokens_used,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/generate",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a B2B proposal",
    description=(
        "Accepts a client profile, runs the pricing calculation, calls the AI model, "
        "validates the JSON output, and returns a complete B2B proposal."
    ),
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "AI service rate limit"},
        502: {"model": ErrorResponse, "description": "AI service error"},
    },
)
async def generate_proposal(
    body: GenerateProposalRequest,
    use_case: GenerateProposalUseCase = Depends(get_use_case),
):
    client = Client(
        company_name=body.client.company_name,
        contact_name=body.client.contact_name,
        contact_email=body.client.contact_email,
        industry=IndustryType(body.client.industry.value),
        company_size=body.client.company_size,
        annual_revenue_usd=body.client.annual_revenue_usd,
        website=body.client.website,
        pain_points=body.client.pain_points,
        goals=body.client.goals,
    )

    try:
        proposal = await use_case.execute(
            client=client,
            contract_duration_months=body.contract_duration_months,
        )
    except AIServiceError as exc:
        status_code = exc.status_code or 502
        raise HTTPException(status_code=status_code, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    _prompt_logger.log_interaction(
        proposal_id=proposal.proposal_id,
        prompt_tokens=proposal.prompt_tokens_used,
        completion_tokens=proposal.completion_tokens_used,
        model=proposal.ai_model_used or "unknown",
    )

    return _map_proposal_to_response(proposal)


@router.get(
    "/{proposal_id}",
    response_model=ProposalResponse,
    summary="Retrieve a generated proposal",
)
async def get_proposal(proposal_id: str):
    proposal = await _repository.get_by_id(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposal '{proposal_id}' not found.")
    return _map_proposal_to_response(proposal)


@router.get(
    "/",
    response_model=list[ProposalResponse],
    summary="List all generated proposals",
)
async def list_proposals():
    proposals = await _repository.list_all()
    return [_map_proposal_to_response(p) for p in proposals]
