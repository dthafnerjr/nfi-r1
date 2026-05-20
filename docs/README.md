# National Fracture Index — R1

**A probabilistic analytical instrument for US social cohesion,
institutional integrity, and fiscal sustainability.**

---

## What It Is

The NFI R1 models the interaction of eleven social, political, and fiscal
dimensions as a Dynamic Bayesian Network with Monte Carlo simulation.
It produces **Zone of Reduced Efficacy** projections — probability
distributions over plausible system trajectories, not point predictions.

The model is grounded in the analytical frameworks of Rodgers (Age of Fracture),
Acemoglu & Robinson (Why Nations Fail), Piketty (Capital in the 21st Century),
Becker (Denial of Death), Bonhoeffer (sociological stupidity), the Club of Rome
(Limits to Growth), and Turchin (structural-demographic theory).

---

## What It Is NOT

- **Not a validated predictive model.** No independent external validation
  against out-of-sample data has been performed.
- **Not a forecast of specific events.** The model produces probability
  distributions over zones, not predictions of dates or events.
- **Not a substitute for domain expertise.** Each dimension represents a complex
  research literature; the composite is a structured synthesis, not a
  definitive measurement.
- **Not politically partisan.** The model measures structural dynamics.
  Its findings apply regardless of which party holds power.

---

## Key Capabilities

| Capability | Description |
|---|---|
| Historical visualization | 11 dimensions, 1972–2024, 4-year intervals |
| τ Dashboard | Real-time fiscal stress with market signal overlay |
| Monte Carlo projections | 10,000–50,000 runs, percentile envelopes |
| Adjustable weights | Sensitivity analysis across weight configurations |
| Scenario comparison | Baseline, stress, recovery trajectories |
| Calvo proximity | Live P(τ > τ°) with VIX-TLT correlation indicator |

---

## The 11 Dimensions

| # | Dimension | Type |
|---|---|---|
| 1 | Affective Polarization | Existing |
| 2 | Institutional Trust Deficit | Existing |
| 3 | Income Inequality (Piketty-enhanced) | Enhanced |
| 4 | Legislative Polarization | Existing |
| 5 | Epistemic Fragmentation | Existing |
| 6 | Elite Misalignment | Existing |
| 7 | Fiscal Stress τ | Existing |
| 8 | Political Responsiveness | New |
| 9 | Institutional Capture | New |
| 10 | Cultural Solidarity | New |
| 11 | Household Economic Security | New |

---

## Quick Start

### Option A — Browser (Streamlit Cloud)
Navigate to the deployment URL. No installation required.

### Option B — Google Colab
Click the badge in the repository README to open in Google Colab.
Run all cells. No local installation required.

### Option C — Local
```bash
git clone https://github.com/[username]/nfi-r1.git
cd nfi-r1
pip install -r requirements.txt
streamlit run app.py
```

---

## System Requirements

- Python 3.11+
- 4 GB RAM minimum (8 GB recommended for 50,000 MC runs)
- Modern browser (Chrome, Firefox, Safari, Edge)
- Internet connection for live market data (optional; manual entry available)

---

## The τ Finding

The model's primary analytical output: under all scenarios tested,
τ (net interest / general fund revenue) approaches the Calvo discontinuity
zone (τ° ≈ 0.38–0.45) within this decade under current trajectory.
P(τ > τ°) by 2030 ranges from 42% (recovery scenario) to >99% (baseline).
The near-term window (2026–2032) is where scenarios most meaningfully diverge.

---

## Citation

```
National Fracture Index R1 (2026).
Probabilistic analytical instrument for US social and fiscal cohesion.
https://github.com/[username]/nfi-r1
```

---

## License

Research and analytical use. Not for commercial redistribution without permission.
