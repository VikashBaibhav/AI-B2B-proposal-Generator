"""
Domain Entities — Proposal

Pure Python dataclasses with no framework dependencies.
These are the core business objects of the application.
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ProposalStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    APPROVED = "approved"
    REJECTED = "rejected"


class IndustryType(str, Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    OTHER = "other"


@dataclass
class Client:
    """Represents the B2B client for whom the proposal is generated."""
    company_name: str
    contact_name: str
    contact_email: str
    industry: IndustryType
    company_size: int          # Number of employees
    annual_revenue_usd: Optional[float] = None
    website: Optional[str] = None
    budget_limit_usd: Optional[float] = None  # Budget allocation limit for cost breakdown
    pain_points: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)


@dataclass
class PricingTier:
    """Represents a pricing option within a proposal."""
    tier_name: str             # e.g., "Starter", "Professional", "Enterprise"
    base_price_usd: float
    features: list[str] = field(default_factory=list)
    discount_percentage: float = 0.0
    setup_fee_usd: float = 0.0
    billing_cycle: str = "monthly"  # monthly | annual | one-time

    @property
    def effective_price(self) -> float:
        """Price after applying discount."""
        discounted = self.base_price_usd * (1 - self.discount_percentage / 100)
        return round(discounted, 2)

    @property
    def annual_value(self) -> float:
        """Total annual contract value including setup fee."""
        if self.billing_cycle == "monthly":
            return round(self.effective_price * 12 + self.setup_fee_usd, 2)
        elif self.billing_cycle == "annual":
            return round(self.effective_price + self.setup_fee_usd, 2)
        return round(self.effective_price + self.setup_fee_usd, 2)


@dataclass
class Proposal:
    """
    Core domain entity: a B2B proposal document.
    Contains the client context, AI-generated content, and pricing tiers.
    """
    proposal_id: str
    client: Client
    title: str
    status: ProposalStatus = ProposalStatus.DRAFT

    # AI-generated content (populated after generation)
    executive_summary: Optional[str] = None
    problem_statement: Optional[str] = None
    proposed_solution: Optional[str] = None
    key_benefits: list[str] = field(default_factory=list)
    implementation_timeline: Optional[str] = None
    pricing_tiers: list[PricingTier] = field(default_factory=list)
    terms_and_conditions: Optional[str] = None
    call_to_action: Optional[str] = None
    
    # New features
    sustainable_product_mix: list[str] = field(default_factory=list)
    budget_allocation: Optional[str] = None
    cost_breakdown: Optional[str] = None
    impact_positioning_summary: Optional[str] = None

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    ai_model_used: Optional[str] = None
    prompt_tokens_used: int = 0
    completion_tokens_used: int = 0
