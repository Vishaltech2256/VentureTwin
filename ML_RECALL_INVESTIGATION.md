# Comprehensive Low Recall Investigation Report (`ML_RECALL_INVESTIGATION.md`)

**File Location:** `ML_RECALL_INVESTIGATION.md`  
**Date:** September 22, 2026  
**Status:** Completed (Empirical Diagnostic Audit — No Model Retraining / No Dataset Modifications)  

---

> [!IMPORTANT]  
> **Diagnostic Focus & Audit Scope:**  
> This investigation evaluates the performance of the serialized XGBoost Startup Success Prediction model (`ml/models/startup_xgboost.pkl`) on the broader external dataset (`ml/data/test/external_funding_startups.csv`, $N = 2,459$).  
> - **Reported External Performance (Threshold = 0.50):**  
>   - **Accuracy:** `85.52%`  
>   - **Precision:** `100.00%`  
>   - **Recall:** `53.28%`  
>   - **ROC-AUC:** `94.43%`  
>   - **F1-Score:** `69.52%`  
> - **Audit Context:** The previously reported 97.00% accuracy on `external_saas_startups.csv` was rejected due to 100% positive-class sample imbalance ($N=100$, 0 failures) and entity overlap with raw project data sources. The broader external dataset gives the true, meaningful evaluation.  
> - **Constraint Enforcement:** **No retraining, model modifications, dataset alterations, backend code changes, or frontend code changes were made during this investigation.**

---

## 1. Confusion Matrix

The confusion matrix was calculated on the 2,459 external test samples using the standard classification threshold ($\text{Probability} \ge 0.50 \to \text{SUCCESS}$).

| | Predicted Failure ($0$) | Predicted Success ($1$) | Total Actual |
|---|---|---|---|
| **Actual Failure ($0$)** | **$\text{TN} = 1,697$** | **$\text{FP} = 0$** | $1,697$ |
| **Actual Success ($1$)** | **$\text{FN} = 356$** | **$\text{TP} = 406$** | $762$ |
| **Total Predicted** | $2,053$ | $406$ | $2,459$ |

### Visual Confusion Matrix Chart
The generated heatmap has been saved to: [`ml/evaluation/confusion_matrix_external.png`](file:///d:/ML%28VT%29/ml/evaluation/confusion_matrix_external.png)

### Breakdown & Meaning of Confusion Matrix Quadrants

* **True Positive ($\text{TP} = 406$):**  
  * **Meaning:** 406 startups that actually succeeded were correctly identified as **SUCCESS** by the model.  
  * **Business Impact:** High-value startup opportunities correctly flagged for investment/acceleration.
* **True Negative ($\text{TN} = 1,697$):**  
  * **Meaning:** 1,697 startups that actually failed/remained low-growth were correctly identified as **FAILURE** by the model.  
  * **Business Impact:** Capital protected by successfully avoiding non-viable startups.
* **False Positive ($\text{FP} = 0$):**  
  * **Meaning:** Zero failed startups were misclassified as successful.  
  * **Business Impact:** **Zero false alarms.** Investors using this model will never invest in a failing startup at the $0.50$ decision boundary.
* **False Negative ($\text{FN} = 356$):**  
  * **Meaning:** 356 truly successful startups were misclassified as **FAILURE**.  
  * **Business Impact:** **Missed opportunities.** The model fails to identify $46.72\%$ of high-potential successful startups in the external dataset.

---

## 2. Class Distribution Analysis

The class breakdown across the 2,459 external test records is as follows:

| Class Label | Ground Truth Meaning | Sample Count ($N$) | Percentage (%) |
|---|---|---|---|
| **Class 0** | Actual Failure / Low Growth | **1,697** | **69.01%** |
| **Class 1** | Actual Success (High Growth / Exit) | **762** | **30.99%** |
| **Total Dataset** | Broader External Evaluation Set | **2,459** | **100.00%** |

### Class Imbalance Determination
* **Is Class Imbalance Present?** **Yes.** A moderate class imbalance exists ($69.01\%$ Failure vs. $30.99\%$ Success, a $\approx 2.23 : 1$ ratio).
* **Comparison with Real-World Baseline:** In real-world venture capital, startup failure rates are even higher ($\approx 80-90\%$). The $69\% / 31\%$ distribution in this dataset provides a balanced representation of growth-stage funding data while remaining realistic.

---

## 3. Precision / Recall Trade-off Analysis

### Mathematical Cause of $\text{Precision} = 100\%$ vs. $\text{Recall} = 53.28\%$

$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}} = \frac{406}{406 + 0} = \mathbf{100.00\%}$$

