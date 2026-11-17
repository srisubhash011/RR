# PRESSUREIQ
## Context-Aware Cricket Pressure & Player Reliability Analytics Engine
### Official Submission for SupeRR Selector Season 2 – Round 1

---

## 1. Executive Summary

Conventional cricket statistics such as raw batting averages, strike rates, economy rates, and wicket tallies fail to distinguish between runs scored in low-leverage blowouts and high-stakes match crises.

**PRESSUREIQ** is an end-to-end, scientifically defensible sports analytics engine that answers the central competition question:
> **Which batters and bowlers maintain or improve their performance when facing difficult match situations, compared with their expected performance under normal circumstances?**

Using historical IPL and T20 International delivery-level data from 2022 to 2026 (193,988 deliveries across 837 matches), PRESSUREIQ introduces a **Context-Aware Pressure Engine** that quantifies situational leverage strictly *before* each ball is bowled, decouples bowling pressure from batting pressure, establishes leak-free 5-fold match-grouped expectation baselines, and generates reproducible top-10 rankings backed by 90% bootstrap confidence intervals.

---

## 2. Official Top 10 Submission Rankings

### Output A: Top 10 Batters Under Pressure

| Rank | Player Name | Player ID | Final Rating | Pressure SR | Normal SR | Δ SR | Pressure Balls | Runs | 90% Bootstrap CI |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Naman Dhir** | 37052 | **93.25** | 185.4 | 157.0 | +28.3 | 260 | 482 | [90.62, 94.36] |
| **2** | **Ashutosh Sharma** | 8101 | **82.22** | 173.9 | 142.0 | +32.0 | 284 | 494 | [78.45, 84.78] |
| **3** | **Jason Holder** | 2633 | **79.72** | 162.7 | 136.3 | +26.4 | 365 | 594 | [77.66, 80.11] |
| **4** | **Babar Azam** | 2485 | **78.39** | 167.9 | 130.1 | +37.8 | 109 | 183 | [76.43, 80.41] |
| **5** | **Tim David** | 6396 | **77.51** | 167.0 | 187.8 | -20.8 | 661 | 1,104 | [76.02, 78.38] |
| **6** | **Donovan Ferreira** | 8182 | **76.11** | 159.4 | 167.3 | -7.9 | 234 | 373 | [74.05, 77.62] |
| **7** | **Rashid Khan** | 4722 | **75.80** | 164.2 | 146.9 | +17.3 | 363 | 596 | [74.31, 76.80] |
| **8** | **Andre Russell** | 1318 | **75.07** | 161.1 | 186.7 | -25.6 | 496 | 799 | [72.95, 76.19] |
| **9** | **Yasir Ali Chowdhury** | 5839 | **74.64** | 160.8 | 132.8 | +28.0 | 79 | 127 | [71.63, 77.85] |
| **10** | **Dwaine Pretorius** | 2334 | **74.52** | 155.6 | 138.5 | +17.1 | 180 | 280 | [72.21, 76.07] |

---

### Output B: Top 10 Bowlers Under Pressure

| Rank | Bowler Name | Player ID | Final Rating | Pressure Econ | Normal Econ | Δ Econ | Pressure Balls | Wickets | 90% Bootstrap CI |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Matheesha Pathirana** | 8661 | **85.70** | 7.97 | 8.24 | +0.27 | 980 | 61 | [81.23, 87.48] |
| **2** | **Mark Wood** | 2985 | **82.33** | 8.05 | 7.88 | -0.17 | 240 | 20 | [75.07, 89.51] |
| **3** | **Jasprit Bumrah** | 2933 | **79.59** | 6.90 | 6.92 | +0.02 | 1,475 | 68 | [75.24, 81.68] |
| **4** | **Liam Dawson** | 722 | **78.73** | 7.35 | 8.01 | +0.66 | 321 | 12 | [73.81, 81.97] |
| **5** | **Lungi Ngidi** | 4641 | **77.77** | 8.44 | 8.78 | +0.34 | 713 | 42 | [72.79, 80.54] |
| **6** | **Harry Tector** | 4812 | **77.67** | 6.38 | 7.25 | +0.87 | 173 | 10 | [73.57, 79.91] |
| **7** | **Logan van Beek** | 3772 | **76.95** | 8.41 | 8.16 | -0.25 | 374 | 29 | [63.49, 89.04] |
| **8** | **Varun Chakravarthy** | 6256 | **76.88** | 7.42 | 7.38 | -0.04 | 1,696 | 84 | [73.28, 78.41] |
| **9** | **Haider Ali** | 28756 | **76.69** | 6.00 | 6.36 | +0.36 | 224 | 13 | [69.10, 82.52] |
| **10** | **Abbas Afridi** | 7699 | **76.71** | 8.88 | 8.35 | -0.53 | 362 | 26 | [71.29, 79.53] |

---

## 3. Core System Innovations

### 3.1 Pre-Delivery State Reconstruction & Anti-Leakage Guarantee
- Every delivery feature represents the situation **immediately before** that ball was bowled.
- Score, wickets lost, balls bowled, and partnership runs are strictly lagged by 1.
- Rolling metrics across the preceding 12 and 18 legal balls use exact temporal pointer lookups (`np.searchsorted`) without lookahead.

