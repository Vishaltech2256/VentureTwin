"""
tests/test_risk_and_health_scores.py
------------------------------------
Tests for operational financial calculations, risk classification, and health scores
computed deterministically in venturetwin_ml.
"""

import pytest
from venturetwin_ml.service import predict_startup


def test_health_score_stays_within_0_to_100_range():
    """Verify health score is always clamped between 0 and 100."""
    # Minimum scenario: no revenue, high expense, no bonus criteria
    worst_input = {
        "business_type": "Software",
        "budget": 10000.0,
        "expected_monthly_revenue": 0.0,
        "monthly_expenses": 10000.0,
        "funding_source": "None",
        "num_employees": 0,
        "startup_stage": "Ideation",
        "has_land": False
    }
    worst = predict_startup(worst_input)["operational_formula_estimates"]
    assert 0.0 <= worst["formula_health_score"] <= 100.0
    assert worst["formula_health_score"] == 50.0  # Base score with 0 bonuses

    # Maximum scenario: profitable, funded, 10 employees, growth stage, has land
    best_input = {
        "business_type": "Software",
        "budget": 500000.0,
        "expected_monthly_revenue": 50000.0,
        "monthly_expenses": 10000.0,
        "funding_source": "Investor",
        "num_employees": 10,
        "startup_stage": "Growth",
        "has_land": True
    }
    best = predict_startup(best_input)["operational_formula_estimates"]
    assert best["formula_health_score"] == 100.0


def test_10_diverse_profiles_risk_and_health():
    """Verify 10 diverse startup profiles and validate that risk/health match expected formula logic."""
    profiles = [
        # 1. Profitable, funded, growing
        ({"expected_monthly_revenue": 50000, "monthly_expenses": 20000, "funding_source": "Investor", "num_employees": 12, "startup_stage": "Growth", "has_land": True}, "Low", 100.0),
        # 2. Profitable, angel funded
        ({"expected_monthly_revenue": 30000, "monthly_expenses": 10000, "funding_source": "Angel Round", "num_employees": 8, "startup_stage": "Seed", "has_land": False}, "Low", 90.0),
        # 3. High Burn Unprofitable
        ({"expected_monthly_revenue": 40000, "monthly_expenses": 60000, "funding_source": "Investor", "num_employees": 15, "startup_stage": "Growth", "has_land": False}, "High", 80.0),
        # 4. Zero Revenue, Burning Cash
        ({"expected_monthly_revenue": 0, "monthly_expenses": 15000, "funding_source": "Bootstrapped", "num_employees": 2, "startup_stage": "Ideation", "has_land": False}, "High", 50.0),
        # 5. Extreme Cash Bleeding
        ({"expected_monthly_revenue": 5000, "monthly_expenses": 50000, "funding_source": "None", "num_employees": 1, "startup_stage": "Ideation", "has_land": False}, "High", 50.0),
        # 6. Modest Profit (<100k annual profit)
        ({"expected_monthly_revenue": 10000, "monthly_expenses": 6000, "funding_source": "Bootstrapped", "num_employees": 4, "startup_stage": "Seed", "has_land": False}, "Medium", 70.0),
        # 7. Barely Breakeven
        ({"expected_monthly_revenue": 10000, "monthly_expenses": 9900, "funding_source": "Investor", "num_employees": 6, "startup_stage": "Growth", "has_land": False}, "Medium", 90.0),
        # 8. Pre-revenue with strong backing
        ({"expected_monthly_revenue": 0, "monthly_expenses": 5000, "funding_source": "Investor", "num_employees": 6, "startup_stage": "Seed", "has_land": True}, "High", 90.0),
        # 9. Solopreneur Profitable
        ({"expected_monthly_revenue": 15000, "monthly_expenses": 3000, "funding_source": "Bootstrapped", "num_employees": 0, "startup_stage": "Seed", "has_land": False}, "Low", 70.0),
        # 10. Zombie (Rev == Exp)
        ({"expected_monthly_revenue": 10000, "monthly_expenses": 10000, "funding_source": "Bootstrapped", "num_employees": 2, "startup_stage": "Ideation", "has_land": False}, "High", 50.0),
    ]

    for p, exp_risk, exp_health in profiles:
        inp = dict(p)
        inp["business_type"] = "Software"
        inp["budget"] = 100000.0
        res = predict_startup(inp)["operational_formula_estimates"]
        assert res["formula_risk_level"] == exp_risk, f"Expected risk {exp_risk}, got {res['formula_risk_level']}"
        assert res["formula_health_score"] == exp_health, f"Expected health {exp_health}, got {res['formula_health_score']}"
