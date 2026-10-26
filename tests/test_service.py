"""
tests/test_service.py
---------------------
Unit and integration tests for venturetwin_ml.service.
Verifies ML likelihood prediction, domain warnings, financial output labelling,
and what-if simulation behavior/limitations.
"""

import pytest
from venturetwin_ml.service import predict_startup, simulate_whatif


def test_predict_startup_basic():
    """Verify predict_startup returns expected schema and reasonable values."""
    payload = {
        "business_type": "Software",
        "budget": 250000.0,
        "location_tier": "Tier 1",
        "expected_monthly_revenue": 15000.0,
        "monthly_expenses": 8000.0,
        "num_employees": 4
    }
    result = predict_startup(payload)

    # Core keys check
    assert "relative_success_likelihood" in result
    assert "relative_likelihood_percentage" in result
    assert "relative_classification" in result
    assert "ml_model_evaluation" in result
    assert "operational_formula_estimates" in result
    assert "warnings" in result

    # Likelihood range check
    likelihood = result["relative_success_likelihood"]
    assert isinstance(likelihood, float)
    assert 0.0 <= likelihood <= 1.0
    assert result["relative_classification"] in [
        "High Relative Likelihood",
        "Moderate/Low Relative Likelihood"
    ]


def test_predict_startup_inr_conversion():
    """Verify INR budget conversion works properly."""
    payload_usd = {"business_type": "Software", "budget": 100000.0, "currency": "USD"}
    payload_inr = {"business_type": "Software", "budget": 8300000.0, "currency": "INR"}

    res_usd = predict_startup(payload_usd)
    res_inr = predict_startup(payload_inr)

    # 8,300,000 INR @ 83.0 = 100,000 USD, so likelihoods should match closely
    assert abs(res_usd["relative_success_likelihood"] - res_inr["relative_success_likelihood"]) < 0.005


def test_domain_warnings_and_tier3_india():
    """Verify domain fallback warnings, Tier 3 India mapping, and domain limitation notice."""
    # Unknown business type
    payload = {
        "business_type": "Space Mining Exploration",
        "budget": 500000.0,
        "location_tier": "Tier 3 India"
    }
    result = predict_startup(payload)
    warnings = result["warnings"]

    # Check fallback warning
    assert any("mapped to Software" in w for w in warnings)

    # Check Tier 3 India mapping warning
    assert any("Tier 3 India" in w and "Tamil Nadu" in w for w in warnings)

    # Check domain limitation warning
    assert any("VC-backed tech startups" in w for w in warnings)


def test_output_labelling_disclaimer():
    """
    CRITICAL REQUIREMENT:
    Verify revenue and profit are clearly labelled as user-entered formula estimates,
    NOT ML predictions.
    """
    payload = {
        "business_type": "Fintech",
        "budget": 100000.0,
        "expected_monthly_revenue": 20000.0,
        "monthly_expenses": 12000.0
    }
    result = predict_startup(payload)
    op = result["operational_formula_estimates"]

    assert op["estimated_annual_revenue"] == 240000.0
    assert op["estimated_annual_profit"] == 96000.0
    assert "calculation_source" in op
    assert "NOT an ML prediction" in op["calculation_source"]
    assert "disclaimer" in op
    assert "NOT" in op["disclaimer"] and "machine learning predictions" in op["disclaimer"]


def test_simulate_whatif_budget_sensitivity():
    """Verify what-if simulation increases likelihood when budget is increased."""
    base = {
        "business_type": "Software",
        "budget": 50000.0,
        "location_tier": "Tier 2",
        "expected_monthly_revenue": 5000.0,
        "monthly_expenses": 8000.0
    }
    changes = {"budget": 1000000.0}

    sim = simulate_whatif(base, changes)
    assert sim["hypothetical_likelihood"] > sim["current_likelihood"]
    assert "impact_summary" in sim
    assert "likelihood_change_percentage" in sim
    assert "base_operational_estimates" in sim
    assert "updated_operational_estimates" in sim


def test_whatif_limitation_operational_changes_do_not_alter_ml_likelihood():
    """
    CRITICAL LIMITATION:
    What-if adjustments only change ML likelihood through budget, business category, and location.
    Operational changes (expenses, employee count, stage, land) must update formula estimates
    but leave ML likelihood identical.
    """
    base = {
        "business_type": "Software",
        "budget": 200000.0,
        "location_tier": "Tier 1",
        "expected_monthly_revenue": 10000.0,
        "monthly_expenses": 5000.0,
        "num_employees": 2,
        "startup_stage": "Ideation",
        "has_land": False
    }
    operational_changes = {
        "monthly_expenses": 15000.0,
        "num_employees": 20,
        "startup_stage": "Growth",
        "has_land": True
    }

    sim = simulate_whatif(base, operational_changes)

    # ML likelihood MUST remain unchanged because the model does not take operational parameters
    assert sim["current_likelihood"] == sim["hypothetical_likelihood"]
    assert sim["likelihood_change_percentage"] == "+0.0%"

    # But operational estimates (revenue, profit, health score) MUST update
    base_profit = sim["base_operational_estimates"]["estimated_annual_profit"]
    new_profit = sim["updated_operational_estimates"]["estimated_annual_profit"]
    assert base_profit != new_profit
    assert sim["updated_operational_estimates"]["estimated_annual_profit"] == round((10000.0 * 12) - (15000.0 * 12), 2)


def test_invalid_input_handling():
    """Verify TypeError is raised when input is not a dict."""
    with pytest.raises(TypeError):
        predict_startup("invalid_string_input")

    with pytest.raises(TypeError):
        simulate_whatif("not_a_dict", {})
