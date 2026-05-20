"""
monte_carlo.py — NFI R1 Monte Carlo Simulation Engine
======================================================
Purpose:
    Forward-projects the NFI from 2024 to the specified horizon using
    Monte Carlo sampling over the Dynamic Bayesian Network's probability
    distributions. Returns percentile envelopes and threshold crossing
    probabilities.

Dependencies:
    numpy, scipy, nfi_model

Key Assumptions:
    See ASSUMPTIONS dict below.

Changelog:
    R1.0 (2026): Initial implementation. Simplified DBN approximation
                 using conditional drift adjustments. Annual time steps.
                 Full pgmpy integration deferred to R2.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from scipy.special import expit  # sigmoid function

from nfi_model import (
    DIMENSION_KEYS, TAU_STAR, TAU_CALVO_LOW, TAU_CALVO_HIGH,
    TAU_CALVO_MID, tau_calvo_effective, compute_composite, ASSUMPTIONS
)

# ── ASSUMPTIONS ─────────────────────────────────────────────────────────────
ASSUMPTIONS.update({
    "mc_trend_model": (
        "Dimension trends modeled as historical drift + conditional "
        "feedback adjustments + normally distributed noise. Drift rates "
        "estimated from 2012-2024 acceleration (most recent trend window). "
        "See METHODOLOGY §7.1."
    ),
    "mc_feedback": (
        "Cross-dimensional feedback implemented as drift multipliers. "
        "Full pgmpy CPT-based inference deferred to R2. Current "
        "implementation captures primary feedback pathways identified "
        "in DBN structure. See METHODOLOGY §7.2."
    ),
    "mc_boundary": (
        "All dimensions bounded [0, 100]. τ additionally bounded at "
        "τ* normalized = 76.9. Calvo cascade modeled as probabilistic "
        "shock event once τ_eff exceeds τ°_effective."
    ),
    "calvo_cascade": (
        "NFI storm modeled as simultaneous shock to all social dimensions "
        "when Calvo event fires. Shock magnitude: HES +18, Trust +12, "
        "Affective +10, other social dims +7. τ spikes +18 normalized. "
        "Probability determined by sigmoid function at effective τ°. "
        "See METHODOLOGY §4.4."
    ),
})

# ── SCENARIO PARAMETERS ──────────────────────────────────────────────────────
SCENARIOS: Dict[str, Dict] = {
    "baseline": {
        "label": "Baseline — Current trajectory",
        "description": (
            "Current trends extrapolated. No structural change in "
            "political responsiveness, oligarchic dynamics, or fiscal "
            "policy. τ continues rising at recent rate."
        ),
        "drift_multiplier": 1.00,
        "tau_drift_multiplier": 1.00,
        "noise_multiplier": 1.00,
        "color": "#EF9F27",
    },
    "stress": {
        "label": "Stress — τ approaches τ° within cycle",
        "description": (
            "Fiscal deterioration accelerates. Bond market term premium "
            "expansion. τ reaches Calvo zone within one political cycle. "
            "NFI social dimensions continue deteriorating."
        ),
        "drift_multiplier": 1.25,
        "tau_drift_multiplier": 1.60,
        "noise_multiplier": 1.40,
        "color": "#E24B4A",
    },
    "recovery": {
        "label": "Recovery — Partial responsiveness restoration",
        "description": (
            "Oligarchic coalition fractures. Sustainability-aware faction "
            "gains influence. Partial fiscal stabilization. Social "
            "dimension acceleration slows but does not reverse."
        ),
        "drift_multiplier": 0.60,
        "tau_drift_multiplier": 0.55,
        "noise_multiplier": 0.80,
        "color": "#3DAD7A",
    },
}

# ── HISTORICAL ANNUAL DRIFT RATES (points/year, 2012-2024 trend) ─────────────
# Computed from historical series: (2024_value - 2012_value) / 12 years
ANNUAL_DRIFT: Dict[str, float] = {
    "affective_polarization":      2.17,   # 44→70 over 12 years
    "trust_deficit":               1.33,   # 55→71
    "income_inequality":           0.67,   # 58→66
    "legislative_polarization":    1.00,   # 74→86
    "epistemic_fragmentation":     1.42,   # 62→79
    "elite_misalignment":          0.75,   # 63→72
    "fiscal_stress_tau":           1.50,   # 18→36 (normalized)
    "political_responsiveness":    1.33,   # 62→78
    "institutional_capture":       0.67,   # 66→74
    "cultural_solidarity":         0.67,   # 64→72
    "household_economic_security": 1.67,   # 46→66
}

# ── HISTORICAL VOLATILITY (std dev, from year-to-year residuals) ─────────────
ANNUAL_SIGMA: Dict[str, float] = {
    "affective_polarization":      2.50,
    "trust_deficit":               3.00,
    "income_inequality":           1.50,
    "legislative_polarization":    1.80,
    "epistemic_fragmentation":     2.50,
    "elite_misalignment":          1.80,
    "fiscal_stress_tau":           3.50,
    "political_responsiveness":    2.00,
    "institutional_capture":       1.80,
    "cultural_solidarity":         1.50,
    "household_economic_security": 3.50,
}

# ── RESULT DATACLASS ─────────────────────────────────────────────────────────
@dataclass
class MCResults:
    """
    Monte Carlo simulation results container.

    Attributes
    ----------
    years : np.ndarray
        Projection years (2024 to horizon, annual).
    composite_pct : np.ndarray
        Shape (5, n_years). Rows: [10, 25, 50, 75, 90] percentiles
        of composite NFI score across all simulation runs.
    tau_pct : np.ndarray
        Same structure for τ normalized score.
    dimension_pct : dict
        Per-dimension percentile arrays, same structure.
    tau_raw_pct : np.ndarray
        Percentile envelopes for raw τ (0-1 scale).
    calvo_crossing_probs : dict
        P(τ > τ°_low) at selected future years.
        Keys: years (int), Values: probabilities (float 0-1).
    zone_exit_probs : dict
        P(NFI composite < 55) — Zone of Reduced Efficacy exit.
    n_runs : int
        Number of simulation runs executed.
    scenario : str
        Scenario identifier.
    n_calvo_events : int
        Number of runs in which Calvo cascade fired.
    """
    years: np.ndarray
    composite_pct: np.ndarray
    tau_pct: np.ndarray
    tau_raw_pct: np.ndarray
    dimension_pct: Dict[str, np.ndarray]
    calvo_crossing_probs: Dict[int, float]
    zone_exit_probs: Dict[int, float]
    n_runs: int
    scenario: str
    n_calvo_events: int = 0


# ── MAIN SIMULATION ENGINE ───────────────────────────────────────────────────
def run_monte_carlo(
    weights: Optional[Dict[str, float]] = None,
    scenario: str = "baseline",
    n_runs: int = 10_000,
    horizon: int = 2040,
    seed: Optional[int] = None,
    start_values: Optional[Dict[str, float]] = None,
) -> MCResults:
    """
    Execute Monte Carlo forward projection of the NFI.

    Parameters
    ----------
    weights : dict, optional
        Dimension weight coefficients summing to 1.0.
        Default: equal weighting (1/11 per dimension).
    scenario : str
        Scenario key: 'baseline', 'stress', or 'recovery'.
        Default: 'baseline'.
    n_runs : int
        Number of simulation runs. Default: 10,000.
        Use 50,000 for stable tail percentile estimates.
    horizon : int
        Final projection year. Default: 2040.
    seed : int, optional
        Random seed for reproducibility.
    start_values : dict, optional
        Override 2024 starting values for dimensions.
        Default: uses historical 2024 values.

    Returns
    -------
    MCResults
        Complete simulation results with percentile envelopes
        and threshold crossing probabilities.

    Notes
    -----
    Implementation uses simplified DBN approximation with conditional
    drift adjustments rather than full CPT-based Bayesian inference.
    Full pgmpy implementation deferred to R2.

    Each run evolves all 11 dimensions annually from 2024 to horizon
    using: D(t+1) = D(t) + drift_adjusted + feedback + N(0, σ)

    Examples
    --------
    >>> results = run_monte_carlo(n_runs=1000, scenario='baseline')
    >>> print(f"Median NFI 2030: {results.composite_pct[2, 6]:.1f}")
    """
    if seed is not None:
        np.random.seed(seed)

    # Default weights
    if weights is None:
        n = len(DIMENSION_KEYS)
        weights = {k: 1.0 / n for k in DIMENSION_KEYS}

    # Normalize weights
    total_w = sum(weights.values())
    weights = {k: v / total_w for k, v in weights.items()}

    # 2024 starting values
    defaults_2024 = {
        "affective_polarization": 70.0,
        "trust_deficit": 71.0,
        "income_inequality": 66.0,
        "legislative_polarization": 86.0,
        "epistemic_fragmentation": 79.0,
        "elite_misalignment": 72.0,
        "fiscal_stress_tau": 36.0,
        "political_responsiveness": 78.0,
        "institutional_capture": 74.0,
        "cultural_solidarity": 72.0,
        "household_economic_security": 66.0,
    }
    if start_values:
        defaults_2024.update(start_values)

    scen = SCENARIOS[scenario]
    drift_mult = scen["drift_multiplier"]
    tau_mult = scen["tau_drift_multiplier"]
    noise_mult = scen["noise_multiplier"]

    n_years = horizon - 2024 + 1
    years = np.arange(2024, horizon + 1)

    # Storage: shape (n_runs, n_years, n_dims)
    n_dims = len(DIMENSION_KEYS)
    all_trajectories = np.zeros((n_runs, n_years, n_dims))
    tau_raw_trajectories = np.zeros((n_runs, n_years))
    calvo_fired = np.zeros(n_runs, dtype=bool)

    # Convert 2024 τ normalized back to raw for simulation
    tau_raw_2024 = TAU_2024_RAW = 0.278

    for run in range(n_runs):
        state = np.array([defaults_2024[k] for k in DIMENSION_KEYS], dtype=float)
        tau_raw = tau_raw_2024
        calvo_has_fired = False

        for t, year in enumerate(years):
            # Store current state
            all_trajectories[run, t] = state.copy()
            tau_raw_trajectories[run, t] = tau_raw

            if t == n_years - 1:
                break

            # --- Compute feedback adjustments ---
            dim_dict = dict(zip(DIMENSION_KEYS, state))

            # NFI social composite (excluding τ) for dynamic τ° adjustment
            social_keys = [k for k in DIMENSION_KEYS if k != "fiscal_stress_tau"]
            social_composite = np.mean([dim_dict[k] for k in social_keys])

            # τ normalized (for feedback calculations)
            tau_norm = (tau_raw / TAU_STAR) * 100

            # Feedback multipliers on drift
            feedback = _compute_feedback(dim_dict, tau_norm, social_composite)

            # --- Evolve each dimension ---
            new_state = state.copy()
            for i, key in enumerate(DIMENSION_KEYS):
                if key == "fiscal_stress_tau":
                    continue  # τ handled separately below

                base_drift = ANNUAL_DRIFT[key] * drift_mult
                adj_drift = base_drift * (1 + feedback.get(key, 0))
                noise = np.random.normal(0, ANNUAL_SIGMA[key] * noise_mult)
                new_val = state[i] + adj_drift + noise
                new_state[i] = np.clip(new_val, 0.0, 100.0)

            # --- Evolve τ ---
            tau_drift = _tau_drift(tau_raw, social_composite, tau_mult)
            tau_noise = np.random.normal(0, 0.008 * noise_mult)
            tau_raw_new = tau_raw + tau_drift + tau_noise
            tau_raw_new = np.clip(tau_raw_new, 0.0, TAU_STAR)

            # --- Calvo cascade check ---
            tau_low_eff, tau_high_eff = tau_calvo_effective(social_composite)
            tau_mid_eff = (tau_low_eff + tau_high_eff) / 2
            calvo_prob = float(expit(25.0 * (tau_raw_new - tau_mid_eff))) * 0.15

            if not calvo_has_fired and np.random.random() < calvo_prob:
                calvo_has_fired = True
                calvo_fired[run] = True
                new_state, tau_raw_new = _apply_calvo_cascade(
                    new_state, tau_raw_new
                )

            # Update τ dimension in state vector
            tau_norm_new = min((tau_raw_new / TAU_STAR) * 100, 100)
            tau_idx = DIMENSION_KEYS.index("fiscal_stress_tau")
            new_state[tau_idx] = tau_norm_new
            tau_raw = tau_raw_new
            state = new_state

    # --- Compute composites ---
    composite_trajectories = np.zeros((n_runs, n_years))
    for run in range(n_runs):
        for t in range(n_years):
            dim_vals = {k: all_trajectories[run, t, i]
                        for i, k in enumerate(DIMENSION_KEYS)}
            composite_trajectories[run, t] = sum(
                dim_vals[k] * weights[k] for k in DIMENSION_KEYS
            )

    # --- Extract percentiles ---
    pcts = [10, 25, 50, 75, 90]
    composite_pct = np.percentile(composite_trajectories, pcts, axis=0)

    tau_norm_trajectories = (tau_raw_trajectories / TAU_STAR) * 100
    tau_pct = np.percentile(tau_norm_trajectories, pcts, axis=0)
    tau_raw_pct = np.percentile(tau_raw_trajectories, pcts, axis=0)

    dimension_pct = {}
    for i, key in enumerate(DIMENSION_KEYS):
        dimension_pct[key] = np.percentile(
            all_trajectories[:, :, i], pcts, axis=0
        )

    # --- Threshold crossing probabilities ---
    calvo_probs = {}
    zone_exit_probs = {}
    for target_year in [2026, 2028, 2030, 2032, 2035, 2040]:
        if target_year > horizon:
            continue
        t_idx = target_year - 2024
        # P(τ > τ°_low_effective)
        # Use mean social composite at that time point
        mean_social = np.mean([
            np.mean(all_trajectories[:, t_idx, i])
            for i, k in enumerate(DIMENSION_KEYS)
            if k != "fiscal_stress_tau"
        ])
        low_eff, _ = tau_calvo_effective(mean_social)
        calvo_probs[target_year] = float(
            np.mean(tau_raw_trajectories[:, t_idx] > low_eff)
        )
        # P(NFI < 55) — recovery threshold
        zone_exit_probs[target_year] = float(
            np.mean(composite_trajectories[:, t_idx] < 55.0)
        )

    return MCResults(
        years=years,
        composite_pct=composite_pct,
        tau_pct=tau_pct,
        tau_raw_pct=tau_raw_pct,
        dimension_pct=dimension_pct,
        calvo_crossing_probs=calvo_probs,
        zone_exit_probs=zone_exit_probs,
        n_runs=n_runs,
        scenario=scenario,
        n_calvo_events=int(np.sum(calvo_fired)),
    )


def _compute_feedback(
    dim_dict: Dict[str, float],
    tau_norm: float,
    social_composite: float,
) -> Dict[str, float]:
    """
    Compute cross-dimensional feedback drift multipliers.

    Implements the key feedback pathways from the DBN structure:
    - High legislative polarization blocks τ correction
    - High τ pressures household economic security
    - Epistemic fragmentation reinforces political responsiveness decay
    - Household stress amplifies affective polarization
    """
    feedback: Dict[str, float] = {}

    # Legislative polarization → fiscal blockage (τ drift amplification)
    leg_excess = max(0, dim_dict["legislative_polarization"] - 60) / 40
    feedback["fiscal_stress_tau"] = leg_excess * 0.30

    # τ → Household Economic Security
    tau_pressure = max(0, tau_norm - 25) / 75
    feedback["household_economic_security"] = tau_pressure * 0.20

    # Epistemic → Political Responsiveness (accelerates decay)
    ep_excess = max(0, dim_dict["epistemic_fragmentation"] - 55) / 45
    feedback["political_responsiveness"] = ep_excess * 0.15

    # Political Responsiveness → Legislative Polarization
    pr_excess = max(0, dim_dict["political_responsiveness"] - 50) / 50
    feedback["legislative_polarization"] = pr_excess * 0.12

    # Household stress → Affective Polarization (Becker pathway)
    hes_excess = max(0, dim_dict["household_economic_security"] - 40) / 60
    feedback["affective_polarization"] = hes_excess * 0.15

    # Institutional Capture → Epistemic (funds partisan media)
    ic_excess = max(0, dim_dict["institutional_capture"] - 50) / 50
    feedback["epistemic_fragmentation"] = ic_excess * 0.10

    # High social composite → all social dims (systemic acceleration)
    systemic = max(0, social_composite - 60) / 40 * 0.08
    for key in ["trust_deficit", "cultural_solidarity", "elite_misalignment"]:
        feedback[key] = feedback.get(key, 0) + systemic

    return feedback


def _tau_drift(
    tau_raw: float,
    social_composite: float,
    tau_mult: float,
) -> float:
    """
    Compute annual τ drift incorporating structural and political components.

    Structural component: rollover repricing (~0.018/year baseline)
    Political blockage: increases as social fracture rises
    """
    # Structural drift from debt rollover repricing
    structural = 0.016 * tau_mult

    # Political blockage amplifier (high fracture = less fiscal adjustment)
    blockage = 1.0 + max(0, (social_composite - 55) / 45) * 0.35

    return structural * blockage


def _apply_calvo_cascade(
    state: np.ndarray,
    tau_raw: float,
) -> Tuple[np.ndarray, float]:
    """
    Apply NFI storm shock when Calvo discontinuity fires.

    Simultaneous spikes across all social dimensions and τ
    representing the cascade from sovereign confidence failure.
    """
    cascaded = state.copy()
    shocks = {
        "household_economic_security":  18.0,
        "trust_deficit":                12.0,
        "affective_polarization":       10.0,
        "epistemic_fragmentation":       8.0,
        "legislative_polarization":      6.0,
        "political_responsiveness":      6.0,
        "cultural_solidarity":           5.0,
        "elite_misalignment":            4.0,
        "institutional_capture":         3.0,
        "income_inequality":             3.0,
    }
    for i, key in enumerate(DIMENSION_KEYS):
        if key in shocks:
            cascaded[i] = min(100.0, state[i] + shocks[key])

    # τ spike from forced repricing
    tau_raw_new = min(TAU_STAR, tau_raw + 0.12)

    return cascaded, tau_raw_new


# ── SENSITIVITY ANALYSIS ──────────────────────────────────────────────────────
def weight_sensitivity_analysis(
    target_year: int = 2035,
    n_weight_configs: int = 500,
    n_runs_per_config: int = 500,
    seed: int = 42,
) -> Dict:
    """
    Run Latin Hypercube weight sensitivity analysis.

    Tests n_weight_configs different weight configurations, each with
    n_runs_per_config Monte Carlo runs, to identify which dimensions
    most affect P(τ > τ°) and composite NFI projections.

    Parameters
    ----------
    target_year : int
        Year to evaluate sensitivity at. Default: 2035.
    n_weight_configs : int
        Number of weight configurations to test. Default: 500.
    n_runs_per_config : int
        MC runs per weight config. Default: 500.
    seed : int
        Random seed. Default: 42.

    Returns
    -------
    dict
        'weights_matrix': np.ndarray shape (n_configs, n_dims)
        'calvo_probs': np.ndarray shape (n_configs,)
        'composite_medians': np.ndarray shape (n_configs,)
        'dimension_keys': list of dimension key strings
    """
    from scipy.stats import qmc

    np.random.seed(seed)
    sampler = qmc.LatinHypercube(d=len(DIMENSION_KEYS), seed=seed)
    raw_weights = sampler.random(n=n_weight_configs)
    # Normalize each row to sum to 1
    weight_matrix = raw_weights / raw_weights.sum(axis=1, keepdims=True)

    calvo_probs = np.zeros(n_weight_configs)
    composite_medians = np.zeros(n_weight_configs)

    for idx in range(n_weight_configs):
        w = dict(zip(DIMENSION_KEYS, weight_matrix[idx]))
        results = run_monte_carlo(
            weights=w,
            n_runs=n_runs_per_config,
            horizon=target_year,
            seed=seed + idx,
        )
        calvo_probs[idx] = results.calvo_crossing_probs.get(target_year, 0.0)
        t_idx = target_year - 2024
        composite_medians[idx] = results.composite_pct[2, t_idx]  # 50th pct

    return {
        "weights_matrix": weight_matrix,
        "calvo_probs": calvo_probs,
        "composite_medians": composite_medians,
        "dimension_keys": DIMENSION_KEYS,
    }
