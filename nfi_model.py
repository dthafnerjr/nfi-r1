"""
nfi_model.py — National Fracture Index R1 Core Data Model
==========================================================
Purpose:
    Defines all 11 NFI dimensions, loads historical data series,
    computes composite scores, and provides the τ (tau) fiscal
    stress function with normalization and threshold parameters.

Dependencies:
    numpy, pandas, pathlib

Key Assumptions:
    See ASSUMPTIONS dict below.

Changelog:
    R1.0 (2026): Initial implementation. 11 dimensions.
                 Equal-weight baseline. 1972-2024 historical series.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── ASSUMPTIONS ────────────────────────────────────────────────────────────
ASSUMPTIONS: Dict[str, str] = {
    "baseline_year": (
        "1972 treated as early-transition period, not stable equilibrium. "
        "Rodgers dates Age of Fracture origin to ~1974; 1972 baseline "
        "captures the final pre-fracture data point. See METHODOLOGY §3."
    ),
    "normalization_scale": (
        "All dimensions normalized 0-100. Higher scores indicate greater "
        "fracture/stress. τ normalized as (τ/τ*) × 100 where τ*=0.769. "
        "See METHODOLOGY §4."
    ),
    "equal_weighting": (
        "Default composite uses equal weighting (1/11 per dimension). "
        "This is a baseline assumption, not a finding. Users should "
        "test sensitivity to weight changes. See METHODOLOGY §9."
    ),
    "tau_star": (
        "τ* = 0.769 computed as 1 - (primary_deficit/T) from 2024 OMB "
        "baseline. Represents mathematical ceiling where all general fund "
        "revenue is consumed by interest. See METHODOLOGY §4.2."
    ),
    "tau_calvo": (
        "τ° ≈ 0.38-0.45 estimated from Morris-Shin coordination game "
        "applied to US sovereign bond market. Dynamic: effective τ° "
        "decreases as NFI social composite rises. See METHODOLOGY §4.3."
    ),
    "citizens_united": (
        "Citizens United (2010) treated as structural break / parameter "
        "shift in Political Responsiveness and Institutional Capture, "
        "not trend continuation. Implemented as DBN parameter change "
        "at t=2012 data point. See METHODOLOGY §5.5."
    ),
    "data_scarcity": (
        "Historical series uses n=14 observations at 4-year intervals "
        "1972-2024. CPT estimation is statistically underdetermined. "
        "Dirichlet regularization applied. Results are indicative "
        "probability ranges. See METHODOLOGY §6.3."
    ),
}

# ── DIMENSION METADATA ─────────────────────────────────────────────────────
@dataclass
class DimensionMeta:
    """Metadata for a single NFI dimension."""
    key: str
    label: str
    label_short: str
    color: str
    theory: str
    sources: str
    description: str
    is_new: bool = False

DIMENSIONS: List[DimensionMeta] = [
    DimensionMeta(
        key="affective_polarization",
        label="Affective Polarization",
        label_short="Affective",
        color="#D85A30",
        theory="Iyengar et al. partisan animosity literature",
        sources="Pew Research affective polarization surveys",
        description=(
            "Measures emotional hostility between partisan groups, "
            "distinct from policy disagreement. Higher scores indicate "
            "stronger out-group animus and identity-protective cognition."
        ),
    ),
    DimensionMeta(
        key="trust_deficit",
        label="Institutional Trust Deficit",
        label_short="Trust",
        color="#378ADD",
        theory="Putnam social capital; Turchin institutional legitimacy",
        sources="Gallup confidence-in-institutions series (inverted)",
        description=(
            "Inverted measure of public confidence across federal, state, "
            "and civic institutions. Rising scores reflect delegitimization "
            "of the institutional framework required for collective action."
        ),
    ),
    DimensionMeta(
        key="income_inequality",
        label="Income Inequality",
        label_short="Inequality",
        color="#7F77DD",
        theory="Piketty r > g capital concentration thesis",
        sources="Saez-Zucman top 1% / 0.1% wealth share; supplemented by Gini",
        description=(
            "Piketty-enhanced inequality measure using top wealth "
            "concentration rather than Gini alone. Captures the "
            "capital accumulation dynamic that drives institutional capture "
            "and household stress."
        ),
    ),
    DimensionMeta(
        key="legislative_polarization",
        label="Legislative Polarization",
        label_short="Legislative",
        color="#E24B4A",
        theory="Voteview DW-NOMINATE; median voter theorem breakdown",
        sources="DW-NOMINATE legislative distance data (Poole & Rosenthal)",
        description=(
            "Ideological distance between congressional party medians. "
            "High scores indicate the legislature cannot form the "
            "cross-partisan coalitions required for fiscal consolidation "
            "or institutional reform."
        ),
    ),
    DimensionMeta(
        key="epistemic_fragmentation",
        label="Epistemic Fragmentation",
        label_short="Epistemic",
        color="#0F6E56",
        theory="Rodgers Age of Fracture; filter bubble / media silo literature",
        sources="Reuters Institute Digital News Report; Media Insight Project",
        description=(
            "Degree to which the population occupies divergent information "
            "ecosystems. Incorporates partisan media audience segregation, "
            "algorithmic filter bubble intensity, and shared-fact erosion."
        ),
    ),
    DimensionMeta(
        key="elite_misalignment",
        label="Elite Misalignment",
        label_short="Elite",
        color="#D4537E",
        theory="Turchin structural-demographic; Piketty wealth separation",
        sources="Turchin elite divergence series; geographic income segregation",
        description=(
            "Social and experiential separation between elites and the "
            "general population. Measures the condition of divergence — "
            "distinct from Institutional Capture which measures the "
            "active employment of that positional advantage."
        ),
    ),
    DimensionMeta(
        key="fiscal_stress_tau",
        label="Fiscal Stress (τ)",
        label_short="Fiscal τ",
        color="#6EC9C4",
        theory="Morris-Shin coordination game; Calvo sovereign debt discontinuity",
        sources="OMB Historical Tables net interest; CBO general fund revenue",
        description=(
            "τ = Net Interest / General Fund Revenue. Dual status: "
            "NFI dimension AND potential cascade trigger. "
            "τ* = 0.769 (mathematical ceiling). "
            "τ° ≈ 0.38-0.45 (Calvo discontinuity trigger). "
            "Current (2024): τ ≈ 0.278."
        ),
    ),
    DimensionMeta(
        key="political_responsiveness",
        label="Political Responsiveness",
        label_short="Pol. Resp.",
        color="#E8A020",
        theory="Median voter theorem; Citizens United structural break (2010)",
        sources=(
            "Cook Political Report / Sabato competitive seat ratings; "
            "FEC campaign finance data; primary vs. general turnout ratios"
        ),
        description=(
            "Degree to which electoral mechanisms function as accountability "
            "tools for median voter preferences. High scores indicate "
            "non-competitive elections, primary extremism, and dark money "
            "insulation of incumbents from constituent accountability."
        ),
        is_new=True,
    ),
    DimensionMeta(
        key="institutional_capture",
        label="Institutional Capture",
        label_short="Inst. Capture",
        color="#A85CC4",
        theory="Acemoglu & Robinson extractive institutions; Citizens United",
        sources=(
            "OpenSecrets lobbying data; revolving door index; "
            "corporate-to-labor political spending ratio; "
            "effective top marginal tax rate trend"
        ),
        description=(
            "Active employment of elite positional advantage to reshape "
            "institutions in extractive directions. Distinct from Elite "
            "Misalignment (the condition): this measures the action. "
            "Structural break at Citizens United (2010)."
        ),
        is_new=True,
    ),
    DimensionMeta(
        key="cultural_solidarity",
        label="Cultural Solidarity",
        label_short="Solidarity",
        color="#3DAD7A",
        theory=(
            "Rodgers Age of Fracture dissolution of collective vocabulary; "
            "Putnam Bowling Alone civic capital decline"
        ),
        sources=(
            "BLS union membership series; Putnam civic participation index; "
            "cross-class social mixing indicators"
        ),
        description=(
            "Degree to which shared conceptual frameworks, civic "
            "institutions, and cross-class social bonds remain intact. "
            "Rodgers dates origin of dissolution to ~1974. "
            "High scores indicate advanced Bonhoeffer sociological "
            "stupidity conditions."
        ),
        is_new=True,
    ),
    DimensionMeta(
        key="household_economic_security",
        label="Household Economic Security",
        label_short="HH Security",
        color="#E85D77",
        theory=(
            "Survival inflation gap; Piketty asset-price / wage divergence; "
            "Becker TMT material anxiety → immortality project susceptibility"
        ),
        sources=(
            "Harvard JCHS housing cost burden data; "
            "USDA food security reports; "
            "BLS real wage series vs. necessity CPI basket"
        ),
        description=(
            "Adequacy of household material conditions relative to "
            "basic survival costs. Measures housing cost burden, food "
            "insecurity rate, and the real wage / survival inflation gap. "
            "Distinct from Income Inequality: measures absolute adequacy, "
            "not distributional structure."
        ),
        is_new=True,
    ),
]

# ── TAU PARAMETERS ─────────────────────────────────────────────────────────
TAU_STAR: float = 0.769       # Mathematical ceiling
TAU_CALVO_LOW: float = 0.380  # Calvo trigger lower bound
TAU_CALVO_HIGH: float = 0.450 # Calvo trigger upper bound
TAU_CALVO_MID: float = 0.415  # Calvo trigger midpoint estimate
TAU_2024: float = 0.278       # Current observed value

DIMENSION_KEYS: List[str] = [d.key for d in DIMENSIONS]
DIMENSION_COLORS: Dict[str, str] = {d.key: d.color for d in DIMENSIONS}
DIMENSION_LABELS: Dict[str, str] = {d.key: d.label for d in DIMENSIONS}
DIMENSION_SHORT: Dict[str, str] = {d.key: d.label_short for d in DIMENSIONS}

# ── DATA LOADING ───────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

def load_historical_data() -> pd.DataFrame:
    """
    Load NFI historical dimension data (1972-2024).

    Returns
    -------
    pd.DataFrame
        Columns: year, all 11 dimension keys, composite.
        Index: integer 0-13 (14 four-year observations).

    Notes
    -----
    Data represents 4-year interval observations normalised 0-100.
    Sources and construction methodology documented in METHODOLOGY.md §3.
    """
    path = DATA_DIR / "historical_dimensions.csv"
    df = pd.read_csv(path)
    return df


def load_tau_data() -> pd.DataFrame:
    """
    Load historical τ (fiscal stress) data series.

    Returns
    -------
    pd.DataFrame
        Columns: year, tau_raw, tau_normalized, net_interest_bn,
                 general_fund_revenue_bn.
    """
    path = DATA_DIR / "tau_historical.csv"
    return pd.read_csv(path)


# ── COMPOSITE COMPUTATION ──────────────────────────────────────────────────
def compute_composite(
    data: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
) -> pd.Series:
    """
    Compute weighted composite NFI score from dimension scores.

    Parameters
    ----------
    data : pd.DataFrame
        Must contain all DIMENSION_KEYS as columns.
    weights : dict, optional
        Dimension weights summing to 1.0.
        Default: equal weighting (1/11 per dimension).

    Returns
    -------
    pd.Series
        Composite NFI score 0-100 for each row.

    Examples
    --------
    >>> df = load_historical_data()
    >>> composite = compute_composite(df)
    >>> print(f"2024 composite: {composite.iloc[-1]:.1f}")
    2024 composite: 70.0
    """
    if weights is None:
        n = len(DIMENSION_KEYS)
        weights = {k: 1.0 / n for k in DIMENSION_KEYS}

    # Validate weights sum to ~1.0
    total = sum(weights.values())
    if abs(total - 1.0) > 0.01:
        weights = {k: v / total for k, v in weights.items()}

    composite = sum(
        data[key] * weights[key]
        for key in DIMENSION_KEYS
        if key in data.columns
    )
    return composite.round(1)


def tau_normalize(tau_raw: float) -> float:
    """
    Normalize raw τ value to 0-100 scale.

    Parameters
    ----------
    tau_raw : float
        Raw τ = net_interest / general_fund_revenue.

    Returns
    -------
    float
        Normalized score 0-100 where 100 = τ* (mathematical ceiling).

    Notes
    -----
    Normalization: τ_norm = (τ / τ*) × 100
    τ* = 0.769 (see ASSUMPTIONS['tau_star'])
    """
    return round(min((tau_raw / TAU_STAR) * 100, 100), 1)


def tau_calvo_effective(nfi_social_composite: float) -> Tuple[float, float]:
    """
    Compute dynamic Calvo trigger adjusted for social fracture level.

    The effective Calvo trigger is lower when social fracture is high
    because political capacity to coordinate a fiscal response is degraded.

    Parameters
    ----------
    nfi_social_composite : float
        NFI composite excluding τ dimension (0-100).

    Returns
    -------
    Tuple[float, float]
        (tau_calvo_low_effective, tau_calvo_high_effective)
        Adjusted Calvo trigger range accounting for political degradation.

    Notes
    -----
    Adjustment: δτ° = -0.06 × (nfi_social - 50) / 50
    At NFI social = 50: no adjustment.
    At NFI social = 100: τ° reduced by 0.06 (≈ 14% of base trigger).
    See METHODOLOGY §4.3 for theoretical derivation.
    """
    degradation = 0.06 * max(0, (nfi_social_composite - 50) / 50)
    low_eff = max(0.25, TAU_CALVO_LOW - degradation)
    high_eff = max(0.30, TAU_CALVO_HIGH - degradation)
    return low_eff, high_eff


def compute_calvo_proximity(tau_raw: float, nfi_social: float) -> float:
    """
    Compute Calvo proximity score (0-100).

    Parameters
    ----------
    tau_raw : float
        Current raw τ value.
    nfi_social : float
        NFI social composite (excluding τ dimension).

    Returns
    -------
    float
        Proximity score 0-100 where:
        0-30: low concern
        30-60: elevated concern
        60-80: warning zone
        80+: critical — Calvo discontinuity structurally plausible

    Notes
    -----
    Uses sigmoid function centered at effective τ°.
    """
    low_eff, high_eff = tau_calvo_effective(nfi_social)
    tau_mid_eff = (low_eff + high_eff) / 2
    # Sigmoid: 50% probability at effective τ°
    k = 25.0  # steepness calibrated to empirical threshold width
    proximity = 100 / (1 + np.exp(-k * (tau_raw - tau_mid_eff)))
    return round(proximity, 1)


# ── LORENZ DISTRIBUTION ────────────────────────────────────────────────────
def compute_lorenz(dimension_scores: List[float]) -> Tuple[List[float], List[float], float]:
    """
    Compute Lorenz-style fracture distribution curve.

    Parameters
    ----------
    dimension_scores : list of float
        Scores for all dimensions at a given time point.

    Returns
    -------
    Tuple[List[float], List[float], float]
        (x_pct, y_cumulative_pct, concentration_coefficient)
        x: cumulative % of domains (sorted low to high)
        y: cumulative % of total fracture score
        coeff: Gini-style concentration coefficient (Trapezoid method)

    Notes
    -----
    Declining concentration coefficient over time indicates fracture
    becoming pervasive (systemic) rather than concentrated (addressable).
    """
    n = len(dimension_scores)
    sorted_scores = sorted(dimension_scores)
    total = sum(sorted_scores)

    if total == 0:
        return [0, 100], [0, 100], 0.0

    x = [0.0] + [100 * (i + 1) / n for i in range(n)]
    cumulative = 0.0
    y = [0.0]
    for s in sorted_scores:
        cumulative += s
        y.append(100 * cumulative / total)

    # Gini concentration coefficient via trapezoid method
    equality_area = 0.5
    lorenz_area = 0.0
    for i in range(len(x) - 1):
        dx = (x[i + 1] - x[i]) / 100
        lorenz_area += dx * (y[i] + y[i + 1]) / 2 / 100
    gini = round(1 - 2 * lorenz_area, 3)

    return x, y, gini
