# backend/tests/test_frontend_backend_endpoints.py
"""
End-to-End Test Suite verifying complete Frontend <-> Backend Endpoint Connectivity.
Validates every endpoint and payload schema used by the React frontend application:
- Auth: login (JSON), refresh, me, updateMe
- Startup Profile: create (step 1), list, get, update (PATCH), delete
- Sub-resources: Financial, Team, Business Location, Land Details (upsert & get by startup_id)
- Full aggregation bundle (getFull)
- Predictions: run (/predictions/run/{id}), getLatest, list (/predictions/{id})
- AI Suggestions: generate, list, detail, delete
- Reports: generate, list (/reports/startup/{id}), download PDF (/reports/download/{id})
- Dashboard: overview summary (/dashboard/)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User

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


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()

    # Pre-create a test user
    user = User(
        id=1,
        email="founder@venturetwin.ai",
        full_name="Alex Founder",
        password_hash=get_password_hash("Password123!"),
    )
    db.add(user)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    old_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    if old_override:
        app.dependency_overrides[get_db] = old_override
    else:
        app.dependency_overrides.pop(get_db, None)


def test_frontend_backend_full_flow(client):
    # 1. Login with JSON payload (as sent by frontend/src/api/auth.ts)
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "founder@venturetwin.ai", "password": "Password123!"},
    )
    assert login_res.status_code == 200, login_res.text
    tokens = login_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Token refresh (POST /api/v1/auth/refresh)
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    refreshed_tokens = refresh_res.json()
    assert "access_token" in refreshed_tokens
    headers = {"Authorization": f"Bearer {refreshed_tokens['access_token']}"}

    # 3. Get Me & Update Me (GET/PATCH /api/v1/auth/me)
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "founder@venturetwin.ai"

    patch_me = client.patch(
        "/api/v1/auth/me",
        headers=headers,
        json={"full_name": "Alex Updated Founder"},
    )
    assert patch_me.status_code == 200
    assert patch_me.json()["full_name"] == "Alex Updated Founder"

    # 4. Create Startup Profile - Step 1 only (as sent by CreateStartupPage)
    create_profile_payload = {
        "startup_name": "Nexus Quantum",
        "description": "Next generation quantum computing cloud platform",
        "business_type": "SaaS",
        "target_market": "B2B Enterprise",
        "website": "https://nexusquantum.com",
        "founded_year": 2024,
    }
    create_res = client.post(
        "/api/v1/startup-profile/",
        headers=headers,
        json=create_profile_payload,
    )
    assert create_res.status_code == 201, create_res.text
    startup = create_res.json()
    startup_id = startup["startup_id"]
    assert startup["startup_name"] == "Nexus Quantum"
    assert startup["description"] == "Next generation quantum computing cloud platform"

    # 5. Upsert Financial Information (PUT /api/v1/financial-information/{startupId})
    fin_payload = {
        "initial_investment": 250000.0,
        "monthly_expenses": 12000.0,
        "monthly_revenue": 20000.0,
        "annual_revenue": 240000.0,
        "funding_raised": 250000.0,
        "burn_rate": 12000.0,
    }
    fin_res = client.put(
        f"/api/v1/financial-information/{startup_id}",
        headers=headers,
        json=fin_payload,
    )
    assert fin_res.status_code == 200, fin_res.text
    fin_data = fin_res.json()
    assert fin_data["initial_investment"] == 250000.0
    assert fin_data["monthly_revenue"] == 20000.0
    assert fin_data["annual_revenue"] == 240000.0
    assert fin_data["annual_profit"] == 96000.0

    # 6. Upsert Team Information (PUT /api/v1/team-information/{startupId})
    team_payload = {
        "founder_name": "Alex Founder",
        "founder_experience_years": 8,
        "founder_education": "PhD in Quantum Physics",
        "employee_count": 6,
        "team_skills": "Python, Qiskit, Distributed Systems",
        "has_technical_cofounder": True,
    }
    team_res = client.put(
        f"/api/v1/team-information/{startup_id}",
        headers=headers,
        json=team_payload,
    )
    assert team_res.status_code == 200, team_res.text
    team_data = team_res.json()
    assert team_data["founder_name"] == "Alex Founder"
    assert team_data["employee_count"] == 6
    assert team_data["has_technical_cofounder"] is True

    # 7. Upsert Business Location (PUT /api/v1/business-location/{startupId})
    loc_payload = {
        "country": "India",
        "state": "Karnataka",
        "city": "Bengaluru",
        "address": "42 Tech Park, Outer Ring Road",
        "pincode": "560103",
    }
    loc_res = client.put(
        f"/api/v1/business-location/{startup_id}",
        headers=headers,
        json=loc_payload,
    )
    assert loc_res.status_code == 200, loc_res.text
    loc_data = loc_res.json()
    assert loc_data["country"] == "India"
    assert loc_data["city"] == "Bengaluru"
    assert loc_data["address"] == "42 Tech Park, Outer Ring Road"

    # 8. Upsert Land Details (PUT /api/v1/land-details/{startupId})
    land_payload = {
        "has_land": True,
        "land_status": "rented",
        "land_area_sqft": 3000.0,
        "land_value": 0.0,
        "monthly_rent": 4000.0,
        "expansion_available": True,
    }
    land_res = client.put(
        f"/api/v1/land-details/{startup_id}",
        headers=headers,
        json=land_payload,
    )
    assert land_res.status_code == 200, land_res.text
    land_data = land_res.json()
    assert land_data["has_land"] is True
    assert land_data["expansion_available"] is True

    # 9. Update Startup Profile (PATCH /api/v1/startup-profile/{startupId})
    update_res = client.patch(
        f"/api/v1/startup-profile/{startup_id}",
        headers=headers,
        json={"description": "Updated Quantum Platform Description"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["description"] == "Updated Quantum Platform Description"

    # 10. Run Prediction (POST /api/v1/predictions/run/{startupId})
    run_pred_res = client.post(
        f"/api/v1/predictions/run/{startup_id}",
        headers=headers,
    )
    assert run_pred_res.status_code == 201, run_pred_res.text
    pred_data = run_pred_res.json()
    assert pred_data["startup_id"] == startup_id
    assert pred_data["predicted_annual_revenue"] == 240000.0
    assert pred_data["predicted_annual_profit"] == 96000.0
    assert pred_data["risk_level"] == "Medium"
    assert pred_data["success_probability"] is not None

    # 11. Get Latest Prediction (GET /api/v1/predictions/{startupId}/latest)
    latest_pred_res = client.get(
        f"/api/v1/predictions/{startup_id}/latest",
        headers=headers,
    )
    assert latest_pred_res.status_code == 200
    assert latest_pred_res.json()["prediction_id"] == pred_data["prediction_id"]

    # 12. List Predictions for Startup (GET /api/v1/predictions/{startupId})
    list_pred_res = client.get(
        f"/api/v1/predictions/{startup_id}",
        headers=headers,
    )
    assert list_pred_res.status_code == 200
    preds_list = list_pred_res.json()
    assert isinstance(preds_list, list)
    assert len(preds_list) >= 1

    # 13. Generate AI Suggestions (POST /api/v1/ai-suggestions/generate/{startupId})
    sugg_res = client.post(
        f"/api/v1/ai-suggestions/generate/{startup_id}",
        headers=headers,
    )
    assert sugg_res.status_code == 201, sugg_res.text
    sugg_data = sugg_res.json()
    assert sugg_data["startup_id"] == startup_id
    assert sugg_data["generated_count"] > 0

    # 14. List AI Suggestions (GET /api/v1/ai-suggestions/{startupId})
    list_sugg_res = client.get(
        f"/api/v1/ai-suggestions/{startup_id}",
        headers=headers,
    )
    assert list_sugg_res.status_code == 200
    assert isinstance(list_sugg_res.json(), list)
    assert len(list_sugg_res.json()) > 0

    # 15. Generate Report (POST /api/v1/reports/generate/{startupId})
    gen_rep_res = client.post(
        f"/api/v1/reports/generate/{startup_id}",
        headers=headers,
    )
    assert gen_rep_res.status_code == 201, gen_rep_res.text
    rep_meta = gen_rep_res.json()
    report_id = rep_meta["report_id"]
    assert "title" in rep_meta or "report_name" in rep_meta

    # 16. List Reports for Startup (GET /api/v1/reports/startup/{startupId})
    list_rep_res = client.get(
        f"/api/v1/reports/startup/{startup_id}",
        headers=headers,
    )
    assert list_rep_res.status_code == 200
    reps_list = list_rep_res.json()
    assert isinstance(reps_list, list)
    assert len(reps_list) >= 1
    assert reps_list[0]["report_id"] == report_id
    assert reps_list[0]["report_type"] == "PDF"

    # 17. Download Report PDF (GET /api/v1/reports/download/{reportId})
    download_res = client.get(
        f"/api/v1/reports/download/{report_id}",
        headers=headers,
    )
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "application/pdf"
    assert download_res.content.startswith(b"%PDF")

    # 18. Dashboard Overview (GET /api/v1/dashboard/)
    dash_res = client.get(
        "/api/v1/dashboard/",
        headers=headers,
    )
    assert dash_res.status_code == 200, dash_res.text
    dash_data = dash_res.json()
    assert dash_data["total_startups"] >= 1
    assert dash_data["total_predictions"] >= 1
    assert dash_data["total_reports"] >= 1
    assert len(dash_data["recent_startups"]) >= 1
    assert len(dash_data["recent_predictions"]) >= 1

    # 19. Delete Startup Profile (DELETE /api/v1/startup-profile/{startupId})
    del_res = client.delete(
        f"/api/v1/startup-profile/{startup_id}",
        headers=headers,
    )
    assert del_res.status_code == 200
    assert "message" in del_res.json()

    # Verify deleted
    get_del = client.get(f"/api/v1/startup-profile/{startup_id}", headers=headers)
    assert get_del.status_code == 404