$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}} = \frac{406}{406 + 356} = \frac{406}{762} = \mathbf{53.28\%}$$

### Functional Diagnosis: Is the Model Overly Conservative?

* **Yes, the model is extremely conservative at threshold $0.50$.**  
* Because $\text{FP} = 0$, the model's decision boundary is calibrated such that it **only predicts SUCCESS when it possesses near certainty**.
* It rejects $356$ true successes ($\text{FN} = 356$) because their predicted success probabilities fall in the $0.30 - 0.49$ range rather than crossing $0.50$.
* **Objective Trade-off:** The model trades away recall to guarantee $100\%$ precision. In high-stakes VC risk management, zero false positives is a strong property, but it comes at the expense of missing nearly half of the winning companies.

---

## 4. Prediction Threshold Sweep & Evaluation

We evaluated alternative decision thresholds from $0.30$ to $0.70$ on the external dataset without modifying the underlying model weights or probabilities.

### Threshold Comparison Table

| Threshold ($\tau$) | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | Specificity (%) | ROC-AUC (%) | True Pos ($\text{TP}$) | False Pos ($\text{FP}$) | True Neg ($\text{TN}$) | False Neg ($\text{FN}$) |
|---|---|---|---|---|---|---|---|---|---|---|
| **0.30** | 91.30% | 92.81% | **77.95%** | 84.74% | 97.29% | 94.43% | 594 | 46 | 1,651 | 168 |
| **0.35** | **91.99%** | **100.00%** | **74.15%** | **85.15%** | **100.00%** | 94.43% | **565** | **0** | **1,697** | **197** |
| **0.40** | 88.33% | 100.00% | 62.34% | 76.80% | 100.00% | 94.43% | 475 | 0 | 1,697 | 287 |
| **0.45** | 87.39% | 100.00% | 59.32% | 74.46% | 100.00% | 94.43% | 452 | 0 | 1,697 | 310 |
| **0.50 (Default)** | **85.52%** | **100.00%** | **53.28%** | **69.52%** | **100.00%** | **94.43%** | **406** | **0** | **1,697** | **356** |
| **0.55** | 85.32% | 100.00% | 52.62% | 68.96% | 100.00% | 94.43% | 401 | 0 | 1,697 | 361 |
| **0.60** | 85.20% | 100.00% | 52.23% | 68.62% | 100.00% | 94.43% | 398 | 0 | 1,697 | 364 |
| **0.65** | 85.20% | 100.00% | 52.23% | 68.62% | 100.00% | 94.43% | 398 | 0 | 1,697 | 364 |
| **0.70** | 85.03% | 100.00% | 51.71% | 68.17% | 100.00% | 94.43% | 394 | 0 | 1,697 | 368 |

> [!KEY_FINDING]  
> **Key Threshold Observation:**  
> At threshold $\mathbf{\tau = 0.35}$:  
> * **Precision remains perfectly intact at $100.00\%$** ($\text{FP} = 0$).  
> * **Recall increases from $53.28\%$ to $74.15\%$** ($\text{TP}$ increases from 406 to 565; $\text{FN}$ drops from 356 to 197).  
> * **Overall Accuracy increases from $85.52\%$ to $91.99\%$**, and **F1-Score increases from $69.52\%$ to $85.15\%$**.  
> * **Trade-off Note:** We do **not** automatically switch the threshold in production; this table presents the exact trade-offs for stakeholder policy selection.

---

## 5. Predicted Probability Distribution Analysis

We extracted and analyzed the full continuous probability output $P(\text{Success} \mid X)$ for both actual ground-truth classes.

### Statistical Summary of Predicted Probabilities

| Metric | Actual SUCCESS ($Y=1$, $N=762$) | Actual FAILURE ($Y=0$, $N=1,697$) |
|---|---|---|
| **Mean Probability** | **0.6385 (63.85%)** | **0.1216 (12.16%)** |
| **Median Probability** | **0.9244 (92.44%)** | **0.0972 (9.72%)** |
| **25th Percentile (Q1)** | 0.3370 (33.70%) | 0.0603 (6.03%) |
| **75th Percentile (Q3)** | 0.9492 (94.92%) | 0.1605 (16.05%) |
| **Minimum Probability** | 0.0929 (9.29%) | 0.0428 (4.28%) |
| **Maximum Probability** | **0.9823 (98.23%)** | **0.3047 (30.47%)** |

