# NFI R1 — Data Provenance & Estimation Notes

## Historical Series 1972–2024

All 14 observations (4-year intervals) represent research-based estimates
normalized to the 0–100 scale. Sources documented in METHODOLOGY.md §3.
The normalization methodology and source references are included there.

---

## R1.1 Addition: 2025 and 2026 YTD Estimates

Added August 2026. These two rows extend the historical series beyond the
original 4-year interval structure. They should be treated as **preliminary
estimates** pending full source data availability.

### 2025 Data Point

| Dimension | Value | Basis |
|---|---|---|
| Affective Polarization | 72 | Trend extrapolation from 2024 Pew data; no reversal observed |
| Trust Deficit | 73 | Trend extrapolation from 2024 Gallup confidence series |
| Income Inequality | 67 | Trend extrapolation; Saez-Zucman wealth share data typically lagged 1–2 yrs |
| Legislative Polarization | 87 | 119th Congress DW-NOMINATE median distance, estimated from early session data |
| Epistemic Fragmentation | 81 | Trend extrapolation; Reuters Digital News Report 2025 |
| Elite Misalignment | 73 | Trend extrapolation from Turchin structural-demographic series |
| Fiscal Stress τ | 37 (τ=0.282) | **Actual**: FY2025 net interest = $970B (Treasury/CRFB confirmed); general fund revenue ≈ $3,440B |
| Political Responsiveness | 80 | Trend extrapolation; 119th Congress competitive seat data |
| Institutional Capture | 76 | Trend extrapolation; OpenSecrets 2025 lobbying data |
| Cultural Solidarity | 73 | Trend extrapolation; BLS union membership 2024 ≈ 10.0% |
| Household Economic Security | 67 | Trend extrapolation; housing costs, food security, real wages through 2025 |

**τ 2025 sources:**
- Net interest: $970B (CRFB, Dec 2025, citing Treasury/CBO FY2025 final)
- CBO also noted gross debt interest surpassed $1T for first time
- General fund revenue: derived from total receipts ($5,243B implied at 18.5% share) minus payroll taxes (~$1,800B estimated)
- τ = 0.282 (slight increase from 0.278 in FY2024)

### 2026 YTD Estimate (as of Aug 2026)

| Dimension | Value | Basis |
|---|---|---|
| Affective Polarization | 74 | Continued trend; no structural break observed |
| Trust Deficit | 75 | Continued trend; DOGE/administration disruption likely depressing institutional confidence |
| Income Inequality | 68 | Continued trend + tariff/inflation effects on lower-income households |
| Legislative Polarization | 88 | 119th Congress; near historical ceiling |
| Epistemic Fragmentation | 83 | Continued trend; AI-generated content proliferation |
| Elite Misalignment | 74 | Continued trend |
| Fiscal Stress τ | 39 (τ≈0.300) | **Estimated**: FY2026 net interest projected ~$1,065B; GFR ~$3,550B; τ≈0.300. One Big Beautiful Bill Act effects and higher-rate rollover environment. |
| Political Responsiveness | 81 | Continued trend; executive consolidation dynamics |
| Institutional Capture | 77 | Continued trend; DOGE-era regulatory rollback |
| Cultural Solidarity | 74 | Continued trend |
| Household Economic Security | 68 | Continued trend; tariff pass-through to consumer prices |

**τ 2026 estimate sources:**
- CRFB August 2025 baseline projected interest payments surpassing $1.0T in FY2025
- FY2026 projection: ~$1,065B net interest based on CRFB/CBO forward estimates
- Revenue estimate incorporates tariff revenue increases partially offset by OBBA tax cuts
- Estimate uncertainty: ±0.015 on raw τ

---

## Important Caveats

1. **2025 data is mostly trend-extrapolated** except for τ, which is based on confirmed FY2025 Treasury data.
2. **2026 is estimated**, not observed. All non-τ dimensions are extrapolations; τ is a forward estimate.
3. These points break the 4-year interval structure of the original series. Treat them as interim updates pending formal data collection.
4. The model's Monte Carlo starting point now uses 2026 values, making forward projections more current but also more uncertain.
5. A full formal data update (all sources verified, not extrapolated) should be conducted when 2026 full-year data becomes available in early 2027.

---

## τ Quick Reference

| Year | Net Interest ($B) | GFR ($B) | τ raw | τ normalized | Status |
|---|---|---|---|---|---|
| 2020 | 345 | 2,111 | 0.163 | 21 | Actual |
| 2024 | 882 | 3,173 | 0.278 | 36 | Actual |
| 2025 | 970 | 3,440 | 0.282 | 37 | Actual (Treasury confirmed) |
| 2026 | ~1,065 | ~3,550 | ~0.300 | ~39 | Estimated |

τ° lower bound: 0.380 | Distance from 2026 estimate: **0.080** | Structural drift: ~0.022/yr
→ At current trajectory, τ reaches lower bound in approximately **3–4 years** (2029–2030).
