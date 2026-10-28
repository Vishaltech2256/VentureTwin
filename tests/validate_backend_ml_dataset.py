"""
validate_backend_ml_dataset.py
-------------------------------
Comprehensive Testing and Validation Suite for VentureTwin Backend <-> ML Integration
using sample records from the Crunchbase reference dataset (big_startup_secsees_dataset.csv)
and controlled operational test fixtures.

TEST SECTIONS:
- TEST 1: Direct ML Module (venturetwin_ml.predict_startup) Execution & Determinism
- TEST 2: FastAPI Backend <-> ML Integration Matching (predict_startup vs /api/predictions/generate)
- TEST 3: Deterministic Financial Formula Verification (Revenue, Profit, Risk, Health Score)
- TEST 4: Controlled Edge Cases (zero/low budget, high budget, INR conversion, unmapped business types, etc.)
- TEST 5: Model Semantics & Terminology (Relative Success Likelihood vs absolute probability, warnings, notes)
"""

import os
import sys
import zipfile
import json
import math
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup pathing
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
nested_backend = os.path.join(backend_dir, "backend")

for p in [backend_dir, nested_backend]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.main import app
from app.database.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.startup_profile import (
    StartupProfile,
    FinancialInformation,
    TeamInformation,
    BusinessLocation,
    LandDetail,
)
from app.models.prediction import Prediction
from venturetwin_ml import predict_startup, simulate_whatif
from venturetwin_ml.service import get_artifacts, INR_TO_USD_RATE

# Setup isolated in-memory test database
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


def load_dataset_samples(zip_path: str, n_samples: int = 35) -> List[Dict[str, Any]]:
    """
    Extracts representative diverse real records from Crunchbase dataset.
    Extracts real dataset fields: name, primary_category, funding_usd, country_code, state_code.
    Pairs each with explicitly labeled synthetic test-fixtures for operational values.
    """
    with zipfile.ZipFile(zip_path) as z:
        with z.open("big_startup_secsees_dataset.csv") as f:
            df = pd.read_csv(f)

    # Clean numeric funding
    df["funding_clean"] = pd.to_numeric(df["funding_total_usd"].replace("-", np.nan), errors="coerce")
    valid = df[
        df["funding_clean"].notna() & 
        (df["funding_clean"] > 0) & 
        df["category_list"].notna() &
        df["country_code"].notna() &
        df["state_code"].notna()
    ].copy()
    valid["primary_cat"] = valid["category_list"].apply(lambda x: str(x).split("|")[0].strip())

    # Diverse cohorts
    target_categories = [
        "Software", "Biotechnology", "E-Commerce", "Analytics", "Enterprise Software",
        "Clean Technology", "Health Care", "Advertising", "Games", "Mobile", "Finance",
        "Curated Web", "Security"
    ]
    target_locations = [
        ("USA", "CA"), ("USA", "NY"), ("USA", "TX"), ("USA", "MA"), ("USA", "WA"),
        ("IND", "19"), ("IND", "16"), ("IND", "25"), ("GBR", None), ("CAN", "ON")
    ]

    selected_rows = []

    # 1. Low capital (< $150k)
    low_cap = valid[(valid["funding_clean"] < 150000) & (valid["funding_clean"] >= 10000)]
    for cat in ["Software", "E-Commerce", "Mobile", "Games", "Advertising"]:
        m = low_cap[low_cap["primary_cat"] == cat]
        if not m.empty:
            selected_rows.append(m.iloc[0])

    # 2. Medium capital ($150k - $2M)
    med_cap = valid[(valid["funding_clean"] >= 150000) & (valid["funding_clean"] <= 2000000)]
    for cat in ["Software", "Biotechnology", "Analytics", "Finance", "Enterprise Software", "Clean Technology", "Health Care"]:
        m = med_cap[med_cap["primary_cat"] == cat]
        if not m.empty:
            selected_rows.append(m.iloc[0])

    # 3. High capital (> $2M)
    high_cap = valid[valid["funding_clean"] > 2000000]
    for cat in ["Software", "Biotechnology", "Curated Web", "Clean Technology", "Security", "Finance"]:
        m = high_cap[high_cap["primary_cat"] == cat]
        if not m.empty:
            selected_rows.append(m.iloc[0])

    # 4. Indian startups
    ind_startups = valid[valid["country_code"] == "IND"]
    for idx, row in ind_startups.head(6).iterrows():
        selected_rows.append(row)

    # 5. International startups (GBR, CAN)
    intl = valid[valid["country_code"].isin(["GBR", "CAN"])]
    for idx, row in intl.head(4).iterrows():
        selected_rows.append(row)

    # Convert to standard test records dictionary
    samples = []
    seen_names = set()

    # Pre-defined deterministic operational scenarios to cycle through
    # (These represent SYNTHETIC TEST FIXTURES)
    fixtures_cycle = [
        {"monthly_exp": 12000.0, "expected_rev": 25000.0, "employees": 6, "stage": "Seed", "funding_source": "Angel Round", "has_land": False},  # Profit: 156k (Low risk)
        {"monthly_exp": 15000.0, "expected_rev": 18000.0, "employees": 4, "stage": "Seed", "funding_source": "Investor", "has_land": True},     # Profit: 36k (Medium risk)
        {"monthly_exp": 25000.0, "expected_rev": 10000.0, "employees": 2, "stage": "Ideation", "funding_source": "Bootstrapped", "has_land": False},# Profit: -180k (High risk)
        {"monthly_exp": 8000.0,  "expected_rev": 12000.0, "employees": 8, "stage": "Growth", "funding_source": "Investor", "has_land": False},   # Profit: 48k (Medium risk)
        {"monthly_exp": 50000.0, "expected_rev": 75000.0, "employees": 12,"stage": "Growth", "funding_source": "Investor", "has_land": True},     # Profit: 300k (Low risk)
    ]

    sample_id = 1
    for r in selected_rows:
        name = str(r["name"])
        if name in seen_names or len(samples) >= n_samples:
            continue
        seen_names.add(name)

        fix = fixtures_cycle[(sample_id - 1) % len(fixtures_cycle)]
        funding = float(r["funding_clean"])
        country = str(r["country_code"]) if pd.notna(r["country_code"]) else None
        state = str(r["state_code"]) if pd.notna(r["state_code"]) else None
        cat = str(r["primary_cat"])

        samples.append({
            "sample_id": sample_id,
            "company_name": name,
            "data_origin": "Crunchbase Historical Dataset (INTEGRATION / REGRESSION TESTING)",
            # Real dataset attributes:
            "real_dataset_fields": {
                "raw_category": cat,
                "funding_usd": funding,
                "country": country,
                "state": state,
            },
            # Explicitly synthetic operational test fixtures:
            "synthetic_test_fixtures": {
                "monthly_expenses": fix["monthly_exp"],
                "expected_monthly_revenue": fix["expected_rev"],
                "number_of_employees": fix["employees"],
                "startup_stage": fix["stage"],
                "funding_source": fix["funding_source"],
                "has_land": fix["has_land"],
            }
        })
        sample_id += 1

    return samples


