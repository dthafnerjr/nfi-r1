# NFI R1 — User Manual

**National Fracture Index, Release 1**

---

## Preface

### What This Manual Assumes About You

You are an analyst, researcher, investment professional, or policymaker
who wants to use the NFI R1 as an analytical instrument. You understand
that complex social systems resist precise prediction, and you are looking
for a structured probabilistic framework rather than a forecasting oracle.

You do not need to be a programmer to use the Streamlit interface.
You may be one if you want to work with the underlying Python code.

### A Critical Note Before You Begin

The NFI R1 produces **probability distributions over zones**, not predictions
of specific events. When the model shows P(τ > τ°) = 64% by 2030, this means:
across 10,000 simulated futures consistent with current conditions and the
model's assumptions, 64% of those futures involve τ crossing the Calvo
discontinuity zone by 2030. It does not mean a fiscal crisis will occur in 2030.

The appropriate question to ask of this model is:
*"Given current conditions, what range of futures is structurally plausible?"*
Not: *"When will X happen?"*

---

## PART I: GETTING STARTED

---

### Chapter 1: Installation and First Run

#### 1.1 Option A: Browser Access (Streamlit Cloud)

The simplest option. No installation of any kind.

1. Open the Streamlit deployment URL in any modern browser
2. The model loads automatically with default settings
3. You are ready to use all features immediately

If you do not have the deployment URL, contact your repository administrator.

#### 1.2 Option B: Google Colab (No Local Installation)

1. Navigate to the NFI R1 GitHub repository
2. Click the **Open in Colab** badge in the README
3. In Colab, click **Runtime → Run all**
4. Wait approximately 90 seconds for packages to install
5. The notebook version of the model is now running

The Colab version provides full analytical capability including sensitivity
analysis functions not exposed in the Streamlit interface.

#### 1.3 Option C: Local Installation

**Requirements:** Python 3.11+, ~500MB disk space, internet connection for first run.

```bash
# Clone the repository
git clone https://github.com/[username]/nfi-r1.git
cd nfi-r1

# Install dependencies
pip install -r requirements.txt

# Launch the application
streamlit run app.py
```

The application will open automatically in your default browser at
`http://localhost:8501`. If it does not, navigate there manually.

#### 1.4 Verifying Your Installation

When the application loads correctly, you will see:
- The header: "National Fracture Index R1"
- A current composite score of 70/100
- Six KPI metric cards across the top
- Five tabs: Overview, τ Dashboard, Projections, Scenarios, Methodology

If the composite score shows differently, your weight sliders may have been
modified. Click **Equal** in the sidebar to restore equal weighting.

#### 1.5 Running the Model for the First Time

1. The model loads with historical data displayed immediately — no button press needed
2. Navigate between tabs using the tab row at the top
3. To generate a forward projection, navigate to the **Projections** tab and
   press **Run simulations**
4. First run at 10,000 simulations takes approximately 15-30 seconds

---

### Chapter 2: Orientation — The Five Panels

#### 2.1 The Overview Tab
Historical NFI trends 1972-2024. All 11 dimensions plus composite.
Lorenz distribution curve. Radar dimensional profile.
*Purpose: understanding where the system currently is.*

#### 2.2 The τ Dashboard Tab
Fiscal stress history and market signal inputs.
Real-time Calvo proximity indicator.
*Purpose: monitoring the primary cascade trigger.*

#### 2.3 The Projections Tab
Monte Carlo forward simulation controls and output.
Percentile band projections 2024-2040.
Threshold crossing probabilities.
*Purpose: understanding where the system is likely going.*

#### 2.4 The Scenarios Tab
Side-by-side comparison of baseline, stress, and recovery scenarios.
Probability tables across time horizons.
*Purpose: understanding how structural changes alter the trajectory.*

#### 2.5 The Methodology Tab
Model overview, theoretical foundations, limitations.
*Purpose: understanding what the model is and is not.*

#### 2.6 Reading the Interface at a Glance

**Header composite score (top right):** Current 2024 NFI composite
under your current weight configuration. Updates live as you move sliders.

**Sidebar weight display:** Table showing current weight percentage for
each dimension. Always sums to 100%.

**Zone of Reduced Efficacy band:** The red-shaded region on trend charts
(NFI > 60). When the median projection line is in this band, the model
is projecting continued high-fracture conditions.

---

## PART II: CORE TASKS

---

### Chapter 3: Understanding the Current State

#### 3.1 Reading the Composite NFI Score

The composite NFI score summarizes the system state as a single 0-100 value.
Higher is worse. Interpret as follows:

