"""Business operations for generated startup report metadata and content."""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.ai_suggestion import AISuggestion
from app.models.prediction import Prediction
from app.models.report import Report
from app.models.startup_profile import StartupProfile

logger = logging.getLogger(__name__)



def _get_owned_startup(db: Session, startup_id: int, user_id: int) -> StartupProfile:
    """Fetch a startup and ensure it belongs to the authenticated user."""
    startup = (
        db.query(StartupProfile)
        .filter(StartupProfile.startup_id == startup_id)
        .first()
    )
    if startup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found",
        )
    if startup.user_id != user_id:
        logger.warning(
            "User %s attempted to access startup %s owned by user %s",
            user_id,
            startup_id,
            startup.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this startup profile",
        )
    return startup


def _get_report_record(db: Session, report_id: int) -> Report:
    """Fetch a report by ID or raise a consistent 404 response."""
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return report


def _get_latest_prediction(db: Session, startup_id: int) -> Prediction | None:
    """Return the most recently generated prediction for a startup, if any."""
    return (
        db.query(Prediction)
        .filter(Prediction.startup_id == startup_id)
        .order_by(Prediction.created_at.desc(), Prediction.prediction_id.desc())
        .first()
    )


def _as_float(value: Any) -> float | None:
    """Convert SQLAlchemy Numeric values to JSON-friendly floats."""
    return float(value) if value is not None else None


def _build_report_content(db: Session, report: Report) -> dict[str, Any]:
    """Assemble the current complete business report for a stored report record."""
    startup = report.startup
    financial = startup.financial_info
    team = startup.team_info
    location = startup.location
    land = startup.land_detail
    prediction = _get_latest_prediction(db, startup.startup_id)
    if prediction is not None:
        from app.services.prediction_service import _attach_ml_fields
        _attach_ml_fields(prediction, startup)

    suggestions = (

        db.query(AISuggestion)
        .filter(AISuggestion.startup_id == startup.startup_id)
        .order_by(AISuggestion.created_at.desc(), AISuggestion.suggestion_id.desc())
        .all()
    )

    return {
        "report_id": report.report_id,
        "startup_id": report.startup_id,
        "report_name": report.report_name,
        "report_path": report.report_path,
        "generated_on": report.generated_on,
        "startup": {
            "startup_id": startup.startup_id,
            "startup_name": startup.startup_name,
            "description": startup.startup_description,
            "industry": startup.industry,
            "business_type": startup.business_type,
            "stage": startup.startup_stage,
            "target_market": startup.target_market,
        },
        "financial": (
            {
                "initial_budget": _as_float(financial.initial_budget),
                "monthly_expenses": _as_float(financial.monthly_expenses),
                "expected_monthly_revenue": _as_float(
                    financial.expected_monthly_revenue
                ),
                "funding_source": financial.funding_source,
            }
            if financial
            else None
        ),
        "team": (
            {
                "founder": team.founder_name,
                "co_founder": team.has_cofounder,
                "employees": team.number_of_employees,
            }
            if team
            else None
        ),
        "business_location": (
            {
                "country": location.country,
                "state": location.state,
                "city": location.city,
                "address": location.business_address,
            }
            if location
            else None
        ),
        "land_details": (
            {
                "has_land": land.has_land,
                "land_status": land.land_status,
                "area": _as_float(land.land_area_sqft),
                "location": land.land_location,
                "value": _as_float(land.land_value),
                "monthly_rent": _as_float(land.monthly_rent),
                "expandable": land.expandable,
            }
            if land
            else None
        ),
        "prediction": (
            {
                "prediction_id": prediction.prediction_id,
                "revenue_prediction": _as_float(prediction.revenue_prediction),
                "profit_prediction": _as_float(prediction.profit_prediction),
                "risk_level": prediction.risk_level,
                "health_score": _as_float(prediction.health_score),
                "relative_success_likelihood": getattr(prediction, "relative_success_likelihood", None),
                "relative_likelihood_percentage": getattr(prediction, "relative_likelihood_percentage", None),
                "relative_classification": getattr(prediction, "relative_classification", None),
            }
            if prediction
            else None
        ),

        "ai_suggestions": [
            {
                "title": suggestion.title,
                "description": suggestion.description,
                "priority": suggestion.priority,
                "category": suggestion.category,
            }
            for suggestion in suggestions
        ],
    }


