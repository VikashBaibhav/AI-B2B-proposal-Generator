"""
Unit Tests — calculate_pricing use case

Tests pure business pricing logic.
No AI service, no HTTP, no database needed.
Run with: pytest tests/test_calculate_pricing.py -v
"""
import pytest
from domain.entities.proposal import Client, IndustryType
from application.use_cases.calculate_pricing import (
    PricingInput, PricingOutput, calculate_pricing,
    BASE_PRICES, SETUP_FEES,
)


def make_client(company_size: int, industry: IndustryType = IndustryType.TECHNOLOGY) -> Client:
    return Client(
        company_name="Test Corp",
        contact_name="Alice",
        contact_email="alice@testcorp.com",
        industry=industry,
        company_size=company_size,
    )


class TestCalculatePricingTiers:
    """Verify that all three tiers are always returned."""

    def test_returns_three_tiers(self):
        client = make_client(50)
        result = calculate_pricing(PricingInput(client=client, requested_features=[]))
        assert len(result.tiers) == 3
        names = {t.tier_name for t in result.tiers}
        assert names == {"Starter", "Professional", "Enterprise"}

    def test_tier_names_are_correct(self):
        client = make_client(100)
        result = calculate_pricing(PricingInput(client=client, requested_features=[]))
        assert result.tiers[0].tier_name == "Starter"
        assert result.tiers[1].tier_name == "Professional"
        assert result.tiers[2].tier_name == "Enterprise"


class TestPricingRecommendation:
    """Test tier recommendation logic."""

    def test_small_company_recommends_starter(self):
        result = calculate_pricing(PricingInput(client=make_client(10), requested_features=[]))
        assert result.recommended_tier == "Starter"

    def test_medium_company_recommends_professional(self):
        result = calculate_pricing(PricingInput(client=make_client(100), requested_features=[]))
        assert result.recommended_tier == "Professional"

    def test_large_company_recommends_enterprise(self):
        result = calculate_pricing(PricingInput(client=make_client(500), requested_features=[]))
        assert result.recommended_tier == "Enterprise"


class TestPricingDiscounts:
    """Verify discount percentages are applied correctly."""

    def test_small_company_no_discount(self):
        result = calculate_pricing(PricingInput(client=make_client(5), requested_features=[]))
        starter = next(t for t in result.tiers if t.tier_name == "Starter")
        assert starter.discount_percentage == 0.0

    def test_large_company_has_discount(self):
        result = calculate_pricing(PricingInput(client=make_client(600), requested_features=[]))
        enterprise = next(t for t in result.tiers if t.tier_name == "Enterprise")
        assert enterprise.discount_percentage > 0.0

    def test_effective_price_less_than_base_when_discounted(self):
        result = calculate_pricing(PricingInput(client=make_client(600), requested_features=[]))
        enterprise = next(t for t in result.tiers if t.tier_name == "Enterprise")
        assert enterprise.effective_price < enterprise.base_price_usd


class TestAnnualBilling:
    """Verify annual billing discount is applied for 12+ month contracts."""

    def test_annual_contract_applies_billing_cycle_annual(self):
        result = calculate_pricing(
            PricingInput(client=make_client(50), requested_features=[], contract_duration_months=12)
        )
        for tier in result.tiers:
            assert tier.billing_cycle == "annual"

    def test_short_contract_uses_monthly_billing(self):
        result = calculate_pricing(
            PricingInput(client=make_client(50), requested_features=[], contract_duration_months=6)
        )
        for tier in result.tiers:
            assert tier.billing_cycle == "monthly"

    def test_annual_price_lower_than_monthly(self):
        monthly_result = calculate_pricing(
            PricingInput(client=make_client(50), requested_features=[], contract_duration_months=6)
        )
        annual_result = calculate_pricing(
            PricingInput(client=make_client(50), requested_features=[], contract_duration_months=12)
        )
        monthly_starter = next(t for t in monthly_result.tiers if t.tier_name == "Starter")
        annual_starter = next(t for t in annual_result.tiers if t.tier_name == "Starter")
        assert annual_starter.base_price_usd < monthly_starter.base_price_usd


class TestIndustryAdjustments:
    """Verify industry-specific pricing notes are generated."""

    def test_finance_generates_compliance_note(self):
        client = make_client(100, IndustryType.FINANCE)
        result = calculate_pricing(PricingInput(client=client, requested_features=[]))
        assert any("FINRA" in note or "SOC2" in note for note in result.notes)

    def test_healthcare_generates_hipaa_note(self):
        client = make_client(100, IndustryType.HEALTHCARE)
        result = calculate_pricing(PricingInput(client=client, requested_features=[]))
        assert any("HIPAA" in note for note in result.notes)

    def test_retail_has_no_compliance_notes(self):
        client = make_client(100, IndustryType.RETAIL)
        result = calculate_pricing(PricingInput(client=client, requested_features=[]))
        # No compliance notes expected for retail
        compliance_notes = [n for n in result.notes if "FINRA" in n or "HIPAA" in n]
        assert len(compliance_notes) == 0


class TestPricingTierProperties:
    """Test computed properties on PricingTier."""

    def test_effective_price_with_zero_discount(self):
        from domain.entities.proposal import PricingTier
        tier = PricingTier(
            tier_name="Starter",
            base_price_usd=2000.0,
            features=[],
            discount_percentage=0.0,
        )
        assert tier.effective_price == 2000.0

    def test_effective_price_with_10_percent_discount(self):
        from domain.entities.proposal import PricingTier
        tier = PricingTier(
            tier_name="Starter",
            base_price_usd=2000.0,
            features=[],
            discount_percentage=10.0,
        )
        assert tier.effective_price == 1800.0

    def test_annual_value_monthly_billing(self):
        from domain.entities.proposal import PricingTier
        tier = PricingTier(
            tier_name="Starter",
            base_price_usd=2000.0,
            features=[],
            discount_percentage=0.0,
            setup_fee_usd=500.0,
            billing_cycle="monthly",
        )
        # 2000 * 12 + 500
        assert tier.annual_value == 24_500.0