| Score | Zone | Interpretation |
|---|---|---|
| 0–35 | Stable | Institutional response capacity intact |
| 35–55 | Elevated | Strained but functional |
| 55–68 | High Fracture | Cross-partisan coordination difficult |
| 68–100 | Reduced Efficacy | Democratic correction mechanisms impaired |

Current score (2024, equal weights): **70** — within the Zone of Reduced Efficacy.

Note: the composite score is weight-dependent. The Piketty weight preset
produces a different composite than the Fiscal preset. This is analytically
appropriate — the "right" composite depends on what you are analyzing.

#### 3.2 Reading Individual Dimension Scores

Each KPI card shows the dimension's current score and its change from the
1972 baseline. Key observations for 2024:

- **Legislative Polarization (86):** Near historical maximum. Primary driver
  of τ blockage.
- **Epistemic Fragmentation (79):** Central node in the Political Responsiveness
  feedback loop.
- **Household Economic Security (66):** Sharpest recent acceleration, driven
  by 2021-2023 inflation surge.
- **Fiscal Stress τ (36):** Lowest social-dimension score but rising fastest
  in absolute terms; only 0.102 raw τ units below the Calvo lower bound.

#### 3.3 The Lorenz Distribution Panel

The Lorenz curve shows how fracture is distributed across the 11 dimensions.

**How to read it:** If fracture were perfectly equal across all dimensions,
the curve would follow the diagonal. The further the curve bows below the
diagonal, the more concentrated fracture is in specific dimensions.

**The analytical story:** The concentration coefficient has declined from
1972 to 2024 (0.137 → 0.082 on equal weighting). This means fracture has
become more *pervasive* — distributed across all dimensions rather than
concentrated in one or two. Concentrated fracture is potentially addressable
(fix the specific problem). Pervasive fracture indicates a systemic condition.

#### 3.4 The Radar Profile

Seven-axis radar showing 2024 vs 1972 profile. The 2024 outline (amber)
is much larger than the 1972 baseline (blue dashed). The "notch" toward
the Fiscal τ axis shows this dimension is still materially lower than the
social dimensions — this is the gap that will close as τ rises.

#### 3.5 Worked Example: Interpreting the 2024 Baseline

*You have just opened the model for the first time. Equal weights are active.*

Observations:
- Composite: 70 (Zone of Reduced Efficacy)
- Legislative Polarization: 86 (near maximum; fiscal consolidation structurally blocked)
- Epistemic Fragmentation: 79 (high; Political Responsiveness feedback loop active)
- Household Economic Security: 66 (elevated; 2021-2023 inflation impact visible)
- Fiscal Stress τ: 36 (rising; only 44 normalized points from τ*)

Synthesis: The system is in the Zone of Reduced Efficacy across social
dimensions, with the fiscal dimension (τ) rising toward the Calvo zone.
The political system that would need to address τ is operating in a
high-fracture environment where the required cross-partisan coordination
is structurally unavailable.

---

### Chapter 4: Working with the τ Dashboard

#### 4.1 What τ Measures and Why It Matters

τ = Net Interest Payments / General Fund Revenue

This measures the fraction of government revenue consumed by debt service.
When τ approaches τ°, a self-fulfilling confidence crisis can fire:
each market participant rationally reduces Treasury exposure if they expect
others to do so, making the crisis self-fulfilling without requiring
fundamental insolvency.

Key thresholds:
- **τ* = 0.769:** Mathematical ceiling (all revenue consumed by interest)
- **τ° = 0.38–0.45:** Calvo discontinuity trigger zone
- **Current τ = 0.278:** 0.102 below the lower trigger bound

#### 4.2 Reading the τ Trend Chart

The bar chart shows annual τ values with color coding:
- **Teal:** Below 0.25 (low concern)
- **Amber:** 0.25–0.38 (elevated concern)
- **Red:** Above 0.38 (Calvo zone)

Note the V-shape: high in the 1980s-early 1990s (Reagan deficits + high rates),
low through the QE era 2000-2020, now rising sharply from the post-2022
rate normalization impact on debt rollover.

#### 4.3 The τ° and τ* Reference Lines

Two dashed horizontal lines on the τ chart:
- **Amber dashed:** τ° lower bound (0.380) — entry to Calvo zone
- **Amber dotted:** τ° upper bound (0.450) — high-confidence trigger zone
- **Red dashed:** τ* ceiling (0.769) — mathematical maximum

The current τ (0.278) is visibly below the amber lines.
The question the projection tab answers: how soon does the bar approach them?

#### 4.4 The Market Signal Indicators

The τ Dashboard includes a signal input panel on the right side.

**For default use:** Enter current market values manually:
- TLT current price (find on any financial data site)
- TLT price 90 days ago (same source, look back)
- TLT price 180 days ago
- VIX level (CBOE website or financial data site)
- VIX-TLT 90-day correlation (requires calculation — see §4.5)
- MOVE index (Bloomberg or ICE website)
- Term premium 10Y (FRBNY website)