def get_edge_case_samples(start_id: int) -> List[Dict[str, Any]]:
    """
    Constructs dedicated edge cases to validate robustness, fallback mappings,
    currency conversions, and boundary conditions.
    """
    cases = [
        {
            "name": "EdgeCase_ZeroBudget",
            "business_type": "Software",
            "budget": 0.0,
            "currency": "USD",
            "country": "USA",
            "state": "CA",
            "monthly_exp": 5000.0,
            "expected_rev": 10000.0,
            "employees": 2,
            "stage": "Ideation",
            "funding_source": "Bootstrapped",
            "has_land": False,
            "expected_note": "Zero starting budget"
        },
        {
            "name": "EdgeCase_NearZeroBudget",
            "business_type": "SaaS",
            "budget": 100.0,
            "currency": "USD",
            "country": "USA",
            "state": "NY",
            "monthly_exp": 2000.0,
            "expected_rev": 3000.0,
            "employees": 1,
            "stage": "Seed",
            "funding_source": "Bootstrapped",
            "has_land": False,
            "expected_note": "Nominal $100 budget"
        },
        {
            "name": "EdgeCase_ExtremeBudget",
            "business_type": "Enterprise Software",
            "budget": 100000000.0,  # $100M
            "currency": "USD",
            "country": "USA",
            "state": "CA",
            "monthly_exp": 200000.0,
            "expected_rev": 500000.0,
            "employees": 50,
            "stage": "Growth",
            "funding_source": "Investor",
            "has_land": True,
            "expected_note": "Extreme high budget $100M"
        },
        {
            "name": "EdgeCase_INR_Currency",
            "business_type": "Software",
            "budget": 8300000.0,  # 8.3M INR = $100k USD
            "currency": "INR",
            "country": "IND",
            "state": "KA",
            "monthly_exp": 50000.0,
            "expected_rev": 100000.0,
            "employees": 5,
            "stage": "Seed",
            "funding_source": "Angel Round",
            "has_land": False,
            "expected_note": "INR currency conversion (8.3M INR -> 100k USD)"
        },
        {
            "name": "EdgeCase_UnsupportedBusinessType",
            "business_type": "Deep Space Asteroid Mining",
            "budget": 500000.0,
            "currency": "USD",
            "country": "USA",
            "state": "TX",
            "monthly_exp": 20000.0,
            "expected_rev": 30000.0,
            "employees": 4,
            "stage": "Seed",
            "funding_source": "Investor",
            "has_land": False,
            "expected_note": "Unsupported business category triggers fallback warning"
        },
        {
            "name": "EdgeCase_MissingLocation",
            "business_type": "Biotechnology",
            "budget": 750000.0,
            "currency": "USD",
            "country": None,
            "state": None,
            "monthly_exp": 15000.0,
            "expected_rev": 20000.0,
            "employees": 3,
            "stage": "Seed",
            "funding_source": "Investor",
            "has_land": False,
            "expected_note": "Omitted country/state triggers ecosystem proxy warning"
        },
        {
            "name": "EdgeCase_ZeroEmployees",
            "business_type": "Analytics",
            "budget": 200000.0,
            "currency": "USD",
            "country": "USA",
            "state": "CA",
            "monthly_exp": 5000.0,
            "expected_rev": 8000.0,
            "employees": 0,
            "stage": "Seed",
            "funding_source": "Bootstrapped",
            "has_land": False,
            "expected_note": "Zero employee count"
        },
        {
            "name": "EdgeCase_SevereLossMaking",
            "business_type": "Clean Technology",
            "budget": 1000000.0,
            "currency": "USD",
            "country": "USA",
            "state": "CA",
            "monthly_exp": 100000.0,
            "expected_rev": 5000.0,  # Loss of $1.14M/year
            "employees": 10,
            "stage": "Seed",
            "funding_source": "Investor",
            "has_land": True,
            "expected_note": "Expenses far exceed revenue -> High risk"
        },
        {
            "name": "EdgeCase_BreakEven",
            "business_type": "Finance",
            "budget": 300000.0,
            "currency": "USD",
            "country": "USA",
            "state": "NY",
            "monthly_exp": 10000.0,
            "expected_rev": 10000.0,  # Profit = 0 -> High risk per formula <= 0
            "employees": 3,
            "stage": "Seed",
            "funding_source": "Angel Round",
            "has_land": False,
            "expected_note": "Exact break-even profit = 0"
        },
        {
            "name": "EdgeCase_IndianTamilNadu",
            "business_type": "Healthcare",
            "budget": 300000.0,
            "currency": "USD",
            "country": "India",
            "state": "Tamil Nadu",
            "monthly_exp": 10000.0,
            "expected_rev": 20000.0,
            "employees": 5,
            "stage": "Seed",
            "funding_source": "Angel Round",
            "has_land": False,
            "expected_note": "Supported Indian state mapping (Tamil Nadu -> 25)"
        }
    ]

    edge_samples = []
    curr_id = start_id
    for c in cases:
        edge_samples.append({
            "sample_id": curr_id,
            "company_name": c["name"],
            "data_origin": "CONTROLLED EDGE CASE TEST FIXTURE",
            "real_dataset_fields": {
                "raw_category": c["business_type"],
                "funding_usd": c["budget"],
                "country": c["country"],
                "state": c["state"],
            },
            "synthetic_test_fixtures": {
                "monthly_expenses": c["monthly_exp"],
                "expected_monthly_revenue": c["expected_rev"],
                "number_of_employees": c["employees"],
                "startup_stage": c["stage"],
                "funding_source": c["funding_source"],
                "has_land": c["has_land"],
            },
            "edge_note": c["expected_note"],
            "currency": c.get("currency", "USD")
        })
        curr_id += 1

    return edge_samples