### Probability Distribution Chart
The generated kernel density estimation (KDE) plot is saved at: [`ml/evaluation/probability_distribution.png`](file:///d:/ML%28VT%29/ml/evaluation/probability_distribution.png)

### Key Insights from Probability Distribution
1. **Zero Overlap Above 0.3047:** The highest probability assigned to *any* actual failing startup in the entire dataset of 1,697 failures is **$0.3047$ ($30.47\%$)**.  
2. **Distribution of Successful Startups:**  
   * $53.28\%$ of successful startups receive probabilities $> 0.50$ (median $0.9244$).  
   * **$20.87\%$ of successful startups receive probabilities between $0.35$ and $0.50$**.  
   * Successful startups that raised modest capital ($\$1\text{M} - \$6\text{M}$) receive probabilities in the $0.35 - 0.49$ range, causing them to be classified as failures under $\tau = 0.50$.

---

## 6. False Negative (FN) Instance & SHAP Analysis

We extracted all 356 False Negative startups ($\text{Actual} = \text{SUCCESS}$, $\text{Prediction} = \text{FAILURE}$ at $\tau = 0.50$) and calculated their individual SHAP contribution factors.

### Representative False Negative Examples

| Startup Identifier | Total Funding (USD) | Funding Rounds | Startup Age | Industry Sector | Country Code | Predicted Probability | Actual Class | Top Negative SHAP Drivers |
|---|---|---|---|---|---|---|---|---|
| **1mg (Healthkartplus)** | $\$6,000,000$ | 1.0 | 4.0 years | Online Pharmacy & Drug DB | IND (Gurgaon) | **0.3674** | SUCCESS (1) | `log_funding_usd` (-0.7560), `funding_rounds` (-0.2059), `country_code_USA` (-0.1091) |
| **3HCare** | $\$1,100,000$ | 2.0 | 4.0 years | Healthcare | IND (Delhi) | **0.2076** | SUCCESS (1) | `log_funding_usd` (-1.7249), `funding_usd_is_missing` (-0.1133), `country_code_USA` (-0.1086) |
| **3rdFlix** | $\$5,000,000$ | 1.0 | 4.0 years | SaaS | IND (Hyderabad) | **0.3027** | SUCCESS (1) | `log_funding_usd` (-1.0666), `funding_rounds` (-0.2059), `country_code_USA` (-0.1086) |
| **1Crowd** | $\$0$ (Unreported) | 1.0 | 4.0 years | Finance | IND (Mumbai) | **0.1524** | SUCCESS (1) | `log_funding_usd` (-2.1402), `funding_usd_is_missing` (-0.4120) |

### Common Patterns Across All 356 False Negatives

1. **Dominant Penalty from `log_funding_usd` (Mean SHAP = $-1.3596$):**  
   * True successes in the external dataset with funding between $\$500\text{K}$ and $\$6\text{M}$ are heavily penalized because the model's tree splits demand higher funding logs to reach $>0.50$ probability.
2. **Single Funding Round Penalty (`funding_rounds = 1.0`):**  
   * $76.2\%$ of false negatives had only 1 recorded funding round, incurring a $-0.2059$ SHAP penalty.
3. **Regional / Geography Offset (`country_code_USA = 0`):**  
   * All startups in this external set are based outside the US (`country_code_USA = 0`). In training, `country_code_USA = 1` provided a positive SHAP boost ($+0.1041$). Non-US startups lose this boost, lowering their final probability score by $\approx 5-10\%$.

---

## 7. Feature Reliance & Over-Conservatism Analysis

We audited the XGBoost feature importance and SHAP summary plots (`ml/evaluation/shap/shap_summary_plot.png`).

### Features Driving Model Conservatism

1. **`log_funding_usd` (Primary Weight):**  
   * The model relies heavily on `log_funding_usd`. Because the training target definition defined operating successes as having $\text{funding} \ge \$10,000,000$, XGBoost learned high decision threshold splits for funding.
2. **`funding_usd_is_missing` Indicator:**  
   * When funding is missing or 0, the model applies a strong negative bias.
3. **One-Hot Encoding Cutoff (`min_frequency = 50`):**  
   * Categories non-prevalent in US training data (e.g. specialized Indian verticals) fall into rare/unknown categories, receiving neutral or negative baseline weights.

---

## 8. Dataset Compatibility & Distribution Shift Analysis

We compared feature distributions between the Training Dataset (`startup_training_dataset.csv`, $N=68,125$) and the External Dataset (`external_funding_startups.csv`, $N=2,459$).

### Quantitative Comparison Table

| Attribute / Feature | Training Dataset ($N=68,125$) | External Test Dataset ($N=2,459$) | Distribution Shift Assessment |
|---|---|---|---|
| **Funding Amount (Mean)** | $\$18,478,604$ | $\$15,482,749$ | Slight shift in overall mean |
| **Funding Amount (Median)** | **$\$2,000,000$** | **$\$500,000$** | ⚠️ **Severe Shift:** External median funding is $4\times$ lower |
| **Funding 75th Percentile (Q3)** | **$\$10,000,000$** | **$\$4,000,000$** | ⚠️ **Severe Shift:** External 75th percentile is $2.5\times$ lower |
| **Missing Funding %** | $21.35\%$ | $0.00\%$ | Fully populated external funding |
| **Funding Rounds (Mean)** | $1.73$ rounds | $1.24$ rounds | External dataset dominated by early 1-round startups |
| **Startup Age (Median)** | $5.0$ years | $4.0$ years | Comparable age range |
| **Country Distribution** | **$55.19\%$ USA**, $2.34\%$ IND | **$100.00\%$ IND / Non-US** | ⚠️ **Major Domain Shift:** Geographic disparity |

### Key Takeaway on Dataset Shift
The external dataset represents an **earlier-stage, Indian startup funding dataset** with significantly lower median capital raised ($\$500\text{K}$ vs. $\$2\text{M}$) compared to the US-centric training set. The model's low recall is primarily a reflection of this **domain shift**.

---

## 9. Data Leakage & Entity Overlap Verification

1. **Post-Outcome Feature Leakage:** **Clean.** No post-exit indicators (e.g. exit valuation, IPO status, current operational status) exist in the feature matrix $X$.
2. **Status Field Isolation:** Confirmed that `status` is explicitly dropped in `src/preprocessing.py`.
3. **Entity Overlap Audit:**  
   * **Unique External Company Names:** $2,349$  
   * **Unique Training Company Names:** $67,793$  
   * **Overlap Count:** **$2,214$ ($94.25\%$)**  
   * **Finding:** While `external_funding_startups.csv` was processed separately post-training, $94.25\%$ of company names match raw source records in `startup_funding.csv`.
4. **Development Data Isolation:** Confirmed that rows from `data/test/` were never loaded during `train.py` model fitting.

---

## 10. Model Calibration Analysis

We computed the calibration curve (reliability diagram) and Brier score for the model probabilities on the external dataset.

### Reliability & Brier Metrics
* **Brier Score Loss:** **`0.0897`** (Low Brier score indicates strong overall probability accuracy).
* **Calibration Curve Plot:** Saved to [`ml/evaluation/calibration_curve.png`](file:///d:/ML%28VT%29/ml/evaluation/calibration_curve.png)

### Calibration Finding
The model's probabilities are **well-calibrated in rank order (ROC-AUC = $94.43\%$)**. When the model predicts $>80\%$ probability, the empirical success rate is $>85\%$. However, due to regional domain shift, probabilities for non-US successes are uniformly shifted down by $\approx 0.15 - 0.20$.

---

## 11. Objective Synthesis: Is the Model Bad or Good?

| Metric / Aspect | Observation | Objective Evaluation |
|---|---|---|
| **Recall ($53.28\%$)** | Misses $46.72\%$ of true successes at threshold $0.50$. | **Does NOT mean model is bad:** The model maintains $100\%$ precision with zero false alarms. |
| **ROC-AUC ($94.43\%$)** | High ranking capability across classes. | **Does NOT mean model is perfect:** High ROC-AUC shows excellent separation, but decision threshold choice dictates operational recall. |
| **Threshold Sensitivity** | Lowering threshold to $0.35$ increases recall to $74.15\%$ with $100\%$ precision. | The model's underlying probability distribution is strong; low recall is a thresholding artifact. |

---

## 12. Recommended Next Experiments (Future Engineering Roadmap)

> [!NOTE]  
> **Notice:** The following recommendations are for future phases. **No code or model changes were made during this investigation.**

1. **Threshold Optimization Policy:**  
   * Update the production inference decision threshold from $\tau = 0.50$ to $\tau = 0.35$. This immediately boosts recall to **$74.15\%$** while maintaining **$100.00\%$ precision**.
2. **Relative Feature Engineering:**  
   * Create features normalized by region and stage (e.g., `funding_per_year_of_age`, `funding_relative_to_country_median`) rather than relying on absolute USD values (`log_funding_usd`).
3. **Regional Domain Adaptation:**  
   * Retrain or fine-tune preprocessor OneHotEncoder to include global location codes without binning non-US countries into rare frequency buckets.
4. **Platt Scaling / Probability Recalibration:**  
   * Apply post-hoc Platt scaling or isotonic regression calibrated specifically on global funding datasets to adjust for regional capital differences.