**For automatic data:** Check the "Fetch live TLT/VIX data" box.
Requires internet connection. MOVE and term premium require manual entry
regardless (not available via free APIs).

#### 4.5 The VIX-TLT Correlation: The Critical Signal

The VIX-TLT rolling correlation is the most important market signal in the model.

**Normal condition (correlation negative, -0.2 to -0.6):**
When equity markets are stressed (VIX rises), Treasuries rally as safe haven
(TLT rises, yields fall). This is the standard portfolio hedging relationship.

**Warning signal (correlation near zero, -0.1 to +0.1):**
The safe-haven relationship is weakening. Both equities and Treasuries
are beginning to face selling pressure simultaneously.

**Critical signal (correlation positive, +0.1 to +0.5):**
Treasuries have lost safe-haven status for this stress episode. Both VIX
and TLT are rising (yields rising). This is the signature of a
Calvo-type discontinuity approaching. The UK gilt crisis of September 2022
showed this exact pattern before Bank of England emergency intervention.

**How to compute the 90-day VIX-TLT correlation:**
Most financial data platforms can compute this. Alternatively, export
both daily closing values to a spreadsheet and compute =CORREL() over
the trailing 90 rows.

#### 4.6 The Calvo Proximity Score

Composite 0-100 score from five signal components:
- TLT velocity (20% weight)
- TLT acceleration (25% weight) — the primary warning
- VIX-TLT correlation inversion (30% weight) — the critical signal
- MOVE + VIX dual elevation (15% weight)
- Term premium level (10% weight)

Interpretation:
- **0-25:** Low concern — normal market conditions
- **25-50:** Elevated — one or more signals showing stress
- **50-72:** Warning — multiple signals aligned; institutional monitoring warranted
- **72-100:** Critical — Calvo discontinuity structurally plausible

#### 4.7 Worked Example: Reading the Market Signal Panel During Rising Yields

*Scenario: TLT has declined from 95 to 87 over 180 days. VIX is at 22.
VIX-TLT correlation has moved from -0.35 to +0.08. MOVE is at 115.*

Enter in the manual panel:
- TLT current: 87
- TLT 90d ago: 91
- TLT 180d ago: 95
- VIX: 22
- VIX-TLT correlation: +0.08
- MOVE: 115
- Term premium: 0.55

Expected output: Calvo Proximity Score approximately 55-65, Warning level.

Key interpretation: The correlation at +0.08 is the most concerning signal —
Treasuries are no longer fully functioning as safe havens during equity stress.
This is worth monitoring but not yet critical.

---

### Chapter 5: Adjusting Dimension Weights

#### 5.1 What Weight Adjustment Means Analytically

Moving a weight slider changes the relative contribution of that dimension
to the composite NFI score. It does not change the underlying dimension
trajectories — only how they are combined.

Weight adjustment is how you ask: *"What does the model say if I believe
fiscal stress matters more than affective polarization?"* or
*"What if the Piketty capital concentration pathway is the primary driver?"*

#### 5.2 The Default Equal-Weighting Baseline

Equal weights (1/11 ≈ 9.1% each) is the analytical starting point.
It reflects no prior claim about relative importance — an agnostic position.

Use equal weights when:
- You want the baseline model output
- You are exploring sensitivity across weight configurations
- You have not formed a view on dimension relative importance

#### 5.3 Moving the Sliders

Sliders are in the left sidebar, labeled by short dimension name.
Range: 0-30 for each slider.

The sliders do not directly control percentage weights — they control
raw values that are then normalized to sum to 100%. This prevents the
composite from being undefined when all sliders are zero.

The weight distribution table at the bottom of the sidebar shows the
actual percentage weight each dimension is receiving.

#### 5.4 Weight Configuration Presets

Four preset buttons are available at the top of the sidebar:

**Equal:** Returns all sliders to default (1/11 ≈ 9.1% each)

**Piketty:** Emphasizes the capital concentration pathway.
Income Inequality (18%) and Institutional Capture (14%) receive
the highest weights, reflecting the r > g dynamic as the primary driver.
Use for: analysis emphasizing the political economy of capital.

**Fiscal τ:** τ-dominant configuration (25%).
Use for: sovereign credit analysis, investment positioning around
fiscal sustainability, bond market risk assessment.

**Social:** Social dimension emphasis. Affective Polarization (14%),
Institutional Trust (12%), Epistemic Fragmentation (12%), Cultural
Solidarity (12%), Political Responsiveness (12%).
Use for: democratic health analysis, political risk assessment.

#### 5.5 Saving a Custom Weight Configuration