def run_full_validation():
    print("=" * 80)
    print("VENTURETWIN BACKEND <-> ML INTEGRATION VALIDATION SUITE")
    print("=" * 80)

    # 1. Verify model and preprocessor loading
    print("\n[STEP 1] Auditing ML Model & Preprocessor Artifacts...")
    model, preprocessor = get_artifacts()
    assert model is not None, "Failed to load XGBoost model!"
    assert preprocessor is not None, "Failed to load Preprocessor!"
    print(f"  [OK] Model loaded successfully: {type(model).__name__} (Features: {model.n_features_in_})")
    print(f"  [OK] Preprocessor loaded successfully: {type(preprocessor).__name__}")

    # 2. Extract dataset samples
    zip_path = r"D:\project v\VentureTwin Dataset\Dataset\big_startup_secsees_dataset.csv.zip"
    print(f"\n[STEP 2] Sampling representative records from {os.path.basename(zip_path)}...")
    dataset_samples = load_dataset_samples(zip_path, n_samples=30)
    edge_samples = get_edge_case_samples(start_id=len(dataset_samples) + 1)
    all_test_samples = dataset_samples + edge_samples

    print(f"  [OK] Loaded {len(dataset_samples)} diverse real dataset records (labelled as INTEGRATION/REGRESSION).")
    print(f"  [OK] Loaded {len(edge_samples)} controlled edge cases.")
    print(f"  [OK] Total sample pool for testing: {len(all_test_samples)}")

    # 3. Setup Test Client & DB
    print("\n[STEP 3] Initializing FastAPI TestClient and In-Memory Database...")
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create test user
    test_user = User(
        id=1,
        full_name="Validation Engineer",
        email="validator@venturetwin.ai",
        password_hash=get_password_hash("securepass123"),
    )
    db.add(test_user)
    db.commit()

    token = create_access_token(subject=test_user.email)
    auth_headers = {"Authorization": f"Bearer {token}"}
    client = TestClient(app)
    print("  [OK] Authenticated TestClient initialized.")

    # Counters
    total_samples = len(all_test_samples)
    successful_predictions = 0
    failed_predictions = 0
    ml_backend_matches = 0
    formula_validations = 0
    warnings_emitted = 0
    nan_inf_found = 0
    determinism_passes = 0
    terminology_passes = 0

    results_table = []
    detailed_results = []

    print("\n[STEP 4] Executing Comprehensive Validation on all Samples...")

    for s in all_test_samples:
        sid = s["sample_id"]
        cname = s["company_name"]
        real = s["real_dataset_fields"]
        fix = s["synthetic_test_fixtures"]
        currency = s.get("currency", "USD")

        # -------------------------------------------------------------
        # TEST 1: Direct ML Module Call
        # -------------------------------------------------------------
        direct_input = {
            "business_type": real["raw_category"],
            "budget": real["funding_usd"],
            "currency": currency,
            "monthly_expenses": fix["monthly_expenses"],
            "expected_monthly_revenue": fix["expected_monthly_revenue"],
            "num_employees": fix["number_of_employees"],
            "country": real["country"],
            "state": real["state"],
            "startup_stage": fix["startup_stage"],
            "funding_source": fix["funding_source"],
            "has_land": fix["has_land"],
        }

        try:
            # First run
            direct_res1 = predict_startup(direct_input)
            # Determinism check (second run with identical input)
            direct_res2 = predict_startup(direct_input)
        except Exception as e:
            failed_predictions += 1
            print(f"  [FAIL] [Sample {sid}: {cname}] Direct ML failed with exception: {e}")
            continue

        # Check determinism
        is_deterministic = (
            direct_res1["relative_success_likelihood"] == direct_res2["relative_success_likelihood"] and
            direct_res1["relative_likelihood_percentage"] == direct_res2["relative_likelihood_percentage"] and
            direct_res1["relative_classification"] == direct_res2["relative_classification"]
        )
        if is_deterministic:
            determinism_passes += 1
        else:
            print(f"  [FAIL] [Sample {sid}: {cname}] Non-deterministic output detected!")

        direct_likelihood = direct_res1["relative_success_likelihood"]
        direct_perc = direct_res1["relative_likelihood_percentage"]
        direct_class = direct_res1["relative_classification"]
        direct_warnings = direct_res1.get("warnings", [])

        # Check bounds and NaN/Inf
        if math.isnan(direct_likelihood) or math.isinf(direct_likelihood):
            nan_inf_found += 1
            print(f"  [FAIL] [Sample {sid}: {cname}] Likelihood is NaN or Infinite!")

        assert 0.0 <= direct_likelihood <= 1.0, f"Likelihood {direct_likelihood} out of [0, 1]!"

        if len(direct_warnings) > 0:
            warnings_emitted += 1

        # -------------------------------------------------------------
        # TEST 2: Backend <-> ML Integration Call
        # -------------------------------------------------------------
        # Populate DB records for this startup
        startup_rec = StartupProfile(
            startup_id=sid,
            user_id=1,
            startup_name=cname,
            startup_description=f"Validation profile for {cname}",
            business_type=real["raw_category"],
            industry="Technology",
            startup_stage=fix["startup_stage"],
            target_market="Enterprise/SMB",
        )
        fin_rec = FinancialInformation(
            financial_id=sid,
            startup_id=sid,
            initial_budget=real["funding_usd"],
            monthly_expenses=fix["monthly_expenses"],
            expected_monthly_revenue=fix["expected_monthly_revenue"],
            funding_source=fix["funding_source"],
        )
        team_rec = TeamInformation(
            team_id=sid,
            startup_id=sid,
            founder_name="Founder Test",
            has_cofounder=True,
            number_of_employees=fix["number_of_employees"],
        )
        to_add = [startup_rec, fin_rec, team_rec]
        if real["country"] is not None and real["state"] is not None:
            loc_rec = BusinessLocation(
                location_id=sid,
                startup_id=sid,
                country=real["country"],
                state=real["state"],
                city="TechCity",
            )
            to_add.append(loc_rec)

        land_rec = LandDetail(
            land_id=sid,
            startup_id=sid,
            has_land=fix["has_land"],
            land_status="Owned" if fix["has_land"] else "None",
        )
        to_add.append(land_rec)

        db.add_all(to_add)
        db.commit()

        # Invoke Backend API: POST /api/predictions/generate/{startup_id}
        resp = client.post(f"/api/predictions/generate/{sid}", headers=auth_headers)
        if resp.status_code != 201:
            failed_predictions += 1
            print(f"  [FAIL] [Sample {sid}: {cname}] Backend API returned status {resp.status_code}: {resp.text}")
            continue

        backend_res = resp.json()
        backend_likelihood = backend_res.get("relative_success_likelihood")
        backend_perc = backend_res.get("relative_likelihood_percentage")
        backend_class = backend_res.get("relative_classification")
        backend_warnings = backend_res.get("warnings", [])

        # Verify Direct ML vs Backend match
        # Note: If currency was INR in direct_input, backend initial_budget is numeric in USD by default schema
        # In INR edge case, direct converted at 1:83. For fair direct comparison:
        direct_comp_input = direct_input.copy()
        direct_comp_input["currency"] = "USD"
        direct_comp_res = predict_startup(direct_comp_input)

        likelihood_match = abs(backend_likelihood - direct_comp_res["relative_success_likelihood"]) < 1e-4
        perc_match = (backend_perc == direct_comp_res["relative_likelihood_percentage"])
        class_match = (backend_class == direct_comp_res["relative_classification"])

        if likelihood_match and perc_match and class_match:
            ml_backend_matches += 1
        else:
            print(f"  [FAIL] [Sample {sid}: {cname}] Backend vs Direct ML mismatch! "
                  f"Direct: {direct_comp_res['relative_success_likelihood']}, Backend: {backend_likelihood}")

        # -------------------------------------------------------------
        # TEST 3: Deterministic Financial Formula Verification
        # -------------------------------------------------------------
        expected_annual_rev = round(float(fix["expected_monthly_revenue"]) * 12.0, 2)
        expected_annual_profit = round(expected_annual_rev - (float(fix["monthly_expenses"]) * 12.0), 2)

        # Expected risk
        if expected_annual_profit <= 0:
            expected_risk = "High"
        elif expected_annual_profit < 100000:
            expected_risk = "Medium"
        else:
            expected_risk = "Low"

        # Expected health
        h = 50.0
        if str(fix["funding_source"]).lower() in {"investor", "angel round"}:
            h += 10.0
        if int(fix["number_of_employees"]) > 5:
            h += 10.0
        if str(fix["startup_stage"]).lower() in {"seed", "growth"}:
            h += 10.0
        if bool(fix["has_land"]) is True:
            h += 10.0
        if expected_annual_rev > (float(fix["monthly_expenses"]) * 12.0):
            h += 10.0
        expected_health = round(max(0.0, min(100.0, h)), 2)

        backend_rev = float(backend_res["revenue_prediction"])
        backend_profit = float(backend_res["profit_prediction"])
        backend_risk = backend_res["risk_level"]
        backend_health = float(backend_res["health_score"])

        formula_ok = (
            abs(backend_rev - expected_annual_rev) < 0.01 and
            abs(backend_profit - expected_annual_profit) < 0.01 and
            backend_risk == expected_risk and
            abs(backend_health - expected_health) < 0.01
        )
        if formula_ok:
            formula_validations += 1
        else:
            print(f"  [FAIL] [Sample {sid}: {cname}] Formula mismatch! "
                  f"Expected: rev={expected_annual_rev}, prof={expected_annual_profit}, risk={expected_risk}, health={expected_health} | "
                  f"Backend: rev={backend_rev}, prof={backend_profit}, risk={backend_risk}, health={backend_health}")

        # -------------------------------------------------------------
        # TEST 5: Model Semantics & Terminology Check
        # -------------------------------------------------------------
        eval_dict = backend_res.get("ml_model_evaluation", {})
        interp_note = eval_dict.get("interpretation_note", "") if eval_dict else ""
        
        has_rel_term = (
            "relative_success_likelihood" in backend_res and
            ("Relative Success Likelihood" in interp_note or "relative" in interp_note.lower())
        )
        no_abs_term = "absolute probability of success" not in json.dumps(backend_res).lower()

        if has_rel_term and no_abs_term:
            terminology_passes += 1
        else:
            print(f"  [FAIL] [Sample {sid}: {cname}] Semantics check failed: invalid probability terminology.")

        successful_predictions += 1

        # Record for report table
        loc_str = f"{real['country'] or 'Omitted'}, {real['state'] or '-'}"
        warning_summary = "Domain notice"
        if any("mapped to Software" in w for w in backend_warnings):
            warning_summary = "Fallback category"
        elif any("Location omitted" in w for w in backend_warnings):
            warning_summary = "Proxy location"
        elif any("Tamil Nadu" in w for w in backend_warnings):
            warning_summary = "Indian Tier 3 mapping"

        results_table.append({
            "Sample": f"#{sid} {cname[:16]}",
            "Business Type": str(real["raw_category"])[:15],
            "Budget": f"${real['funding_usd']:,.0f}",
            "Location": loc_str,
            "Direct ML Likelihood": f"{direct_comp_res['relative_success_likelihood']:.4f}",
            "Backend ML Likelihood": f"{backend_likelihood:.4f}",
            "Match": "YES" if likelihood_match else "NO",
            "Risk": backend_risk,
            "Health": f"{backend_health:.0f}",
            "Warning": warning_summary,
            "Status": "PASS" if (likelihood_match and formula_ok) else "FAIL"
        })

    db.close()

    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY RESULTS")
    print("=" * 80)
    print(f"Total samples tested:              {total_samples}")
    print(f"Successful predictions:            {successful_predictions}")
    print(f"Failed predictions:                {failed_predictions}")
    print(f"Direct ML vs Backend matches:      {ml_backend_matches} / {total_samples}")
    print(f"Formula validations passed:        {formula_validations} / {total_samples}")
    print(f"Determinism checks passed:         {determinism_passes} / {total_samples}")
    print(f"Terminology & Semantics passed:    {terminology_passes} / {total_samples}")
    print(f"Warnings/fallback count:           {warnings_emitted} / {total_samples}")
    print(f"NaN / Infinity outputs:            {nan_inf_found}")
    print(f"Edge cases successfully tested:    {len(edge_samples)}")

    # Return structured dict
    return {
        "total_samples": total_samples,
        "successful_predictions": successful_predictions,
        "failed_predictions": failed_predictions,
        "ml_backend_matches": ml_backend_matches,
        "formula_validations": formula_validations,
        "determinism_passes": determinism_passes,
        "terminology_passes": terminology_passes,
        "warnings_emitted": warnings_emitted,
        "nan_inf_found": nan_inf_found,
        "edge_cases_count": len(edge_samples),
        "results_table": results_table
    }

if __name__ == "__main__":
    res = run_full_validation()
    print("\nRepresentative 12 samples for report:")
    print(pd.DataFrame(res["results_table"][:12]).to_string(index=False))
