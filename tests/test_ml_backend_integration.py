import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend directory is in sys.path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nested_backend = os.path.join(backend_root, "backend")
if nested_backend not in sys.path:
    sys.path.insert(0, nested_backend)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

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
from venturetwin_ml.service import get_artifacts

# Setup in-memory SQLite database for testing
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()

    # Create test users
    user1 = User(
        id=1,
        full_name="Founder One",
        email="founder1@example.com",
        password_hash=get_password_hash("password123"),
    )
    user2 = User(
        id=2,
        full_name="Founder Two",
        email="founder2@example.com",
        password_hash=get_password_hash("password123"),
    )
    db.add_all([user1, user2])
    db.commit()

    # Create Startup 1 for User 1 (Reference Test Input Profile)
    # {
    #   "business_type": "Software",
    #   "budget": 250000.0,
    #   "monthly_expenses": 12000.0,
    #   "expected_monthly_revenue": 20000.0,
    #   "num_employees": 4,
    #   "country": "USA",
    #   "state": "CA",
    #   "startup_stage": "Seed",
    #   "funding_source": "Angel Round",
    #   "has_land": false
    # }
    startup1 = StartupProfile(
        startup_id=1,
        user_id=1,
        startup_name="CloudMatrix AI",
        startup_description="AI infrastructure platform",
        business_type="Software",
        industry="Artificial Intelligence",
        startup_stage="Seed",
        target_market="Developers and Startups",
    )
    db.add(startup1)
    db.commit()

    fin1 = FinancialInformation(
        financial_id=1,
        startup_id=1,
        initial_budget=250000.0,
        monthly_expenses=12000.0,
        expected_monthly_revenue=20000.0,
        funding_source="Angel Round",
    )
    team1 = TeamInformation(
        team_id=1,
        startup_id=1,
        founder_name="Jane Doe",
        has_cofounder=True,
        number_of_employees=4,
    )
    loc1 = BusinessLocation(
        location_id=1,
        startup_id=1,
        country="USA",
        state="CA",
        city="San Francisco",
    )
    land1 = LandDetail(
        land_id=1,
        startup_id=1,
        has_land=False,
        land_status="None",
    )

    db.add_all([fin1, team1, loc1, land1])

    # Create Startup 2 for User 2 (for authorization tests)
    startup2 = StartupProfile(
        startup_id=2,
        user_id=2,
        startup_name="OtherTech",
        startup_description="Another tech company",
        business_type="Fintech",
        industry="Finance",
        startup_stage="Growth",
        target_market="Banks",
    )
    db.add(startup2)
    db.commit()

    fin2 = FinancialInformation(
        financial_id=2,
        startup_id=2,
        initial_budget=100000.0,
        monthly_expenses=5000.0,
        expected_monthly_revenue=15000.0,
        funding_source="Investor",
    )
    team2 = TeamInformation(
        team_id=2,
        startup_id=2,
        founder_name="Bob Smith",
        number_of_employees=6,
    )
    loc2 = BusinessLocation(
        location_id=2,
        startup_id=2,
        country="India",
        state="Karnataka",
        city="Bengaluru",
    )
    db.add_all([fin2, team2, loc2])

    # Create Startup 3 for User 1 with MISSING financial information
    startup3 = StartupProfile(
        startup_id=3,
        user_id=1,
        startup_name="IncompleteTech",
        startup_description="Incomplete startup profile",
        business_type="Biotech",
        industry="Healthcare",
        startup_stage="Ideation",
        target_market="Hospitals",
    )
    db.add(startup3)

    # Create Startup 4 for User 1 with unsupported business type and Indian location
    startup4 = StartupProfile(
        startup_id=4,
        user_id=1,
        startup_name="SpaceMining India",
        startup_description="Extraterrestrial mining",
        business_type="Space Mining Exploration",
        industry="Aerospace",
        startup_stage="Seed",
        target_market="Global",
    )
    db.add(startup4)
    db.commit()

    fin4 = FinancialInformation(
        financial_id=4,
        startup_id=4,
        initial_budget=500000.0,
        monthly_expenses=20000.0,
        expected_monthly_revenue=30000.0,
        funding_source="Investor",
    )
    loc4 = BusinessLocation(
        location_id=4,
        startup_id=4,
        country="India",
        state="Tamil Nadu",
        city="Chennai",
    )
    db.add_all([fin4, loc4])
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers_user1():
    token = create_access_token(subject="founder1@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user2():
    token = create_access_token(subject="founder2@example.com")
    return {"Authorization": f"Bearer {token}"}



# ---------------------------------------------------------------------------
# Test Cases (1 through 15)
# ---------------------------------------------------------------------------

def test_1_model_artifacts_load_successfully():
    """Verify ML model artifacts load via get_artifacts() without exceptions."""
    model, preprocessor = get_artifacts()
    assert model is not None
    assert preprocessor is not None


def test_2_predict_startup_returns_expected_structure():
    """Verify predict_startup returns the full contract schema with expected sanity checks."""
    test_input = {
        "business_type": "Software",
        "budget": 250000.0,
        "currency": "USD",
        "monthly_expenses": 12000.0,
        "expected_monthly_revenue": 20000.0,
        "num_employees": 4,
        "location_tier": "Tier 1",
        "startup_stage": "Seed",
        "funding_source": "Angel Round",
        "has_land": False,
    }
    res = predict_startup(test_input)

    assert "relative_success_likelihood" in res
    assert "relative_likelihood_percentage" in res
    assert "relative_classification" in res
    assert "ml_model_evaluation" in res
    assert "operational_formula_estimates" in res
    assert "warnings" in res

    # Verification against the reference test values (~0.2291, 22.9%, 240000 rev, 96000 profit, Medium, 80)
    assert abs(res["relative_success_likelihood"] - 0.2291) < 0.005
    assert res["relative_likelihood_percentage"] == "22.9%"
    assert res["relative_classification"] == "Moderate/Low Relative Likelihood"

    op = res["operational_formula_estimates"]
    assert op["estimated_annual_revenue"] == 240000.0
    assert op["estimated_annual_profit"] == 96000.0
    assert op["formula_risk_level"] == "Medium"
    assert op["formula_health_score"] == 80.0


def test_3_and_4_and_5_and_6_generate_prediction_endpoint(client, auth_headers_user1):
    """
    Test 3: Existing startup prediction endpoint still works.
    Test 4: Prediction record is saved in database.
    Test 5: Existing revenue/profit/risk/health fields remain correct.
    Test 6: Relative Success Likelihood is returned correctly.
    """
    response = client.post("/api/predictions/generate/1", headers=auth_headers_user1)
    assert response.status_code == 201

    data = response.json()

    # Test 3 & 4: Response received and primary keys populated
    assert "prediction_id" in data
    assert data["startup_id"] == 1
    assert "created_at" in data

    # Test 5: Existing formula fields remain mathematically correct
    # expected_monthly_revenue (20000) * 12 = 240000
    assert data["revenue_prediction"] == 240000.0
    # 240000 - (12000 * 12) = 96000
    assert data["profit_prediction"] == 96000.0
    # 96000 -> Medium risk
    assert data["risk_level"] == "Medium"
    # Base 50 + Angel Round (+10) + Seed (+10) + Rev > Exp (+10) = 80
    assert data["health_score"] == 80.0

    # Test 6: Relative Success Likelihood is returned and properly formatted
    assert "relative_success_likelihood" in data
    assert abs(data["relative_success_likelihood"] - 0.2291) < 0.005
    assert data["relative_likelihood_percentage"] == "22.9%"
    assert data["relative_classification"] == "Moderate/Low Relative Likelihood"
    assert "ml_model_evaluation" in data
    assert "warnings" in data

    # Verify record was persisted in DB
    db = TestingSessionLocal()
    pred_record = db.query(Prediction).filter(Prediction.prediction_id == data["prediction_id"]).first()
    assert pred_record is not None
    assert pred_record.startup_id == 1
    assert float(pred_record.revenue_prediction) == 240000.0
    assert float(pred_record.profit_prediction) == 96000.0
    db.close()


def test_7_unsupported_business_type_produces_warning(client, auth_headers_user1):
    """Test 7: Unsupported business type maps gracefully to Software with a warning."""
    response = client.post("/api/predictions/generate/4", headers=auth_headers_user1)
    assert response.status_code == 201
    data = response.json()

    warnings = data.get("warnings", [])
    assert any("mapped to Software" in w for w in warnings)


def test_8_indian_location_mapping_works(client, auth_headers_user1):
    """Test 8: Explicit Indian state (Tamil Nadu) maps to FIPS code 25 without errors."""
    response = client.post("/api/predictions/generate/4", headers=auth_headers_user1)
    assert response.status_code == 201
    data = response.json()

    assert data["relative_success_likelihood"] > 0.0
    ml_eval = data.get("ml_model_evaluation", {})
    geo_factors = [f for f in ml_eval.get("positive_factors", []) if f.get("feature") == "geography"]
    assert len(geo_factors) > 0
    assert "IND" in geo_factors[0]["description"]


def test_9_unauthorized_startup_access_remains_blocked(client, auth_headers_user1, auth_headers_user2):
    """Test 9: Unauthorized startup access remains blocked with 403 Forbidden or 401 Unauthorized."""
    # User 1 tries to generate prediction for User 2's startup (startup_id=2)
    res_forbidden = client.post("/api/predictions/generate/2", headers=auth_headers_user1)
    assert res_forbidden.status_code == 403

    # Unauthenticated request
    res_unauthorized = client.post("/api/predictions/generate/1")
    assert res_unauthorized.status_code == 401


def test_10_missing_financial_data_returns_correct_validation_error(client, auth_headers_user1):
    """Test 10: Missing financial data returns 400 Bad Request."""
    # Startup 3 has no financial information
    res = client.post("/api/predictions/generate/3", headers=auth_headers_user1)
    assert res.status_code == 400
    assert "Financial information is missing" in res.json()["detail"]


def test_11_existing_dashboard_still_works(client, auth_headers_user1):
    """Test 11: Existing dashboard endpoint still works and includes prediction with ML evaluation."""
    res = client.get("/api/dashboard/1", headers=auth_headers_user1)
    assert res.status_code == 200
    data = res.json()

    assert "startup_profile" in data
    assert "financial_information" in data
    assert "team_information" in data
    assert "business_location" in data
    assert "prediction" in data

    pred = data["prediction"]
    assert pred is not None
    assert pred["revenue_prediction"] == 240000.0
    assert pred["profit_prediction"] == 96000.0
    assert pred["relative_success_likelihood"] is not None
    assert pred["relative_likelihood_percentage"] == "22.9%"


def test_12_existing_report_generation_still_works(client, auth_headers_user1):
    """Test 12: Existing report generation still works and includes prediction with ML fields."""
    # Generate report for startup 1 (which now has a prediction)
    gen_res = client.post("/api/reports/generate/1", headers=auth_headers_user1)
    assert gen_res.status_code == 201
    report_meta = gen_res.json()
    report_id = report_meta["report_id"]

    # Fetch full report
    get_res = client.get(f"/api/reports/{report_id}", headers=auth_headers_user1)
    assert get_res.status_code == 200
    report_data = get_res.json()

    assert "startup" in report_data
    assert "prediction" in report_data
    pred_summary = report_data["prediction"]
    assert pred_summary is not None
    assert pred_summary["revenue_prediction"] == 240000.0
    assert pred_summary["profit_prediction"] == 96000.0
    assert pred_summary["relative_success_likelihood"] is not None
    assert pred_summary["relative_likelihood_percentage"] == "22.9%"


def test_13_existing_frontend_response_parsing_not_broken(client, auth_headers_user1):
    """Test 13: All original legacy fields are present with correct types and keys."""
    res = client.get("/api/predictions", headers=auth_headers_user1)
    assert res.status_code == 200
    records = res.json()
    assert len(records) > 0

    latest = records[0]
    required_legacy_keys = [
        "prediction_id",
        "startup_id",
        "revenue_prediction",
        "profit_prediction",
        "risk_level",
        "health_score",
        "created_at",
    ]
    for key in required_legacy_keys:
        assert key in latest, f"Missing required legacy key: {key}"
        assert latest[key] is not None

    assert isinstance(latest["revenue_prediction"], (int, float))
    assert isinstance(latest["profit_prediction"], (int, float))
    assert isinstance(latest["risk_level"], str)
    assert isinstance(latest["health_score"], (int, float))


def test_14_whatif_simulation_service():
    """Verify simulate_whatif behaves according to model limitations."""
    base_input = {
        "business_type": "Software",
        "budget": 100000.0,
        "expected_monthly_revenue": 10000.0,
        "monthly_expenses": 8000.0,
    }
    # Operational change does not change ML likelihood
    op_sim = simulate_whatif(base_input, {"monthly_expenses": 12000.0})
    assert op_sim["current_likelihood"] == op_sim["hypothetical_likelihood"]

    # Budget change does change ML likelihood
    budget_sim = simulate_whatif(base_input, {"budget": 1000000.0})
    assert budget_sim["hypothetical_likelihood"] > budget_sim["current_likelihood"]


def test_15_openapi_swagger_loads_cleanly(client):
    """Test 15: OpenAPI/Swagger JSON schema loads without errors."""
    res = client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert "paths" in schema
    assert "/api/predictions/generate/{startup_id}" in schema["paths"]
    assert "/api/dashboard/{startup_id}" in schema["paths"]
    assert "/api/reports/generate/{startup_id}" in schema["paths"]


def test_16_ai_suggestions_generation_and_retrieval(client, auth_headers_user1):
    """Test 16: Verify AI suggestions are generated (>0), persisted, and retrieved via GET."""
    # Ensure prediction exists
    client.post("/api/predictions/generate/1", headers=auth_headers_user1)

    # Generate suggestions
    gen_res = client.post("/api/ai-suggestions/generate/1", headers=auth_headers_user1)
    assert gen_res.status_code == 201
    gen_data = gen_res.json()

    assert gen_data["startup_id"] == 1
    assert gen_data["prediction_id"] > 0
    assert gen_data["generated_count"] > 0

    assert len(gen_data["suggestions"]) == gen_data["generated_count"]

    # Verify at least one suggestion incorporates ML Relative Success Likelihood
    ml_suggs = [
        s for s in gen_data["suggestions"]
        if "Relative Success Likelihood" in s["description"]
    ]
    assert len(ml_suggs) > 0
    assert "22.9%" in ml_suggs[0]["description"]
    assert "Relative Success Likelihood" in ml_suggs[0]["description"]
    # Ensure it NEVER claims absolute probability of success
    assert "absolute probability" not in ml_suggs[0]["description"].lower()

    # Verify GET /api/ai-suggestions/1 returns the persisted records
    get_res = client.get("/api/ai-suggestions/1", headers=auth_headers_user1)
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert len(retrieved) == gen_data["generated_count"]