### 3.2 Six Modeled Pressure Scenarios
1. **Scenario A (Batting Collapse):** Rapid fall of wickets (`w12`, `w18`), top-order resource depletion, and par-score deficit in Innings 1.
2. **Scenario B (Run Chase Steepness):** Required run rate (RRR), $RRR - CRR$ differential, and dwindling ball resources in Innings 2.
3. **Scenario C (Lower-Order Survival):** Batting position ≥ 7 or ≥ 6 wickets down while defending against innings termination.
4. **Scenario D (Aggressive Opposition Bowling Pressure):** Facing rampant opposition scoring at 10–14+ RPO with set partnerships.
5. **Scenario E (Defensive Bowling Leverage):** Defending close target margins in Innings 2 death overs.
6. **Scenario F (Momentum Shifts):** Dot-ball clustering (3+ consecutive dots) and acute scoring deceleration.

### 3.3 Leak-Free Expected Performance Models (5-Fold GroupKFold)
- Expected outcomes are modeled using LightGBM gradient boosted decision trees.
- Validated via 5-Fold GroupKFold strictly on `match_id` (zero intra-match leakage).
- Predicts expected runs per ball, boundary probability, dot ball probability, dismissal probability, and bowler wicket probability without player identity bias.

### 3.4 Five Orthogonal Reliability Dimensions
- **Dimension 1: Pressure Impact Score (35%)** — Expected impact per ball with Bayesian shrinkage blended with cumulative volume.
- **Dimension 2: Pressure Resilience Score (25%)** — Maintenance/improvement over empirical Bayes-shrunk normal baselines ($\Delta SR$ for batters, $\Delta Econ$ for bowlers).
- **Dimension 3: Match Consistency Score (15%)** — Inverse variance of match-level performance.
- **Dimension 4: Sample Confidence Score (15%)** — Logarithmic scaling of pressure ball exposure.
- **Dimension 5: Scenario Specialty Score (10%)** — Collapse resistance for batters; aggression resistance for bowlers.

---

## 4. Repository Structure

```text
PRESSUREIQ/
├── data/
│   ├── ball_by_ball.csv
│   ├── matches.csv
│   ├── competitions.csv
│   ├── teams.csv
│   ├── playing_eleven.csv
│   └── competition_team_player_mapping.csv
├── config/
│   ├── methodology.yaml
│   └── competition_filters.yaml
├── src/
│   ├── data/
│   │   ├── loader.py
│   │   ├── validation.py
│   │   └── delivery_state.py
│   ├── pressure/
│   │   ├── par_model.py
│   │   └── pressure_scoring.py
│   ├── models/
│   │   └── expected_models.py
│   ├── performance/
│   │   └── player_metrics.py
│   ├── ranking/
│   │   ├── ranking_engine.py
│   │   └── sensitivity.py
│   └── reporting/
│       ├── charts.py
│       └── report_generator.py
├── dashboard/
│   ├── app.py
│   └── pages/
├── outputs/
│   ├── rankings/
│   │   ├── top_10_batters.csv
│   │   ├── top_10_bowlers.csv
│   │   ├── all_batters_ranked.csv
│   │   ├── all_bowlers_ranked.csv
│   │   └── ranking_confidence.csv
│   ├── analytical/
│   │   ├── delivery_pressure_features.parquet
│   │   ├── delivery_pressure_features.csv
│   │   ├── batting_performance.csv
│   │   ├── bowling_performance.csv
│   │   ├── player_baselines.csv
│   │   └── player_scenario_analysis.csv
│   ├── audit/
│   │   ├── data_quality_report.csv
│   │   ├── competition_audit.csv
│   │   ├── missing_matches_audit.csv
│   │   ├── model_evaluation_metrics.csv
│   │   └── sensitivity_analysis.csv
│   ├── charts/
│   └── reports/
│       └── PRESSUREIQ_Methodology_Report.pdf
├── tests/
│   ├── test_delivery_accounting.py
│   ├── test_pressure_features.py
│   ├── test_batting_metrics.py
│   ├── test_bowling_metrics.py
│   └── test_ranking.py
├── run_pipeline.py
├── requirements.txt
└── README.md
```

---

## 5. Execution and Reproduction

### 1. Run the Full Analytical Pipeline
To execute the complete end-to-end pipeline (data audit, state reconstruction, GBDT modeling, player scoring, bootstrap CIs, charts, and PDF report):
```bash
python run_pipeline.py
```
*Total execution time: ~42 seconds.*

### 2. Launch the Web Dashboard & Deploy to Vercel

#### A. Run Locally
To preview the interactive web dashboard locally:
```bash
cd web
npm run dev
```
Or view the production build:
```bash
cd web
npm run preview
```

#### B. Deploy to Vercel (Instant Live Link)
The dashboard is fully pre-configured for **1-click Vercel deployment** with `vercel.json`:
1. Run in your terminal:
   ```bash
   npx vercel
   ```
2. Log in with your GitHub/Vercel account and hit Enter.
3. Vercel will instantly build and output your production link (e.g., `https://pressureiq-dashboard.vercel.app`).

*Alternatively, push this repository to GitHub, link it on [vercel.com/new](https://vercel.com/new), and it will automatically deploy with continuous CI/CD updates!*

#### C. Launch Streamlit Alternative Dashboard
```bash
streamlit run dashboard/app.py
```

### 3. Run the Unit Test Suite
To verify statistical accounting, anti-leakage guarantees, and ranking constraints:
```bash
python -m unittest discover tests
```
*18 unit tests executed in < 0.1s — 100% PASS.*

---

## 6. Official Competition Deliverables

1. **Top 10 Player Rankings:** Exported in `outputs/rankings/top_10_batters.csv` and `outputs/rankings/top_10_bowlers.csv`.
2. **Methodology Report PDF:** Available in `outputs/reports/PRESSUREIQ_Methodology_Report.pdf` (13 pages, comprehensive documentation, actual analytical results, embedded high-resolution figures).
3. **Interactive Dashboard:** Accessible via `dashboard/app.py`.