The Streamlit interface does not currently save weight configurations between
sessions. To preserve a custom configuration:

1. Note the weight values from the sidebar distribution table
2. Record them in your analysis notes
3. On next session, manually recreate using the sliders

Weight configuration persistence is planned for R2.

#### 5.6 The Sensitivity Display

When you move sliders, the composite score in the header updates immediately.
This real-time feedback shows the sensitivity of the composite to weight changes.

High sensitivity (large composite change from small weight shift) indicates
that dimension is analytically powerful given current dimension scores.
Low sensitivity indicates the dimension is either low-scored or that other
dimensions dominate.

#### 5.7 Worked Example: Configuring Weights for a Sovereign Credit Analysis

*Purpose: Assessing US fiscal sustainability for long-duration bond positioning.*

Recommended configuration: Fiscal τ preset, with manual adjustment to
increase Household Economic Security slightly (reflects τ-to-HES feedback
relevance for domestic demand and revenue base).

1. Click **Fiscal τ** preset
2. Increase **HH Security** slider from its preset value (~10) to 13
3. Observe composite score change (will increase slightly)
4. Navigate to Projections tab
5. Note P(τ > τ°) at 5-year and 10-year horizons under this weighting
6. Run stress scenario to see outer bound of plausible τ trajectory

Expected finding: The Fiscal τ weighting produces a higher composite
score (worse) in earlier years (1980s-1990s when τ was elevated)
and a sharply rising recent period as both τ and HES deteriorate.

---

### Chapter 6: Running Monte Carlo Projections

#### 6.1 What the Monte Carlo Engine Is Doing

Each simulation run evolves all 11 dimensions from 2024 to the horizon year,
using:
- Historical trend drift rates (how fast each dimension has been moving)
- Cross-dimensional feedback effects (from the DBN structure)
- Normally distributed noise (calibrated from historical volatility)
- Calvo cascade shocks (probabilistic, based on τ proximity to τ°)

After 10,000 runs, the model has 10,000 distinct plausible futures.
It then shows you the distribution of those futures — not which one
will happen, but which range of outcomes is consistent with current
conditions and the model's assumptions.

#### 6.2 Choosing a Run Count

**1,000 runs:** Fast (~5 seconds). Suitable for quick exploration.
The median line is stable; percentile bands may show some noise.

**10,000 runs:** Standard (~15-30 seconds). Percentile bands are stable.
Calvo crossing probabilities are reliable. Recommended for analysis.

**50,000 runs:** Extended (~2-5 minutes). Tail distributions are stable.
Required for precise estimation of low-probability events (P < 5%).
Use when precise tail estimates matter.

#### 6.3 Selecting a Scenario

**Baseline:** Current trajectory extrapolated. No structural change.
The model assumes current trends in all 11 dimensions continue at their
recent rates. τ drift at current structural rate. No assumption about
policy intervention.

**Stress:** Fiscal deterioration accelerates. Bond market term premium
expands. τ rises faster than baseline. Social dimension deterioration
also accelerates. Represents: continued fiscal recklessness, rising
rates, no corrective policy action.

**Recovery:** Partial political responsiveness restoration.
τ drift slows significantly (τ_multiplier = 0.55). Social dimension
acceleration slows (drift_multiplier = 0.60). Represents: oligarchic
coalition fracture, sustainability-aware faction gaining influence,
some degree of fiscal stabilization. Does NOT assume a return to low-NFI
conditions — only a deceleration of deterioration.

#### 6.4 Reading the Probability Band Output

The projection chart shows:

**Dark shaded band (25th-75th percentile):**
The interquartile range — half of all simulated futures fall within this band.
This is your central case range.

**Light shaded band (10th-90th percentile):**
80% of simulated futures fall within this band.
Futures outside this band are plausible but represent the tails of the distribution.

**Median line (50th percentile):**
The middle of the distribution — half of simulated futures are above,
half below. This is NOT a prediction; it is the central tendency of
the distribution.

**Critical distinction:** The median is not the expected value for planning
purposes. In a system with Calvo cascade dynamics, the distribution is
skewed — many "mild deterioration" runs average against fewer but large
"cascade" runs. The 75th and 90th percentile lines are analytically
more important for risk management than the median.

#### 6.5 The τ Crossing Probability Display

Below the main projection chart, a row of metric cards shows:

P(τ > τ°) at 2026, 2028, 2030, 2032, 2035, 2040

These are direct estimates from the simulation:
the fraction of simulation runs in which τ exceeded the effective τ°
lower bound by that year.

**Color coding:**
- Green: below 25% — low concern
- Amber: 25-50% — elevated concern
- Red: above 50% — high concern; Calvo crossing more likely than not

