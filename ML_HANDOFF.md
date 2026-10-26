# VentureTwin — Machine Learning Engineering Handoff (`ML_HANDOFF.md`)

**Module Version:** 2.1 (Configuration B — Clean Known Retraining & Standalone Service)  
**Primary Python Service:** `venturetwin_ml/service.py` (`predict_startup`, `simulate_whatif`)  
**Trained Artifacts:** `venturetwin_ml/models/startup_xgboost.pkl`, `venturetwin_ml/models/preprocessor.pkl`  
**Target Environment:** Python 3.11+, Scikit-learn, XGBoost, Pandas, NumPy, Joblib  
**Date:** October 25, 2026  

---

## 1. Executive Summary & Architecture

The VentureTwin Machine Learning module provides founders and investors with an **Explainable Relative Success Likelihood** evaluated against historical startup outcomes. It is engineered specifically for **Pre-Launch / Day-0** viability assessment, strictly isolating pre-launch attributes (capital raised, industry category, geographic hub) from post-launch milestones to prevent target leakage.

```
+-----------------------------------------------------------------------------------------+
|                                VENTURETWIN HYBRID ARCHITECTURE                          |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|   App / Founder Inputs (JSON Dictionary):                                               |
|   - business_type, budget (USD/INR), location_tier, monthly_expenses, num_employees     |
|                                       │                                                 |
|                   ┌───────────────────┴───────────────────┐                             |
|                   ▼                                       ▼                             |
|       [ Input Feature Translation ]           [ Operational Formula Engine ]            |
|       - Currency: INR -> USD (1:83)           - Revenue = MRR x 12                      |
|       - Category: business_type -> sector     - Profit = Revenue - Annual Expenses      |
|       - Location: tier -> ISO code            - Risk Level = High / Med / Low           |
|       - Warnings: Fallbacks & Proxies         - Health Score = 50 + Bonuses (0-100)     |
|                   │                           - Explicit: NOT ML predictions            |
|                   ▼                                       │                             |
|       [ Preprocessor & XGBoost ]                          │                             |
|       - One-Hot Encoder (min_freq=20)                     │                             |
|       - Standard Scaler (fitted on train)                 │                             |
|       - Feature attributions                              │                             |
|       - 0 UNKNOWN indicator columns                       │                             |
|                   │                                       │                             |
|                   └───────────────────┬───────────────────┘                             |
|                                       ▼                                                 |
|   Output Payload (Service Dict & API Response):                                         |
|   1. relative_success_likelihood (0.0 to 1.0) & percentage                              |
|   2. ml_model_evaluation (drivers, recommendations, interpretation note)                |
|   3. operational_formula_estimates (Annual Revenue, Profit, Risk, Health Score)         |
|   4. warnings (Plain-English list: sector fallbacks, location proxies, domain notices) |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Model Metrics & Calibration Evaluation

### UNKNOWN Scraping Artifacts Removal & Clean Retraining

In initial audits, the top feature importances were `country_code_UNKNOWN` (gain 0.0782), `state_code_UNKNOWN` (gain 0.0667), and `primary_category_UNKNOWN` (gain 0.0387). These represented scraping incompleteness in the Crunchbase scrape, NOT startup business quality.

To eliminate this bias:
1. All records with missing/UNKNOWN category, country, or state were filtered out, leaving a clean dataset of $N=10,745$ resolved ventures.
2. The preprocessor and XGBoost model were retrained on this clean subset.
3. Zero UNKNOWN columns exist in the feature matrix; missing or unseen categories gracefully map to reference baseline via `OneHotEncoder(handle_unknown="ignore")`.

| Evaluation Metric | Old Model (Full Set with UNKNOWN) | Old Model (Evaluated on Known Subset) | **New Retrained Model (Clean Known Subset)** | Engineering Assessment |
| :--- | :---: | :---: | :---: | :--- |
| **Dataset Size ($N$)** | 13,334 | 10,745 | **10,745 (Clean Subset)** | Filtered out scraping missingness artifacts. |
| **Feature Count** | 168 | 168 | **152 (0 UNKNOWN columns)** | UNKNOWN columns completely eliminated. |
| **Top Feature #1** | `country_code_UNKNOWN` (0.0782) | `country_code_UNKNOWN` (0.0782) | **`log_funding_usd` (0.0526)** | Capital raised is now the primary predictive driver. |
| **Top Feature #2** | `state_code_UNKNOWN` (0.0667) | `state_code_UNKNOWN` (0.0667) | **`country_code_USA` (0.0226)** | US tech ecosystem presence. |
| **Top Feature #3** | `log_funding_usd` (0.0510) | `log_funding_usd` (0.0510) | **`country_code_RUS` (0.0220)** | Russian regional ecosystem representation. |
| **Top Feature #4** | `primary_category_UNKNOWN` (0.0473) | `primary_category_UNKNOWN` (0.0473) | **`state_code_48` (0.0219)** | Texas (Austin/Dallas tech hubs). |
| **Test Accuracy** | 74.26% | 71.48% | **68.36%** | Authentic generalization on real attributes (beats Dummy 61.19%). |
| **Test Precision** | 73.75% | 73.91% | **75.88%** | Higher precision on genuine positive exits. |
| **Test Recall** | 77.92% | 82.51% | **70.80%** | Balanced trade-off avoiding false positive inflation. |
| **Test F1-Score** | 75.78% | 77.97% | **73.25%** | Robust harmonic mean across resolved exit and closure classes. |
| **Test ROC-AUC** | 81.24% (inflated by scraping) | 76.03% (real attributes) | **74.47%** | Honest discriminative power (+24.47% above random baseline). |
| **5-Fold Grouped CV (ROC-AUC)** | 80.33% ± 0.63% | N/A | **75.50% ± 0.87%** | Grouped by company entity across 10,733 unique companies. |
| **5-Fold Grouped CV (Accuracy)** | 72.76% ± 1.02% | N/A | **68.95% ± 0.39%** | Highly stable across all 5 folds. |
| **Brier Score Loss** | 0.1754 | 0.1890 | **0.2019** | Model is NOT well calibrated; provides ordinal rank ordering. |

> [!WARNING]
> **Calibration Reality: The Model is NOT Well Calibrated**  
> With a Brier score loss of **0.2019**, the model cannot be characterized as well calibrated in absolute probability terms (0.25 is uninformative random guessing). While it preserves monotonic rank-ordering across bins, predicted values must **NOT** be interpreted as true probabilities; they represent an ordinal **Relative Success Likelihood** index comparing ventures within historical cohorts.

---

## 3. Domain Limitations & Warning System

### Fundamental Domain Limitations
1. **VC-Backed Tech Startups (~2015 Historical Data):**  
   The underlying dataset consists of historical tech startups funded between 1990 and 2015. Predictions reflect tech startup venture dynamics and are not applicable to traditional non-tech small businesses (e.g., local bakeries, consulting agencies, physical retail).
2. **Cumulative Capital Raised vs. Founder Starting Budget:**  
   Historical data records total cumulative capital raised across funding rounds. Early-stage founders input an initial starting budget. While initial budget is an empirical proxy for starting runway, cumulative funding reflects total life-cycle capital.
3. **Selection & Survival Bias:**  
   The training sample excludes active "operating" startups to avoid right-censoring bias, leaving resolved historical outcomes (61.3% exits vs. 38.7% closures). Early-stage startup population base rates are typically ~10%. Therefore, outputs represent **Relative Success Likelihood**, not an absolute population base-rate probability.
4. **What-If Simulation ML Likelihood Scope Limitation:**  
   The XGBoost model operates solely on four input features: `log_funding_usd` (budget), `primary_category` (business type), `country_code`, and `state_code` (location). Therefore, what-if simulations **only change the machine learning relative likelihood through modifications to budget, business category, and location**. Adjusting operational inputs (e.g., `monthly_expenses`, `num_employees`, `startup_stage`, `has_land`) updates deterministic financial formula estimates (revenue, profit, runway, health score), but has **zero impact on the ML likelihood score**.

### Warning Mechanisms in Responses
Every response payload includes a `warnings: List[str]` list:
- **Fallback Warning:** When a user's `business_type` is not in the training taxonomy:  
  `"Business type '{user_type}' not in training data; mapped to Software"`
- **Location Proxy Warning:** When a `location_tier` is used:  
  `"Location tier '{tier}' used as ecosystem proxy (mapped to {hub})"`
- **Tier 3 India Mapping:** Added explicit mapping for `Tier 3 India` (`country_code="IND"`, `state_code="25"` / Tamil Nadu emerging ecosystem).
- **Domain Constraint Notice:** Appends standard historical notice clarifying that predictions reflect VC-backed tech startups.

---

## 4. Output Labelling: ML Likelihood vs. Financial Formulas

> [!IMPORTANT]
> **Strict Separation of Estimates:**  
> - **Revenue and Profit:** Calculated strictly from user-entered expected monthly revenue and expenses via deterministic financial formulas ($\text{MRR} \times 12, \text{Revenue} - \text{Annual Expenses}$). They are **NOT** machine learning predictions.
> - **Relative Success Likelihood:** The **ONLY** machine learning output produced by the XGBoost model.

---

## 5. Python Service Interface & Quickstart

The module provides standalone Python functions in `venturetwin_ml/service.py` with zero `sys.path` hacks.

### Quickstart Example:

```python
from venturetwin_ml.service import predict_startup, simulate_whatif

# 1. Predict Startup
result = predict_startup({
    "business_type": "Fintech",
    "budget": 250000.0,
    "currency": "USD",
    "monthly_expenses": 10000.0,
    "expected_monthly_revenue": 15000.0,
    "location_tier": "Tier 3 India"
})

print("Likelihood:", result["relative_likelihood_percentage"])
print("Warnings:", result["warnings"])
print("Financials:", result["operational_formula_estimates"])

# 2. What-If Simulation
sim = simulate_whatif(
    base_input={"business_type": "SaaS", "budget": 100000.0, "monthly_expenses": 8000.0},
    changes={"budget": 500000.0, "monthly_expenses": 12000.0}
)
print("Impact:", sim["impact_summary"])
print("Change:", sim["likelihood_change_percentage"])
```