def generate_report(db: Session, startup_id: int, user_id: int) -> Report:
    """Persist metadata for a complete report after startup ownership validation."""
    _get_owned_startup(db, startup_id, user_id)

    if _get_latest_prediction(db, startup_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No prediction is available for this startup. "
                "Generate a prediction before creating a report."
            ),
        )

    generated_on = datetime.now(timezone.utc)
    report_name = f"Startup_Report_{startup_id}_{generated_on.year}.pdf"
    report_path = f"/reports/Startup_Report_{startup_id}.pdf"

    try:
        report = Report(
            startup_id=startup_id,
            report_name=report_name,
            report_path=report_path,
            generated_on=generated_on,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        logger.info("Generated report %s for startup %s", report.report_id, startup_id)
        return report
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to generate report for startup %s", startup_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the report.",
        )


def get_reports(db: Session, user_id: int) -> list[Report]:
    """Return metadata for reports that belong to the authenticated user."""
    try:
        return (
            db.query(Report)
            .join(StartupProfile, Report.startup_id == StartupProfile.startup_id)
            .filter(StartupProfile.user_id == user_id)
            .order_by(Report.generated_on.desc(), Report.report_id.desc())
            .all()
        )
    except SQLAlchemyError:
        logger.exception("Failed to fetch reports for user %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching reports.",
        )


def get_report(db: Session, report_id: int, user_id: int) -> dict[str, Any]:
    """Return a complete current business report after ownership verification."""
    try:
        report = _get_report_record(db, report_id)
        _get_owned_startup(db, report.startup_id, user_id)
        return _build_report_content(db, report)
    except HTTPException:
        raise
    except SQLAlchemyError:
        logger.exception("Failed to fetch report %s", report_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the report.",
        )


def delete_report(db: Session, report_id: int, user_id: int) -> None:
    """Delete one report record after ownership verification."""
    report = _get_report_record(db, report_id)
    _get_owned_startup(db, report.startup_id, user_id)

    try:
        db.delete(report)
        db.commit()
        logger.info("Deleted report %s", report_id)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to delete report %s", report_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the report.",
        )


def get_reports_for_startup(db: Session, startup_id: int, user_id: int) -> list[Report]:
    """Return all report metadata records belonging to a given startup."""
    _get_owned_startup(db, startup_id, user_id)
    return (
        db.query(Report)
        .filter(Report.startup_id == startup_id)
        .order_by(Report.generated_on.desc(), Report.report_id.desc())
        .all()
    )


def generate_report_pdf(db: Session, report_id: int, user_id: int) -> tuple[bytes, str]:
    """Render a downloadable PDF for the report using fpdf."""
    report_data = get_report(db, report_id, user_id)
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "VentureTwin - Startup Executive Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Report ID: #{report_id}  |  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    startup = report_data.get("startup", {})
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, f"1. Startup: {startup.get('startup_name', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, f"Description: {startup.get('description', 'N/A')}")
    pdf.cell(0, 6, f"Industry: {startup.get('industry', 'N/A')}  |  Type: {startup.get('business_type', 'N/A')}  |  Stage: {startup.get('stage', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    fin = report_data.get("financial") or {}
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "2. Financial Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Initial Budget: {fin.get('initial_budget', 0):,.2f}  |  Monthly Expenses: {fin.get('monthly_expenses', 0):,.2f}  |  Expected MRR: {fin.get('expected_monthly_revenue', 0):,.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Funding Source: {fin.get('funding_source', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    pred = report_data.get("prediction") or {}
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "3. Prediction & Twin Modeling", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    if pred:
        pdf.cell(0, 6, f"Projected Annual Revenue: {pred.get('revenue_prediction', 0):,.2f}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Projected Annual Profit: {pred.get('profit_prediction', 0):,.2f}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Formula Risk Level: {pred.get('risk_level', 'N/A')}  |  Health Score: {pred.get('health_score', 0):.0f}/100", new_x="LMARGIN", new_y="NEXT")
        if pred.get("relative_success_likelihood"):
            pdf.cell(0, 6, f"ML Relative Success Likelihood: {pred.get('relative_likelihood_percentage', 'N/A')} ({pred.get('relative_classification', 'N/A')})", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, "No prediction record linked.", new_x="LMARGIN", new_y="NEXT")

    filename = report_data.get("report_name") or f"report_{report_id}.pdf"
    return bytes(pdf.output()), filename