**Important calibration note:** Under baseline conditions, the model shows
high P(τ > τ°) by 2030. This reflects the structural reality that:
τ = 0.278 requires only +0.102 to reach τ° = 0.380, and the structural
drift rate (~0.018/year) covers this distance in approximately 5.7 years.
The model is not alarmist; the arithmetic is. The recovery scenario
shows meaningful delay but not prevention within the decade.

#### 6.6 Zone of Reduced Efficacy Boundaries

The red-shaded region (NFI > 60) represents the Zone of Reduced Efficacy.
Key projections questions:
- Does any scenario show the median projection line dropping below the zone?
- What is the 10th percentile (best-case) trajectory?

Under current calibration, no scenario returns the median composite
below the Zone boundary within the projection horizon. The recovery
scenario slows entry into the deeper zone; it does not produce zone exit
within the 2040 horizon.

#### 6.7 Worked Example: Running a Stress Scenario

*Purpose: Assessing the outer bound of NFI deterioration under adverse conditions.*

1. Navigate to **Projections** tab
2. Set **Scenario** to "Stress — τ approaches τ° within cycle"
3. Set **Runs** to 10,000
4. Set **Horizon** to 2040
5. Press **Run simulations**
6. Observe: the 10th-90th band is wider than baseline (higher uncertainty)
7. Note P(τ > τ°) at 2028 — this is the near-term risk horizon

Under stress calibration, expect:
- Median composite: 90-95+ by 2040
- P(τ > τ°) by 2028: high (60-80%+)
- Calvo events in ~65-70% of runs by 2040

Analytical interpretation: The stress scenario represents the path
where no structural change occurs and fiscal trajectory continues
to deteriorate at its recent rate. The Calvo crossing probability
by 2028-2030 represents the primary risk horizon.

---

### Chapter 7: Scenario Comparison

#### 7.1 The Three Built-In Scenarios

See §6.3 for scenario descriptions. The comparison panel allows
side-by-side visualization of all three simultaneously.

#### 7.2 Reading the Comparison Panel

The composite projection chart overlays all three scenario median lines
with their 25-75th percentile bands. Key observations:

- The **divergence between scenarios** is widest in the near term (2026-2032)
  and converges at longer horizons. This is the model's most important
  practical finding: structural intervention in the near term has larger
  effects than the same intervention deferred.

- All three scenarios remain in the Zone of Reduced Efficacy. The scenarios
  differ in how deep into the Zone the system moves and how quickly τ
  approaches τ°, not in whether the Zone is occupied.

#### 7.3 The Probability Table

Below the comparison chart, a table shows P(τ > τ°) by scenario and year.
This is the most useful decision-relevant output for investment and
policy applications.

Example interpretation (approximate values):

| Year | Baseline | Stress | Recovery |
|---|---|---|---|
| 2028 | ~85% | ~95% | ~35% |
| 2030 | ~97% | ~99% | ~55% |
| 2035 | ~99% | ~100% | ~90% |

*The near-term window (2026-2030) is where recovery scenario differs most.*

#### 7.4 Worked Example: Comparing Scenarios for a 10-Year Investment Thesis

*Purpose: Evaluating long-duration Treasury exposure over a 10-year horizon.*

1. Navigate to **Scenarios** tab
2. Set horizon to 2035
3. Press **Run All Scenarios**
4. Read P(τ > τ°) table for 2030 and 2035

Baseline at 2030: high probability of τ > τ°
Recovery at 2030: meaningful reduction
Baseline at 2035: near certainty across all scenarios

Analytical conclusion: The 10-year horizon shows structural convergence
toward τ° crossing regardless of scenario. The investment implication
is not "will this happen" but "when" and "how severely." The recovery
scenario buys approximately 3-5 years of delay in the near term.

---

## PART III: ADVANCED USE

---

### Chapter 8: Sensitivity Analysis

#### 8.1 What Sensitivity Analysis Shows

Sensitivity analysis asks: does the model's conclusion change significantly
if I use different weight configurations? If P(τ > τ°) = 75% under equal
weighting but ranges from 40% to 90% across plausible weight configurations,
the conclusion is weight-sensitive. If it ranges from 70% to 82%, the
conclusion is robust.

Robust conclusions are more defensible. Sensitive conclusions require
explicit acknowledgment of the weight assumption driving them.

#### 8.2 Running Sensitivity Analysis

Sensitivity analysis requires the Python/Colab version.

```python
from monte_carlo import weight_sensitivity_analysis

results = weight_sensitivity_analysis(
    target_year=2035,
    n_weight_configs=500,
    n_runs_per_config=500,
)

# Results contain:
# results['calvo_probs']       — P(τ>τ°) for each weight config
# results['composite_medians'] — Median NFI for each config
# results['weights_matrix']    — The weight configurations tested
```

