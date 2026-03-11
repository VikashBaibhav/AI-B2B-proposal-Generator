"""
Use Case — Calculate Pricing

Pure business logic for computing pricing tiers based on client profile.
No AI, no HTTP, no database — fully unit-testable.
"""
from dataclasses import dataclass
from domain.entities.proposal import Client, PricingTier, IndustryType


@dataclass
class PricingInput:
    """Input data required to calculate proposal pricing."""
    client: Client
    requested_features: list[str]
    contract_duration_months: int = 12


@dataclass
class PricingOutput:
    """Result of the pricing calculation."""
    tiers: list[PricingTier]
    recommended_tier: str
    estimated_roi_percentage: float
    notes: list[str]


# ---------------------------------------------------------------------------
# Pricing constants (business rules — easy to tune)
# ---------------------------------------------------------------------------

BASE_PRICES = {
    "Starter":      2_000.0,
    "Professional": 5_000.0,
    "Enterprise":  15_000.0,
}

SETUP_FEES = {
    "Starter":      500.0,
    "Professional": 1_500.0,
    "Enterprise":   5_000.0,
}

# Discount rules based on company size (head count)
SIZE_DISCOUNTS: list[tuple[int, float]] = [
    (10,    0.0),   # <10 employees: no discount
    (50,    5.0),   # 10–49 employees: 5%
    (200,  10.0),   # 50–199 employees: 10%
    (500,  15.0),   # 200–499 employees: 15%
    (99999, 20.0),  # 500+ employees: 20%
]

# Industry-specific uplift/discount in percentage points
INDUSTRY_ADJUSTMENT: dict[IndustryType, float] = {
    IndustryType.TECHNOLOGY:    -5.0,   # Tech-savvy: slight discount
    IndustryType.HEALTHCARE:     5.0,   # Compliance overhead: uplift
    IndustryType.FINANCE:       10.0,   # Highest compliance overhead
    IndustryType.RETAIL:         0.0,
    IndustryType.MANUFACTURING:  0.0,
    IndustryType.EDUCATION:    -10.0,   # EDU pricing
    IndustryType.OTHER:          0.0,
}

TIER_FEATURES = {
    "Starter": [
        "AI Proposal Generation (up to 10/month)",
        "Basic templates",
        "Email export",
        "Standard support",
    ],
    "Professional": [
        "AI Proposal Generation (unlimited)",
        "Custom branding",
        "CRM integrations (HubSpot, Salesforce)",
        "PDF & Word export",
        "Analytics dashboard",
        "Priority email support",
    ],
    "Enterprise": [
        "Everything in Professional",
        "Dedicated AI model fine-tuning",
        "On-premise deployment option",
        "SSO / SAML",
        "SLA 99.9% uptime",
        "Dedicated customer success manager",
        "Custom integrations",
    ],
}


def _get_size_discount(company_size: int) -> float:
    """Return the discount percentage based on company head count."""
    for threshold, discount in SIZE_DISCOUNTS:
        if company_size <= threshold:
            return discount
    return 20.0


def _estimate_roi(tier_name: str, client: Client) -> float:
    """
    Heuristic ROI estimation (%).
    Real implementations can be far more sophisticated.
    """
    base_roi = {"Starter": 120.0, "Professional": 200.0, "Enterprise": 350.0}[tier_name]
    # Larger companies have more proposal volume — higher ROI
    if client.company_size > 200:
        base_roi += 50.0
    return round(base_roi, 1)


def _build_tier(
    tier_name: str,
    client: Client,
    contract_duration_months: int,
) -> PricingTier:
    base_price = BASE_PRICES[tier_name]
    size_discount = _get_size_discount(client.company_size)
    industry_adj = INDUSTRY_ADJUSTMENT.get(client.industry, 0.0)

    # Net discount: size discount minus any industry uplift
    net_discount = max(0.0, size_discount - max(0.0, industry_adj))

    # Annual billing discount
    billing_cycle = "monthly"
    if contract_duration_months >= 12:
        billing_cycle = "annual"
        base_price *= 0.9  # 10% off for annual commitment

    return PricingTier(
        tier_name=tier_name,
        base_price_usd=round(base_price, 2),
        features=TIER_FEATURES[tier_name],
        discount_percentage=round(net_discount, 2),
        setup_fee_usd=SETUP_FEES[tier_name],
        billing_cycle=billing_cycle,
    )


def calculate_pricing(input_data: PricingInput) -> PricingOutput:
    """
    Main pricing calculation function.

    Args:
        input_data: PricingInput with client profile and contract details.

    Returns:
        PricingOutput with all three pricing tiers and a recommendation.
    """
    client = input_data.client
    tiers = [
        _build_tier("Starter", client, input_data.contract_duration_months),
        _build_tier("Professional", client, input_data.contract_duration_months),
        _build_tier("Enterprise", client, input_data.contract_duration_months),
    ]

    # Recommendation logic
    if client.company_size <= 20:
        recommended = "Starter"
    elif client.company_size <= 200:
        recommended = "Professional"
    else:
        recommended = "Enterprise"

    roi = _estimate_roi(recommended, client)

    notes: list[str] = []
    if client.industry == IndustryType.FINANCE:
        notes.append("FINRA/SOC2 compliance requirements may incur additional setup time.")
    if client.industry == IndustryType.HEALTHCARE:
        notes.append("HIPAA Business Associate Agreement (BAA) available on Professional+.")
    if input_data.contract_duration_months >= 12:
        notes.append("Annual billing applied — 10% discount over monthly pricing.")

    return PricingOutput(
        tiers=tiers,
        recommended_tier=recommended,
        estimated_roi_percentage=roi,
        notes=notes,
    )
