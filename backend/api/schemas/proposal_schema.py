"""
API Schemas — Proposal Request/Response (Pydantic)

Pydantic models for request validation and response serialization at the HTTP boundary.
These are separate from domain entities — they handle HTTP concerns (field naming,
optional fields for partial responses, JSON serialization).
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from enum import Enum


# ---- Enums (mirrors domain, but decoupled) ---------------------------------

class IndustryEnum(str, Enum):
    technology = "technology"
    healthcare = "healthcare"
    finance = "finance"
    retail = "retail"
    manufacturing = "manufacturing"
    education = "education"
    other = "other"


# ---- Request Models ---------------------------------------------------------

class ClientRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200, example="Acme Corp")
    contact_name: str = Field(..., min_length=2, max_length=100, example="Jane Smith")
    contact_email: EmailStr = Field(..., example="jane@acmecorp.com")
    industry: IndustryEnum = Field(..., example="technology")
    company_size: int = Field(..., ge=1, le=1_000_000, example=75)
    annual_revenue_usd: Optional[float] = Field(None, ge=0, example=5_000_000.0)
    website: Optional[str] = Field(None, example="https://acmecorp.com")
    budget_limit_usd: Optional[float] = Field(None, ge=0, example=50_000.0, description="Annual budget allocation limit for cost breakdown")
    pain_points: list[str] = Field(
        default_factory=list,
        max_length=10,
        example=["Manual proposal creation takes too long", "Poor win rate on enterprise deals"],
    )
    goals: list[str] = Field(
        default_factory=list,
        max_length=10,
        example=["Close enterprise deals faster", "Standardise proposal quality"],
    )


class GenerateProposalRequest(BaseModel):
    client: ClientRequest
    contract_duration_months: int = Field(
        default=12, ge=1, le=60, example=12,
        description="Contract duration for pricing calculation (1–60 months)."
    )


# ---- Response Models --------------------------------------------------------

class PricingTierResponse(BaseModel):
    tier_name: str
    base_price_usd: float
    effective_price: float
    setup_fee_usd: float
    discount_percentage: float
    billing_cycle: str
    annual_value: float
    features: list[str]


class ProposalResponse(BaseModel):
    proposal_id: str
    title: str
    status: str

    # Client summary
    company_name: str
    industry: str

    # AI-generated sections
    executive_summary: Optional[str] = None
    problem_statement: Optional[str] = None
    proposed_solution: Optional[str] = None
    key_benefits: list[str] = []
    implementation_timeline: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    call_to_action: Optional[str] = None
    
    # New features
    sustainable_product_mix: list[str] = []
    budget_allocation: Optional[str] = None
    cost_breakdown: Optional[str] = None
    impact_positioning_summary: Optional[str] = None

    # Pricing
    pricing_tiers: list[PricingTierResponse] = []

    # Metadata
    created_at: Optional[str] = None
    ai_model_used: Optional[str] = None
    prompt_tokens_used: int = 0
    completion_tokens_used: int = 0


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