#### 8.3 Identifying Robust vs. Sensitive Conclusions

High correlation between a dimension's weight and the outcome = that
dimension is driving the conclusion. Low correlation = robust to that
dimension's weighting.

#### 8.4 The Overfitting Warning

Do not adjust weights to produce a desired backtesting result and then
use those weights for forward projection. This is overfitting.
Weight configurations should be justified by theoretical reasoning
(why would this dimension matter more?) not by historical curve-fitting.

---

### Chapter 9: Exporting Results

#### 9.1 Generating a Standalone HTML Snapshot

From the Python environment:

```python
# Generate a standalone HTML snapshot of the current model state
# (requires plotly installed)
# This creates a file you can share via email or web

# First run your desired Monte Carlo configuration via the app,
# then use the plotly figure objects:
import plotly.io as pio
pio.write_html(fig, "nfi_r1_snapshot_YYYYMM.html",
               include_plotlyjs=True, full_html=True)
```

The resulting HTML file (~5-8MB) opens in any browser without internet.

#### 9.2 Exporting Data to CSV

```python
from nfi_model import load_historical_data
df = load_historical_data()
df.to_csv("nfi_historical_export.csv", index=False)
```

For Monte Carlo results:

```python
import pandas as pd
from monte_carlo import run_monte_carlo

results = run_monte_carlo(n_runs=10000)
# Export percentile envelopes
pct_df = pd.DataFrame(
    results.composite_pct.T,
    columns=["p10", "p25", "p50", "p75", "p90"],
    index=results.years,
)
pct_df.to_csv("nfi_projections_baseline.csv")
```

#### 9.3 Citing NFI R1

```
National Fracture Index R1 (2026).
An analytical instrument for US social cohesion and fiscal sustainability.
11-dimension Dynamic Bayesian Network with Monte Carlo simulation.
Theoretical foundations: Rodgers (2011), Acemoglu & Robinson (2012),
Piketty (2014), Becker (1973), Club of Rome (1972), Turchin (2016).
[Repository URL]
```

---

### Chapter 10: Updating the Data

#### 10.1 Updating Historical Dimension Data

Edit `data/historical_dimensions.csv` to add new data points
(e.g., the 2028 observation when it becomes available).
Each row corresponds to one 4-year interval observation.
All values must be 0-100 normalized.

#### 10.2 Updating τ

Edit `data/tau_historical.csv`.
τ_raw = net interest outlays (OMB Table 3.2) / general fund revenue (CBO).
τ_normalized = (τ_raw / 0.769) × 100.

#### 10.3 Rerunning After Updates

After data updates, restart the Streamlit app:

```bash
# Stop current instance (Ctrl+C)
streamlit run app.py
```

The updated data loads automatically on restart.

---

## PART IV: REFERENCE

---

### Chapter 11: Dimension Reference

**Affective Polarization**
*What it measures:* Emotional hostility between partisan groups.
*Score of 70 (2024):* High hostility. Identity-protective cognition dominant.
*Trend:* Accelerating. 14→70 from 1972 to 2024. Steepening post-2012.

**Institutional Trust Deficit**
*What it measures:* Inverted institutional confidence (Gallup).
*Score of 71 (2024):* Low confidence across federal and civic institutions.
*Trend:* Persistent rise with temporary reversals during stable periods.

**Income Inequality**
*What it measures:* Top 1%/0.1% wealth concentration (Piketty-enhanced).
*Score of 66 (2024):* High concentration approaching Gilded Age levels.
*Trend:* Steady rise since 1975 resumption of r > g dynamics.

**Legislative Polarization**
*What it measures:* DW-NOMINATE distance between party medians.
*Score of 86 (2024):* Near-maximum historical levels.
*Trend:* Consistent acceleration. Primary τ blockage mechanism.

**Epistemic Fragmentation**
*What it measures:* Population segregation into divergent information ecosystems.
*Score of 79 (2024):* Deep media silos. Partisan media ecosystem well-established.
*Trend:* Accelerating. Structural break post-Citizens United (partisan media funding).

**Elite Misalignment**
*What it measures:* Social/experiential separation between elites and population.
*Score of 72 (2024):* Significant geographic and institutional divergence.
*Trend:* Steady rise; slower than Political dimensions.

**Fiscal Stress τ**
*What it measures:* Net interest / general fund revenue.
*Score of 36 (2024):* Raw τ = 0.278; 0.102 below Calvo lower bound.
*Trend:* V-shaped: high 1980s, low QE era, rising sharply since 2022.

**Political Responsiveness** *(New)*
*What it measures:* Electoral accountability mechanism functionality.
*Score of 78 (2024):* Safe seats dominant; primary extremism structurally entrenched.
*Trend:* Accelerating. Structural break at Citizens United (2010).

