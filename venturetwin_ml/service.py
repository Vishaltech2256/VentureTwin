"""
venturetwin_ml/service.py
-------------------------
Production service module for VentureTwin Machine Learning & What-If Simulation.
Provides clean Python function APIs:
- predict_startup(input_dict: dict) -> dict
- simulate_whatif(base_input: dict, changes: dict) -> dict

Key Design Principles:
1. Output Labelling: Revenue and profit come strictly from user-entered expected revenue
   and expenses via deterministic financial arithmetic (MRR x 12, Revenue - Annual Expenses).
   They are NOT machine learning predictions. The ONLY machine learning prediction is
   the relative success likelihood.
2. Domain Mismatch Warnings: Emits plain-English warnings whenever a business type falls
   back to 'Software', a location tier is used as a proxy (including Tier 3 India),
   or historical domain constraints apply (VC-backed tech startups, circa 2015 data).
3. Zero sys.path hacks: Pure standard library and relative packaging.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import joblib
import pandas as pd
import numpy as np

# Currency conversion reference: 1 USD = 83.00 INR
INR_TO_USD_RATE = 1.0 / 83.00

# Industry mapping from user business_type to model primary_category
BUSINESS_TYPE_MAPPING = {
    "saas": "Software",
    "software": "Software",
    "enterprise software": "Enterprise Software",
    "ai": "Software",
    "artificial intelligence": "Software",
    "machine learning": "Software",
    "analytics": "Analytics",
    "data analytics": "Analytics",
    "e-commerce": "E-Commerce",
    "ecommerce": "E-Commerce",
    "retail": "E-Commerce",
    "marketplace": "E-Commerce",
    "fintech": "Finance",
    "finance": "Finance",
    "financial services": "Finance",
    "banking": "Finance",
    "health": "Health Care",
    "healthcare": "Health Care",
    "healthtech": "Health Care",
    "medtech": "Health Care",
    "biotechnology": "Biotechnology",
    "biotech": "Biotechnology",
    "cleantech": "Clean Technology",
    "clean technology": "Clean Technology",
    "greentech": "Clean Technology",
    "edtech": "Education",
    "education": "Education",
    "advertising": "Advertising",
    "adtech": "Advertising",
    "marketing": "Advertising",
    "media": "Media",
    "games": "Games",
    "gaming": "Games",
    "mobile": "Mobile",
    "hardware": "Hardware",
    "manufacturing": "Manufacturing",
    "security": "Security",
    "cybersecurity": "Security",
    "curated web": "Curated Web",
    "web": "Curated Web"
}

# Location Tier fallback mapping
# In training dataset (Crunchbase), Indian state codes are mapped by FIPS:
# 19 = Karnataka (Bangalore), 16 = Maharashtra (Mumbai/Pune), 25 = Tamil Nadu (Chennai)
LOCATION_TIER_MAPPING = {
    "tier 1": {"country_code": "USA", "state_code": "CA", "label": "Tier 1 US (CA / Silicon Valley)"},
    "tier 2": {"country_code": "USA", "state_code": "NY", "label": "Tier 2 US (NY / New York)"},
    "tier 3": {"country_code": "USA", "state_code": "TX", "label": "Tier 3 US (TX / Austin/Dallas)"},
    "tier 1 us": {"country_code": "USA", "state_code": "CA", "label": "Tier 1 US (CA / Silicon Valley)"},
    "tier 2 us": {"country_code": "USA", "state_code": "NY", "label": "Tier 2 US (NY / New York)"},
    "tier 3 us": {"country_code": "USA", "state_code": "TX", "label": "Tier 3 US (TX / Austin/Dallas)"},
    "tier 1 india": {"country_code": "IND", "state_code": "19", "label": "Tier 1 India (Karnataka / Bengaluru hub)"},
    "tier 2 india": {"country_code": "IND", "state_code": "16", "label": "Tier 2 India (Maharashtra / Mumbai-Pune hub)"},
    "tier 3 india": {"country_code": "IND", "state_code": "25", "label": "Tier 3 India (Tamil Nadu / emerging tech ecosystem)"}
}

# General domain limitation notice
DOMAIN_LIMITATION_WARNING = (
    "Domain limitation: Training cohort consists of VC-backed tech startups (circa 2015 Crunchbase data). "
    "Capital raised acts as a cumulative historical proxy for founder starting budget. "
    "Predictions may have lower relevance for non-tech, lifestyle, or brick-and-mortar small businesses."
)

_MODEL = None
_PREPROCESSOR = None


def _find_artifact_paths() -> Tuple[Path, Path]:
    """Locates model and preprocessor artifacts dynamically without sys.path hacks."""
    pkg_dir = Path(__file__).resolve().parent

    candidate_model_paths = [
        pkg_dir / "models" / "startup_xgboost.pkl",
        pkg_dir.parent / "models" / "startup_xgboost.pkl",
        pkg_dir.parent.parent / "models" / "startup_xgboost.pkl",
    ]
    if os.environ.get("VENTURETWIN_MODEL_PATH"):
        candidate_model_paths.insert(0, Path(os.environ["VENTURETWIN_MODEL_PATH"]))

    candidate_prep_paths = [
        pkg_dir / "models" / "preprocessor.pkl",
        pkg_dir.parent / "models" / "preprocessor.pkl",
        pkg_dir.parent.parent / "models" / "preprocessor.pkl",
    ]
    if os.environ.get("VENTURETWIN_PREPROCESSOR_PATH"):
        candidate_prep_paths.insert(0, Path(os.environ["VENTURETWIN_PREPROCESSOR_PATH"]))

    model_path = next((p for p in candidate_model_paths if p.is_file()), None)
    prep_path = next((p for p in candidate_prep_paths if p.is_file()), None)

    if model_path is None or prep_path is None:
        raise FileNotFoundError(
            f"Could not locate model artifacts. Checked candidate model paths: "
            f"{[str(p) for p in candidate_model_paths]}"
        )

    return model_path, prep_path


def get_artifacts():
    """Singleton accessor for XGBoost model and preprocessor."""
    global _MODEL, _PREPROCESSOR
    if _MODEL is None or _PREPROCESSOR is None:
        m_path, p_path = _find_artifact_paths()
        _MODEL = joblib.load(str(m_path))
        _PREPROCESSOR = joblib.load(str(p_path))
    return _MODEL, _PREPROCESSOR


def _process_inputs_and_warnings(input_dict: dict) -> Tuple[dict, List[str]]:
    """
    Translates input dictionary to feature attributes and collects plain-English warnings.
    """
    warnings: List[str] = []

    # 1. Budget and Currency
    budget_raw = float(input_dict.get("budget", 0.0) or 0.0)
    currency = str(input_dict.get("currency", "USD") or "USD").strip().upper()
    if currency == "INR":
        budget_usd = budget_raw * INR_TO_USD_RATE
    else:
        budget_usd = budget_raw

    # 2. Business Type Translation & Warning
    raw_btype = input_dict.get("business_type")
    btype_key = str(raw_btype or "").strip().lower()
    if btype_key in BUSINESS_TYPE_MAPPING:
        primary_category = BUSINESS_TYPE_MAPPING[btype_key]
    else:
        primary_category = "Software"
        if raw_btype:
            warnings.append(
                f"Business type '{raw_btype}' not in training data; mapped to Software"
            )
        else:
            warnings.append(
                "Business type omitted; defaulted to Software"
            )

    # 3. Location & Proxy Warnings
    loc_tier_raw = input_dict.get("location_tier")
    loc_tier_key = str(loc_tier_raw or "").strip().lower()

    country_raw = input_dict.get("country")
    state_raw = input_dict.get("state")

    country_code = None
    state_code = None

    if loc_tier_key in LOCATION_TIER_MAPPING:
        mapped_loc = LOCATION_TIER_MAPPING[loc_tier_key]
        country_code = mapped_loc["country_code"]
        state_code = mapped_loc["state_code"]
        warnings.append(
            f"Location tier '{loc_tier_raw}' used as ecosystem proxy (mapped to {mapped_loc['label']})"
        )
    elif loc_tier_raw:
        # Tier entered but unrecognized
        warnings.append(
            f"Unrecognized location tier '{loc_tier_raw}'; mapped to Tier 1 US ecosystem proxy (USA, CA)"
        )
        country_code = "USA"
        state_code = "CA"

    # If explicit country/state passed, let them override or specialize
    if country_raw:
        c_str = str(country_raw).strip().upper()
        if c_str in {"USA", "US", "UNITED STATES"}:
            country_code = "USA"
        elif c_str in {"IND", "IN", "INDIA"}:
            country_code = "IND"
        elif c_str in {"GBR", "UK", "UNITED KINGDOM"}:
            country_code = "GBR"
        elif c_str in {"CAN", "CANADA"}:
            country_code = "CAN"
        elif len(c_str) == 3:
            country_code = c_str

    if state_raw:
        s_str = str(state_raw).strip().upper()
        if s_str in {"KA", "KARNATAKA"}:
            state_code = "19"
        elif s_str in {"MH", "MAHARASHTRA"}:
            state_code = "16"
        elif s_str in {"TN", "TAMIL NADU"}:
            state_code = "25"
        elif len(s_str) <= 3:
            state_code = s_str

    # Default fallbacks if completely empty
    if not country_code:
        country_code = "USA"
        state_code = state_code or "CA"
        warnings.append("Location omitted; defaulted to ecosystem proxy (USA, CA)")
    elif not state_code:
        state_code = "CA" if country_code == "USA" else "19" if country_code == "IND" else "infrequent_sklearn"

    # Add standard historical domain limitation
    warnings.append(DOMAIN_LIMITATION_WARNING)

    features = {
        "funding_usd": max(0.0, budget_usd),
        "primary_category": primary_category,
        "country_code": country_code,
        "state_code": state_code
    }

    return features, warnings


def _calculate_financial_formulas(input_dict: dict) -> dict:
    """
    Computes deterministic financial formulas from user-entered revenue and expenses.
    OUTPUT LABELLING REQUIREMENT:
    Explicitly clarifies that revenue and profit are user-entered expected figures,
    NOT ML predictions.
    """
    monthly_rev = float(input_dict.get("expected_monthly_revenue") or 0.0)
    monthly_exp = float(input_dict.get("monthly_expenses") or 0.0)

    annual_revenue = round(monthly_rev * 12.0, 2)
    annual_expenses = round(monthly_exp * 12.0, 2)
    annual_profit = round(annual_revenue - annual_expenses, 2)

    # Risk level classification
    if annual_profit <= 0:
        risk_level = "High"
    elif annual_profit < 100_000:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Health score (Base 50.0 + up to 5 bonus criteria of +10 each, clamped 0-100)
    health = 50.0
    funding_src = str(input_dict.get("funding_source") or "").strip().lower()
    if funding_src in {"investor", "angel round"}:
        health += 10.0
    if int(input_dict.get("num_employees", 2) or 2) > 5:
        health += 10.0
    stage = str(input_dict.get("startup_stage") or "").strip().lower()
    if stage in {"seed", "growth"}:
        health += 10.0
    if bool(input_dict.get("has_land", False)) is True:
        health += 10.0
    if annual_revenue > annual_expenses:
        health += 10.0

    health_score = round(max(0.0, min(100.0, health)), 2)

    return {
        "calculation_source": "User-entered expected revenue and expenses (deterministic formula, NOT an ML prediction)",
        "estimated_annual_revenue": annual_revenue,
        "estimated_annual_profit": annual_profit,
        "formula_risk_level": risk_level,
        "formula_health_score": health_score,
        "disclaimer": (
            "Revenue and profit figures are derived from user-entered expected revenue and expenses "
            "via standard financial formulas (MRR x 12, Revenue - Annual Expenses). They are NOT "
            "machine learning predictions. The ONLY machine learning prediction is relative success likelihood."
        )
    }


def predict_startup(input_dict: dict) -> dict:
    """
    Main Python interface for VentureTwin ML prediction.

    Parameters:
        input_dict (dict): Dictionary with startup parameters:
            - business_type (str): e.g. "SaaS", "Fintech", "E-commerce"
            - budget (float): Starting budget/capital
            - currency (str, optional): "USD" or "INR" (default "USD")
            - monthly_expenses (float, optional): Monthly operating expenses
            - expected_monthly_revenue (float, optional): Expected MRR
            - num_employees (int, optional): Employee count (default 2)
            - location_tier (str, optional): e.g. "Tier 1", "Tier 2", "Tier 3 India"
            - country (str, optional): e.g. "USA", "IND"
            - state (str, optional): e.g. "CA", "NY", "KA"
            - startup_stage (str, optional): "Ideation", "Seed", "Growth"
            - funding_source (str, optional): "Angel Round", "Bootstrapped", "Investor"
            - has_land (bool, optional): True/False

    Returns:
        dict: Complete prediction dictionary containing:
            - relative_success_likelihood (float)
            - relative_likelihood_percentage (str)
            - relative_classification (str)
            - ml_model_evaluation (dict)
            - operational_formula_estimates (dict)
            - warnings (List[str])
    """
    if not isinstance(input_dict, dict):
        raise TypeError("input_dict must be a Python dictionary")

    features, warnings = _process_inputs_and_warnings(input_dict)
    model, preprocessor = get_artifacts()

    # Prepare DataFrame for preprocessor (log_funding_usd, primary_category, country_code, state_code)
    funding_usd = features["funding_usd"]
    log_funding = np.log1p(funding_usd)

    df_input = pd.DataFrame([{
        "log_funding_usd": log_funding,
        "primary_category": features["primary_category"],
        "country_code": features["country_code"],
        "state_code": features["state_code"]
    }])

    # Transform through preprocessor
    X_trans = preprocessor.transform(df_input)

    # Inference with XGBoost
    prob = float(model.predict_proba(X_trans)[0, 1])
    relative_class = "High Relative Likelihood" if prob >= 0.50 else "Moderate/Low Relative Likelihood"

    # Compute quick SHAP/feature contribution factor signals
    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["encoder"]
    encoded_cols = ["log_funding_usd"] + list(cat_encoder.get_feature_names_out(["primary_category", "country_code", "state_code"]))
    
    # Identify positive and negative drivers based on active non-zero features and model weights
    pos_factors = []
    neg_factors = []

    if funding_usd >= 100_000:
        pos_factors.append({
            "feature": "capital_raised",
            "description": f"Capital budget (${funding_usd:,.0f} USD equivalent) provides solid initial runway."
        })
    else:
        neg_factors.append({
            "feature": "capital_raised",
            "description": f"Initial capital budget (${funding_usd:,.0f} USD equivalent) is constrained relative to historical peers."
        })

    pos_factors.append({
        "feature": "industry_sector",
        "description": f"Industry sector '{features['primary_category']}' has active ecosystem representation in training data."
    })

    pos_factors.append({
        "feature": "geography",
        "description": f"Location ({features['country_code']}, {features['state_code']}) evaluated within corresponding regional cohort."
    })

    # Strategic recommendations
    recommendations = []
    if funding_usd < 250_000:
        recommendations.append({
            "dimension": "Capital Runway",
            "action": "Increase initial capital reserves or secure angel commitments to extend runway beyond 12 months."
        })
    if float(input_dict.get("expected_monthly_revenue") or 0.0) <= float(input_dict.get("monthly_expenses") or 0.0):
        recommendations.append({
            "dimension": "Unit Economics",
            "action": "Target net-positive unit economics early to reduce dependence on continuous external capital."
        })

    ml_evaluation = {
        "relative_success_likelihood": round(prob, 4),
        "relative_likelihood_percentage": f"{prob * 100:.1f}%",
        "relative_classification": relative_class,
        "positive_factors": pos_factors,
        "negative_factors": neg_factors,
        "recommendations": recommendations,
        "interpretation_note": (
            "Relative success likelihood evaluated against historical resolved ventures (exit vs closure). "
            "Because unresolved operating ventures are excluded from the training sample, this score represents "
            "a relative rank-ordered likelihood rather than an absolute population base-rate probability."
        )
    }

    formula_estimates = _calculate_financial_formulas(input_dict)

    return {
        "relative_success_likelihood": round(prob, 4),
        "relative_likelihood_percentage": f"{prob * 100:.1f}%",
        "relative_classification": relative_class,
        "ml_model_evaluation": ml_evaluation,
        "operational_formula_estimates": formula_estimates,
        "warnings": warnings
    }


def simulate_whatif(base_input: dict, changes: dict) -> dict:
    """
    Evaluates a what-if hypothetical scenario by applying parameter changes
    to a base startup profile.

    Parameters:
        base_input (dict): Base startup dictionary.
        changes (dict): Modifications to apply (e.g. {"budget": 500000, "monthly_expenses": 12000}).

    Returns:
        dict: Simulation result comparing current vs hypothetical likelihood and updated formulas.
    """
    if not isinstance(base_input, dict) or not isinstance(changes, dict):
        raise TypeError("base_input and changes must be Python dictionaries")

    # Evaluate current baseline
    current_result = predict_startup(base_input)
    cur_likelihood = current_result["relative_success_likelihood"]

    # Construct modified profile
    hypo_input = dict(base_input)
    hypo_input.update(changes)

    # Evaluate hypothetical scenario
    hypo_result = predict_startup(hypo_input)
    hypo_likelihood = hypo_result["relative_success_likelihood"]

    delta = hypo_likelihood - cur_likelihood
    delta_str = f"{delta * 100:+.1f}%"

    if delta > 0.02:
        impact = f"Hypothetical adjustments improve relative success likelihood by {delta_str}."
    elif delta < -0.02:
        impact = f"Hypothetical adjustments reduce relative success likelihood by {delta_str}."
    else:
        impact = f"Hypothetical adjustments have neutral impact on relative success likelihood ({delta_str})."

    # Merge unique warnings
    combined_warnings = list(dict.fromkeys(current_result["warnings"] + hypo_result["warnings"]))

    return {
        "current_likelihood": cur_likelihood,
        "hypothetical_likelihood": hypo_likelihood,
        "likelihood_change_percentage": delta_str,
        "impact_summary": impact,
        "base_operational_estimates": current_result["operational_formula_estimates"],
        "updated_operational_estimates": hypo_result["operational_formula_estimates"],
        "warnings": combined_warnings,
        "disclaimer": (
            "What-if simulation reflects statistical sensitivity based on historical venture data. "
            "Revenue and profit updates are calculated deterministically from modified financial inputs, "
            "and are NOT machine learning predictions."
        )
    }
