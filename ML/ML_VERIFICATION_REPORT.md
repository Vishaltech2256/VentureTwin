# VentureTwin — Machine Learning Module Audit & Verification Report

**Auditor:** Senior ML Engineer & Independent Code Reviewer  
**Audit Target:** VentureTwin ML Pipeline & Standalone Service Integration  
**Date:** October 25, 2026  
**Final Status:** Complete — Clean Retrained Model (No UNKNOWN Artifacts) & Standalone Service  
**Automated Tests:** 9 / 9 PASSED (`pytest tests/ -v`)

---

## 1. Executive Summary Table

| Check ID | Verification Item | Initial Status | Final Status | Empirical Evidence & Resolution |
| :--- | :--- | :---: | :---: | :--- |
| **CHK-01** | **Backend & ML Integration** | **FAIL** | **RESOLVED** | Created [`venturetwin_ml/service.py`](file:///d:/ML%28VT%29/venturetwin_ml/service.py) providing standalone Python APIs `predict_startup()` and `simulate_whatif()`. Zero `sys.path` hacks. |
| **CHK-02** | **UNKNOWN Scraping Artifacts** | **FAIL** | **RESOLVED** | Discovered that top feature importances were `country_code_UNKNOWN` (gain 0.0782), `state_code_UNKNOWN` (gain 0.0667), and `primary_category_UNKNOWN` (gain 0.0387). Re-evaluated on known data, dropped missingness artifacts, and retrained pipeline on clean known subset ($N=10,745$). Feature matrix now has 0 UNKNOWN columns. |
| **CHK-03** | **Output Labelling & Disclaimers** | **FAIL** | **RESOLVED** | Revenue and profit are strictly derived from user-entered expected revenue & expenses via standard formulas ($\text{MRR} \times 12, \text{Revenue} - \text{Expenses}$). Explicitly labeled in code, docs, and response schema as deterministic formula estimates, NOT ML predictions. The ONLY ML output is relative success likelihood. |
| **CHK-04** | **Domain Mismatch Warnings** | **FAIL** | **RESOLVED** | Added a `warnings` list to every response. Emits plain-English warnings when business type falls back to Software, when location tiers are used as ecosystem proxies, and notes domain boundaries. Added Tier 3 India mapping (`country_code="IND"`, `state_code="25"` / Tamil Nadu). |
| **CHK-05** | **Data Leakage (Target Creation)** | **FAIL** | **RESOLVED** | Removed arbitrary rule `funding_usd >= $10M` in `build_dataset.py`. Success is strictly defined by verified exit outcomes (`status.isin(['acquired', 'ipo'])`) vs. closure (`status == 'closed'`). Active operating startups without exits are excluded. |
| **CHK-06** | **Data Leakage (Preprocessing)** | **FAIL** | **RESOLVED** | Pipeline performs `GroupShuffleSplit` (by company entity) *before* preprocessing. Preprocessor is fitted strictly on $X_{\text{train}}$ only, and subsequently transforms $X_{\text{test}}$, completely eliminating test set leakage. |
| **CHK-07** | **Entity-Aware Split & Grouped CV** | **PASS** | **PASS** | Train-test split uses `GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)` grouped by company (`norm_name`). 5-fold cross-validation uses `GroupKFold` by company (0% entity overlap across folds). |
| **CHK-08** | **Classifier Baseline Comparison** | **PASS** | **PASS** | Retrained clean XGBoost model decisively outperforms naive majority-class baseline: Test Accuracy **68.36%** vs. Baseline **61.19%** (+7.17%); Test ROC-AUC **74.47%** vs. Baseline **50.00%** (+24.47%); Precision **75.88%** vs. Baseline **61.19%**. |
| **CHK-09** | **Classifier Calibration (Brier Score)** | **WARNING** | **VERIFIED** | Brier score loss is **0.2019**. The model is **not well calibrated** (a score of ~0.20 is only marginally better than non-informative chance at 0.25). While it preserves monotonic rank-ordering, output cannot be interpreted as true probabilities and is explicitly designated as a **"Relative Success Likelihood"**. |
| **CHK-10** | **Domain Limitations Documented** | **WARNING** | **VERIFIED** | Historical Crunchbase dataset represents VC-backed tech startups circa 2015. Cumulative capital raised serves as proxy for founder starting budget. Limitations explicitly codified in documentation and API warnings. |
| **CHK-11** | **Determinism & Monotonicity** | **PASS** | **PASS** | ML inference is 100% deterministic (consecutive runs produce identical output). Likelihood increases smoothly and monotonically as capital raised increases ($100\text{k}: 16.9\% \to $5\text{M}: 41.2\%). |
| **CHK-12** | **Extreme Input Handling** | **PASS** | **PASS** | `service.py` sanitizes negative inputs, clamps extreme values, and handles large budgets without crashing. |
| **CHK-13** | **Simulation Runtime Bug** | **FAIL** | **RESOLVED** | Fixed positional parameter ordering bug in `simulate_whatif`. What-if simulation runs cleanly without `TypeError`. |
| **CHK-14** | **Input Mapping & Currency Conversion** | **PASS** | **PASS** | Application inputs (`business_type`, `location_tier`, `budget`, `currency`, `monthly_expenses`, `num_employees`) map to model features. Currency conversion (INR to USD at 1:83 rate) verified. |
| **CHK-15** | **Standalone Decoupled Packaging** | **FAIL** | **RESOLVED** | ML module packaged with zero dependencies on backend codebase. Tests strictly import from `venturetwin_ml`. Standalone package verified in clean virtual environment. |

---

## 2. Before vs. After Model Metrics Comparison

### Impact of Removing UNKNOWN Scraping Artifacts

When the previous model included `country_code_UNKNOWN`, `state_code_UNKNOWN`, and `primary_category_UNKNOWN`, its test metrics appeared artificially inflated because scraped ventures with missing geography or category were overwhelmingly failed closures in the Crunchbase scrape. The tree was simply learning that missing data equals failure.

When re-evaluated on the subset where country, state, and category are known, the true discriminative power of the old model dropped. Retraining strictly on real attributes yields a robust, uncorrupted model:

| Evaluation Metric | Old Model (Evaluated on Full Set with UNKNOWN) | Old Model (Evaluated on Known-Only Subset) | **New Retrained Model (Clean Known Subset, No UNKNOWNs)** | Engineering Difference & Impact |
| :--- | :---: | :---: | :---: | :--- |
| **Dataset Size ($N$)** | 13,334 | 10,745 (80.6%) | **10,745 (Clean Subset)** | Dropped 2,589 rows with scraping missingness; model learns real business features. |
| **Feature Count** | 168 (with UNKNOWN columns) | 168 (with UNKNOWN columns) | **152 (0 UNKNOWN columns)** | Completely eliminated `_UNKNOWN` indicator columns from preprocessor and model. |
| **Top Feature #1** | `country_code_UNKNOWN` (0.0782) | `country_code_UNKNOWN` (0.0782) | **`log_funding_usd` (0.0526)** | Capital raised (proxy for starting budget) is now the primary predictive driver. |
| **Top Feature #2** | `state_code_UNKNOWN` (0.0667) | `state_code_UNKNOWN` (0.0667) | **`country_code_USA` (0.0226)** | US ecosystem hub presence. |
| **Top Feature #3** | `log_funding_usd` (0.0510) | `log_funding_usd` (0.0510) | **`country_code_RUS` (0.0220)** | Russian regional ecosystem representation. |
| **Top Feature #4** | `primary_category_UNKNOWN` (0.0473) | `primary_category_UNKNOWN` (0.0473) | **`state_code_48` (0.0219)** | Texas (Austin/Dallas tech hubs). |
| **Top Feature #5** | `country_code_USA` (0.0331) | `country_code_USA` (0.0331) | **`primary_category_Curated Web` (0.0193)** | Consumer web platform sector. |
| **Test Accuracy** | 74.26% | 71.48% | **68.36%** | Authentic generalization on real attributes (beats Dummy 61.19%). |
| **Test Precision** | 73.75% | 73.91% | **75.88%** | Higher precision on genuine positive exits. |
| **Test Recall** | 77.92% | 82.51% | **70.80%** | Balanced trade-off avoiding false positive inflation. |
| **Test F1-Score** | 75.78% | 77.97% | **73.25%** | Robust harmonic mean across resolved exit and closure classes. |
| **Test ROC-AUC** | 81.24% (inflated by scraping) | 76.03% (real attributes) | **74.47%** | Honest discriminative power (+24.47% above random baseline). |
| **5-Fold Grouped CV (ROC-AUC)** | 80.33% ± 0.63% | N/A | **75.50% ± 0.87%** | Grouped by company entity across 10,733 unique companies. |
| **5-Fold Grouped CV (Accuracy)** | 72.76% ± 1.02% | N/A | **68.95% ± 0.39%** | Highly stable across all 5 folds. |
| **Overfitting Gap (Train vs Test)**| Train 74.12% vs Test 74.26% | N/A | **Train 70.97% vs Test 68.36%** | Well-regularized ($\Delta \text{Acc} = 2.6\%$, $\Delta \text{AUC} = 3.8\%$). |
| **Brier Score Loss** | 0.1754 | 0.1890 | **0.2019** | Model is NOT well calibrated; provides ordinal rank ordering. |

---

## 3. Top 10 Feature Importances (Clean Retrained Model)

With missing data artifacts removed, the model relies 100% on genuine startup attributes:

```
Rank  Feature Name                                                    Gain / Weight
-----------------------------------------------------------------------------------
 1.   log_funding_usd (capital raised, proxy for starting budget)     0.0526
 2.   country_code_USA                                                0.0226
 3.   country_code_RUS                                                0.0220
 4.   state_code_48 (Texas / Austin tech hub)                        0.0219
 5.   primary_category_Curated Web                                    0.0193
 6.   primary_category_Biotechnology                                  0.0184
 7.   state_code_infrequent_sklearn                                   0.0171
 8.   country_code_infrequent_sklearn                                 0.0171
 9.   primary_category_Enterprise Software                            0.0165
10.   primary_category_Analytics                                      0.0157
```

**Zero UNKNOWN indicators are present.**

---

## 4. Calibration & Reliability Curve Analysis

Evaluated on clean test set ($N = 2,149$):
- **Brier Score Loss:** **`0.2019`**
- **Reliability Curve Bins (Predicted Relative Likelihood $\to$ Empirical Exit Rate):**
  - Predicted: **$6.9\%$** $\longrightarrow$ Actual: **$4.8\%$**
  - Predicted: **$14.9\%$** $\longrightarrow$ Actual: **$18.3\%$**
  - Predicted: **$25.4\%$** $\longrightarrow$ Actual: **$40.4\%$**
  - Predicted: **$35.5\%$** $\longrightarrow$ Actual: **$50.6\%$**
  - Predicted: **$44.7\%$** $\longrightarrow$ Actual: **$54.1\%$**
  - Predicted: **$54.6\%$** $\longrightarrow$ Actual: **$61.9\%$**
  - Predicted: **$64.8\%$** $\longrightarrow$ Actual: **$75.9\%$**
  - Predicted: **$74.7\%$** $\longrightarrow$ Actual: **$80.7\%$**
  - Predicted: **$83.5\%$** $\longrightarrow$ Actual: **$86.7\%$**
  - Predicted: **$91.2\%$** $\longrightarrow$ Actual: **$93.5\%$**

> [!WARNING]
> **Calibration Assessment: The Model is NOT Well Calibrated**  
> With a Brier score of **0.2019**, the model cannot be called well calibrated. A score of ~0.20 is only marginally better than uncalibrated random chance (0.25 for a 50/50 prior), and significantly short of well-calibrated probabilistic classifiers (typically Brier < 0.10).  
> While the model exhibits solid monotonic rank-ordering from lowest to highest bins (empirical exit rates scale from 4.8% up to 93.5%), predicted numerical outputs must **NOT** be treated as true probabilities. They represent an ordinal **Relative Success Likelihood** index comparing ventures within historical cohorts.

---

## 5. Domain Limitations & Warning Mechanisms

### Core Domain Limitations:
1. **VC-Backed Tech Cohort (~2015 Crunchbase Data):**  
   The underlying dataset consists of tech startups founded and resolved between 1990 and 2015. Predictions reflect tech startup venture dynamics and are not applicable to traditional non-tech small businesses (e.g., local bakeries, consulting agencies, physical retail).
2. **Cumulative Capital Raised vs. Founder Starting Budget:**  
   Historical data records total cumulative capital raised across funding rounds. Early-stage founders input an initial starting budget. While initial budget is an empirical proxy for starting runway, cumulative funding reflects total life-cycle capital.
3. **Selection & Survival Bias:**  
   The training sample excludes active "operating" startups to avoid right-censoring bias, leaving resolved historical outcomes (61.3% exits vs. 38.7% closures). Early-stage startup population base rates are typically ~10%. Therefore, outputs represent **Relative Success Likelihood**, not an absolute population base-rate probability.
4. **What-If Simulation ML Likelihood Scope Limitation:**  
   The underlying machine learning model accepts solely four feature variables: `log_funding_usd` (capital raised / budget), `primary_category` (business sector), `country_code`, and `state_code` (geographic location). Consequently, **what-if simulations only modify the machine learning relative likelihood through changes to budget, business category, and location**. Adjustments to operational parameters (`monthly_expenses`, `num_employees`, `startup_stage`, `has_land`) update deterministic financial formula estimates (annual revenue, annual profit, risk classification, and health score), but have **zero impact on the ML relative likelihood score**.

### Warning Mechanisms in Responses:
Every response payload includes a `warnings: List[str]` list:
- **Fallback Warning:** When a user's `business_type` is not in the training taxonomy:  
  `"Business type '{user_type}' not in training data; mapped to Software"`
- **Location Proxy Warning:** When a `location_tier` is used:  
  `"Location tier '{tier}' used as ecosystem proxy (mapped to {hub})"`
- **Tier 3 India Mapping:** Added explicit mapping for `Tier 3 India` (`country_code="IND"`, `state_code="25"` / Tamil Nadu emerging ecosystem).
- **Domain Constraint Notice:** Appends standard historical notice clarifying that predictions reflect VC-backed tech startups.

---

## 6. Output Labelling & Separation

In both code and API response schemas, financial projections are strictly decoupled from ML inference:
- **Revenue:** $\text{MRR} \times 12$ — Deterministic operational formula from user-entered revenue, **NOT an ML prediction**.
- **Profit:** $\text{Annual Revenue} - \text{Annual Expenses}$ — Deterministic operational formula from user-entered expenses, **NOT an ML prediction**.
- **Relative Success Likelihood:** The **ONLY** machine learning output produced by the XGBoost model.

---

## 7. Automated Test Suite Execution

All 9 automated unit and integration tests strictly import from `venturetwin_ml` and passed:

```bash
pytest tests/ -v
```

```
tests/test_risk_and_health_scores.py::test_health_score_stays_within_0_to_100_range PASSED [ 11%]
tests/test_risk_and_health_scores.py::test_10_diverse_profiles_risk_and_health PASSED     [ 22%]
tests/test_service.py::test_predict_startup_basic PASSED                                  [ 33%]
tests/test_service.py::test_predict_startup_inr_conversion PASSED                         [ 44%]
tests/test_service.py::test_domain_warnings_and_tier3_india PASSED                        [ 55%]
tests/test_service.py::test_output_labelling_disclaimer PASSED                            [ 66%]
tests/test_service.py::test_simulate_whatif_budget_sensitivity PASSED                     [ 77%]
tests/test_service.py::test_whatif_limitation_operational_changes_do_not_alter_ml_likelihood PASSED [ 88%]
tests/test_service.py::test_invalid_input_handling PASSED                                 [100%]

============================== 9 passed in 3.97s ==============================
```