**Institutional Capture** *(New)*
*What it measures:* Active employment of concentrated power to reshape institutions.
*Score of 74 (2024):* Record lobbying levels; revolving door prevalent.
*Trend:* Accelerating. K-Street expansion 1990s-2000s; Citizens United amplifier.

**Cultural Solidarity** *(New)*
*What it measures:* Shared civic frameworks and cross-class social bonds.
*Score of 72 (2024):* Union membership ~10%; civic participation substantially reduced.
*Trend:* Steady rise (dissolution). Rodgers Age of Fracture origin ~1974 visible.

**Household Economic Security** *(New)*
*What it measures:* Material adequacy relative to survival costs.
*Score of 66 (2024):* Sharp recent acceleration from inflation surge.
*Trend:* Steepening. Housing 6x+ median income. Real wages lag necessity inflation.

---

### Chapter 12: The τ Function Reference

**Formula:** τ = Net Interest Payments / General Fund Revenue

**General Fund Revenue** = Total Federal Receipts - Payroll Tax Receipts
(Social Security and Medicare trust fund contributions excluded as
dedicated to specific obligations, not general fiscal response)

**τ* = 0.769** — Mathematical ceiling = 1 - (Primary Deficit / T)
Derived from 2024 OMB baseline. Represents point where interest consumes
all general fund revenue.

**τ° = 0.38–0.45** — Calvo discontinuity trigger zone
Estimated from Morris-Shin coordination game model.
Dynamic: effective τ° = τ°_base - 0.06 × max(0, (NFI_social - 50) / 50)

**Current (2024):** τ = 0.278 / normalized = 36/100

**VIX-TLT Correlation Signal:** See Chapter 4.5
Primary real-time Calvo proximity indicator.
Transition from negative to positive is the critical warning.

---

### Chapter 13: Glossary

**Affective polarization:** Emotional hostility between groups, distinct
from policy disagreement.

**Calvo trigger / Calvo discontinuity:** The τ threshold at which a
self-fulfilling confidence crisis becomes structurally plausible. Named
for economist Guillermo Calvo's work on currency crises; applied here
to sovereign debt markets via Morris-Shin coordination game model.

**Conditional probability table (CPT):** In a Bayesian network, the table
specifying the probability distribution of a node's value given each
possible combination of its parent nodes' values.

**Dynamic Bayesian Network (DBN):** A Bayesian network extended across
time steps, allowing feedback loops to be modeled as time-lagged dependencies
rather than simultaneous cycles.

**Epistemic fragmentation:** The condition in which population segments
occupy non-overlapping information ecosystems, preventing shared factual grounding.

**General fund revenue:** Federal revenue available for general government
purposes — total receipts minus dedicated payroll tax collections.

**Immortality project:** Becker's term for cultural/ideological systems
that provide symbolic transcendence of individual mortality. When political
identity fuses with an immortality project, policy outcomes become secondary
to symbolic identity maintenance.

**Monte Carlo simulation:** A computational method that generates many
random samples from probability distributions to estimate the distribution
of outcomes in complex systems.

**NFI storm:** The NFI cascade event when τ crosses τ° — simultaneous
deterioration across social dimensions from fiscal crisis consequences.

**Plateau capitalism:** The structural condition in which mature economies
face persistently low growth rates, making r > g dynamics explicitly zero-sum
rather than distributional.

**Term premium:** The additional yield investors demand for holding
long-duration bonds over rolling short-term instruments, reflecting
duration and fiscal risk rather than rate expectations.

**τ (tau):** The NFI fiscal stress function. Net interest / general fund revenue.

**τ° (tau-circle):** The Calvo discontinuity trigger — the τ level at which
a confidence crisis becomes self-fulfilling.

**τ* (tau-star):** The mathematical ceiling for τ — the level at which all
general fund revenue is consumed by interest payments.

**Zone of Reduced Efficacy:** The NFI zone (composite > ~60) in which
institutional response capacity is structurally impaired. The model's
primary forecasting output is the probability of system trajectory
within vs. outside this zone.

---

### Chapter 14: Troubleshooting

**"The model won't start (local installation)"**
Verify Python 3.11+: `python3 --version`
Verify all packages: `pip install -r requirements.txt`
Try: `streamlit run app.py --server.port 8502` if port 8501 is in use

**"Monte Carlo is very slow"**
For 10,000 runs on older hardware, expect 30-60 seconds.
Use 1,000 runs for exploration; 10,000 for final analysis.
Streamlit Cloud free tier may take 30-90 seconds for 10,000 runs.

**"The live market data isn't loading"**
yfinance may be rate-limited. Try again after 60 seconds.
Use the Manual Entry fields as a reliable fallback.
MOVE index and term premium always require manual entry.

**"My weight configuration produces a very different composite"**
This is expected and analytically appropriate. Different weight
configurations are different analytical questions. Use the sensitivity
analysis (Chapter 8) to determine if your conclusion is weight-robust.

**"The P(τ > τ°) looks very high — is the model too pessimistic?"**
The high probability reflects the structural arithmetic: τ = 0.278 is
only 0.102 below the Calvo lower bound, and the structural drift rate
covers this distance in approximately 5-6 years. The model is reflecting
the actual proximity of current τ to the trigger zone. The recovery
scenario shows meaningful but not unlimited delay.

---

### Chapter 15: Frequently Asked Questions

**Q: Why doesn't the model tell me exactly when the crisis will happen?**

A: Because no honest model of complex social systems can.
The NFI follows the Club of Rome's forecasting philosophy: predict
the shape of the trajectory and zone boundaries, not specific events
or dates. The timing of a Calvo discontinuity depends on thousands
of contingent factors the model cannot observe. What the model can say
is: given current structural conditions, the probability of τ entering
the Calvo zone within a given time horizon is X%. That is the epistemically
honest output. Point predictions would be false precision.

**Q: The recovery scenario still shows high τ crossing probability by 2035.
Does that mean recovery is pointless?**

A: No — it means the near-term window matters most. The recovery scenario
materially reduces P(τ > τ°) in the 2026-2030 window, which is when
structural intervention has the largest effect. By 2035, the scenarios
converge because even reduced drift rates cannot indefinitely prevent
crossing when the starting point is already 0.278 and τ* = 0.769.
Recovery is meaningful; it buys time for structural changes in the
political system (generational succession, oligarchic coalition fracture)
that might create conditions for genuine fiscal consolidation.

**Q: How often should I update the data?**

A: The historical series updates every four years with new data points.
The τ series should be updated annually when OMB fiscal year data is
published (October/November). Market signal inputs update continuously
as you choose. The model architecture will not become stale between
4-year data intervals — but the τ raw value should be updated annually.

**Q: Can I add a new dimension?**

A: Yes, in the Python/Colab version. Add a row to `DIMENSIONS` list
in `nfi_model.py`, add the historical data column to `historical_dimensions.csv`,
add a drift rate and sigma to `ANNUAL_DRIFT` and `ANNUAL_SIGMA` in
`monte_carlo.py`, and add relevant feedback edges to `bayesian_network.py`.
The composite and all charts update automatically.

**Q: How do I know if my weight configuration is analytically defensible?**

A: Two tests. First, is there a theoretical reason why this dimension
should receive this weight? Weight choices should be justified by your
analytical framework, not by which weights produce the output you want.
Second, run sensitivity analysis — if your conclusion only holds under
your specific weight configuration and collapses under nearby alternatives,
it is weight-sensitive and requires explicit acknowledgment of that dependence.

---

### Chapter 16: Frequently Asked Questions (Advanced)

**Q: The model treats Citizens United as a structural break. How is this
implemented?**

A: In `monte_carlo.py`, drift rates and feedback multipliers for
Political Responsiveness and Institutional Capture reflect the post-2010
acceleration. In `bayesian_network.py`, the structural break is documented
in `STRUCTURAL_BREAKS` with the estimated CPT parameter changes.
For R2, time-varying CPT estimation will explicitly model the parameter
shift at t=2012 (the next available 4-year data point after 2010).

**Q: What is the "Becker-Bonhoeffer condition" the model references?**

A: When political identity fuses with an immortality project (Becker),
the person becomes resistant to policy argument, evidence, or outcome-based
reasoning (Bonhoeffer's sociological stupidity condition). The model
operationalizes this as a floor on the Political Responsiveness dimension —
a level below which PR cannot recover within normal political timeframes
absent structural forcing events. Estimated at ~40% of electorate in
the US currently, creating a durable minimum fracture level that persists
for approximately one political generation (25-35 years).

**Q: Why does the model separate Elite Misalignment from Institutional Capture?**

A: They measure different things. Elite Misalignment measures the condition —
the degree of social separation between elites and the general population.
This is a structural condition that develops over decades (geographic sorting,
diverging institutional ecosystems). Institutional Capture measures the action —
the active employment of that positional advantage to reshape institutions
in extractive directions. The two are related (Misalignment enables Capture
by reducing the social friction that might check it) but can diverge.
High Misalignment with low Capture describes an isolated but not yet
weaponized elite class. The distinction matters analytically for
understanding where in the Acemoglu & Robinson vicious circle the
system currently sits.

---

*End of User Manual — National Fracture Index R1*

*Analytical instrument only — not a validated predictive model.*
*For research and analytical purposes.*
