"""
app.py — National Fracture Index R1 Streamlit Application
==========================================================
Purpose:
    Primary interactive interface for the NFI R1 model.
    Provides historical visualization, τ dashboard with market
    signals, Monte Carlo forward projections, adjustable dimension
    weights, and scenario comparison.

Run:
    streamlit run app.py

Dependencies:
    streamlit, plotly, numpy, pandas, nfi_model, monte_carlo,
    market_signals (all in requirements.txt)

Changelog:
    R1.0 (2026): Initial Streamlit interface. Five tabs.
                 Live Monte Carlo. Market signal overlay.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, Optional

from nfi_model import (
    load_historical_data, load_tau_data, compute_composite,
    compute_lorenz, tau_normalize, tau_calvo_effective,
    compute_calvo_proximity, DIMENSIONS, DIMENSION_KEYS,
    DIMENSION_COLORS, DIMENSION_LABELS, DIMENSION_SHORT,
    TAU_STAR, TAU_CALVO_LOW, TAU_CALVO_HIGH, TAU_2024,
)
from monte_carlo import run_monte_carlo, SCENARIOS, weight_sensitivity_analysis
from market_signals import (
    fetch_live_signals, compute_signals_manual, MarketSignals
)

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="National Fracture Index R1",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── COLORS ───────────────────────────────────────────────────────────────────
C = {
    "bg":         "#0b0e14",
    "surface":    "#13171f",
    "border":     "#1e2530",
    "text":       "#d4d8e0",
    "muted":      "#5c6370",
    "amber":      "#EF9F27",
    "amber_dk":   "#BA7517",
    "danger":     "#E24B4A",
    "safe":       "#3DAD7A",
    "grid":       "rgba(255,255,255,0.07)",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color=C["text"],
    font_family="IBM Plex Mono, monospace",
    font_size=11,
    xaxis=dict(gridcolor=C["grid"], linecolor=C["grid"]),
    yaxis=dict(gridcolor=C["grid"], linecolor=C["grid"]),
    margin=dict(l=40, r=20, t=30, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=C["border"],
        borderwidth=1,
        font_size=10,
    ),
)

# ── DATA LOADING (cached) ─────────────────────────────────────────────────────
@st.cache_data
def get_data():
    df = load_historical_data()
    tau_df = load_tau_data()
    return df, tau_df

# ── WEIGHT DEFAULTS ───────────────────────────────────────────────────────────
DEFAULT_WEIGHT = round(100 / len(DIMENSION_KEYS), 1)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def build_sidebar() -> Dict[str, float]:
    st.sidebar.markdown(
        "## ⚖️ Dimension Weights\n"
        "_Adjust to explore model sensitivity._\n"
        "_Weights auto-normalize to sum to 100._"
    )
    st.sidebar.markdown("---")

    # Preset buttons
    col1, col2 = st.sidebar.columns(2)
    preset = None
    with col1:
        if st.button("Equal", help="Equal weighting (default)", use_container_width=True):
            preset = "equal"
        if st.button("Piketty", help="Capital concentration emphasis", use_container_width=True):
            preset = "piketty"
    with col2:
        if st.button("Fiscal τ", help="Fiscal stress dominant", use_container_width=True):
            preset = "fiscal"
        if st.button("Social", help="Social dimensions emphasis", use_container_width=True):
            preset = "social"

    # Preset definitions
    presets = {
        "equal": {k: DEFAULT_WEIGHT for k in DIMENSION_KEYS},
        "piketty": {
            "income_inequality": 18, "institutional_capture": 14,
            "household_economic_security": 14, "elite_misalignment": 10,
            "fiscal_stress_tau": 12, "legislative_polarization": 8,
            "affective_polarization": 6, "trust_deficit": 6,
            "epistemic_fragmentation": 6, "political_responsiveness": 4,
            "cultural_solidarity": 2,
        },
        "fiscal": {
            "fiscal_stress_tau": 25, "legislative_polarization": 15,
            "institutional_capture": 12, "income_inequality": 10,
            "household_economic_security": 10, "political_responsiveness": 8,
            "trust_deficit": 6, "affective_polarization": 5,
            "epistemic_fragmentation": 4, "elite_misalignment": 3,
            "cultural_solidarity": 2,
        },
        "social": {
            "affective_polarization": 14, "trust_deficit": 12,
            "epistemic_fragmentation": 12, "cultural_solidarity": 12,
            "political_responsiveness": 12, "legislative_polarization": 10,
            "household_economic_security": 10, "elite_misalignment": 8,
            "fiscal_stress_tau": 5, "institutional_capture": 3,
            "income_inequality": 2,
        },
    }

    # Initialise session state weights
    if "weights" not in st.session_state or preset:
        key_preset = preset or "equal"
        st.session_state["weights"] = presets[key_preset].copy()

    st.sidebar.markdown("---")

    raw_weights = {}
    for dim in DIMENSIONS:
        val = st.sidebar.slider(
            dim.label_short,
            min_value=0,
            max_value=30,
            value=int(st.session_state["weights"].get(dim.key, DEFAULT_WEIGHT)),
            step=1,
            help=dim.description[:120] + "…",
        )
        raw_weights[dim.key] = val

    # Normalize
    total = sum(raw_weights.values()) or 1
    weights = {k: v / total for k, v in raw_weights.items()}

    # Weight distribution bar
    st.sidebar.markdown("---")
    st.sidebar.caption("Weight distribution")
    weight_df = pd.DataFrame({
        "Dimension": [DIMENSION_SHORT[k] for k in DIMENSION_KEYS],
        "Weight (%)": [round(weights[k] * 100, 1) for k in DIMENSION_KEYS],
    })
    st.sidebar.dataframe(
        weight_df,
        hide_index=True,
        use_container_width=True,
        height=320,
    )

    return weights


# ── CHART HELPERS ─────────────────────────────────────────────────────────────
def styled_fig(**kwargs) -> go.Figure:
    fig = go.Figure(**kwargs)
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def add_threshold_line(fig, y, label, color, dash="dash", row=None, col=None):
    kw = dict(row=row, col=col) if row else {}
    fig.add_hline(
        y=y, line_dash=dash, line_color=color, line_width=1,
        annotation_text=label,
        annotation_font_color=color,
        annotation_font_size=9,
        **kw,
    )


# ── TAB 1: OVERVIEW ──────────────────────────────────────────────────────────
def tab_overview(df: pd.DataFrame, weights: Dict[str, float]):
    composite = compute_composite(df, weights)
    current_score = composite.iloc[-1]
    delta = current_score - composite.iloc[0]

    # Header KPIs
    cols = st.columns([2] + [1] * 6)
    with cols[0]:
        st.metric(
            "Composite NFI (2024)",
            f"{current_score:.0f} / 100",
            delta=f"+{delta:.0f} from 1972",
            delta_color="inverse",
        )

    kpi_dims = [
        "affective_polarization", "trust_deficit", "legislative_polarization",
        "epistemic_fragmentation", "fiscal_stress_tau", "household_economic_security",
    ]
    for i, key in enumerate(kpi_dims):
        with cols[i + 1]:
            val = df[key].iloc[-1]
            d72 = df[key].iloc[0]
            st.metric(
                DIMENSION_SHORT[key],
                f"{val:.0f}",
                delta=f"+{val - d72:.0f}",
                delta_color="inverse",
            )

    st.markdown("---")

    # Main trend chart
    fig = styled_fig()
    years = df["year"].tolist()

    # Composite line (thick)
    fig.add_trace(go.Scatter(
        x=years, y=composite.tolist(),
        name="Composite NFI",
        line=dict(color=C["amber_dk"], width=3),
        mode="lines",
    ))

    # Individual dimensions (thin)
    for dim in DIMENSIONS:
        if dim.key not in df.columns:
            continue
        fig.add_trace(go.Scatter(
            x=years, y=df[dim.key].tolist(),
            name=dim.label_short,
            line=dict(color=dim.color, width=1.5, dash="solid"),
            mode="lines",
            opacity=0.8,
        ))

    # Zone of Reduced Efficacy annotation
    fig.add_hrect(
        y0=60, y1=100,
        fillcolor="rgba(226,75,74,0.06)",
        line_width=0,
        annotation_text="Zone of Reduced Efficacy",
        annotation_position="top left",
        annotation_font_color=C["danger"],
        annotation_font_size=9,
    )

    fig.update_layout(
        title="NFI Composite & Component Indicators — 1972–2024",
        xaxis_title="Year",
        yaxis_title="Score (0–100)",
        yaxis_range=[0, 100],
        height=360,
        **{k: v for k, v in PLOTLY_LAYOUT.items()
           if k not in ("paper_bgcolor", "plot_bgcolor", "font_color",
                        "font_family", "font_size", "margin", "legend")},
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    # Lorenz and Radar row
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("##### Fracture Distribution — Lorenz Curve (2024 vs 1972)")
        scores_1972 = [df[k].iloc[0] for k in DIMENSION_KEYS]
        scores_2024 = [df[k].iloc[-1] for k in DIMENSION_KEYS]

        x72, y72, gini72 = compute_lorenz(scores_1972)
        x24, y24, gini24 = compute_lorenz(scores_2024)
        n = len(DIMENSION_KEYS)
        x_eq = [100 * i / n for i in range(n + 1)]

        fig_l = styled_fig()
        fig_l.add_trace(go.Scatter(
            x=x_eq, y=x_eq, name="Equal distribution",
            line=dict(color=C["muted"], dash="dot", width=1),
        ))
        fig_l.add_trace(go.Scatter(
            x=x72, y=y72,
            name=f"1972 (coeff {gini72:.3f})",
            line=dict(color="#378ADD", width=2),
            mode="lines+markers",
        ))
        fig_l.add_trace(go.Scatter(
            x=x24, y=y24,
            name=f"2024 (coeff {gini24:.3f})",
            line=dict(color=C["amber"], width=2),
            mode="lines+markers",
        ))
        fig_l.update_layout(
            xaxis_title="Cumulative % of domains (low → high)",
            yaxis_title="Cumulative % of fracture score",
            height=280,
            **PLOTLY_LAYOUT,
        )
        st.plotly_chart(fig_l, use_container_width=True)
        st.caption(
            "Declining concentration coefficient: fracture shifting "
            "from addressable (concentrated) to systemic (pervasive)."
        )

    with col_r:
        st.markdown("##### Dimensional Profile — 2024 vs 1972 Baseline")
        labels_radar = [DIMENSION_SHORT[k] for k in DIMENSION_KEYS]
        vals_2024 = [df[k].iloc[-1] for k in DIMENSION_KEYS]
        vals_1972 = [df[k].iloc[0] for k in DIMENSION_KEYS]

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=vals_2024 + [vals_2024[0]],
            theta=labels_radar + [labels_radar[0]],
            fill="toself",
            fillcolor="rgba(186,117,23,0.15)",
            line_color=C["amber_dk"],
            name="2024",
        ))
        fig_r.add_trace(go.Scatterpolar(
            r=vals_1972 + [vals_1972[0]],
            theta=labels_radar + [labels_radar[0]],
            fill="toself",
            fillcolor="rgba(55,138,221,0.08)",
            line_color="#378ADD",
            line_dash="dot",
            name="1972 baseline",
        ))
        fig_r.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, range=[0, 100],
                    gridcolor=C["grid"],
                    linecolor=C["grid"],
                    tickfont_color=C["muted"],
                ),
                angularaxis=dict(
                    linecolor=C["grid"],
                    gridcolor=C["grid"],
                ),
                bgcolor="rgba(0,0,0,0)",
            ),
            height=280,
            **PLOTLY_LAYOUT,
        )
        st.plotly_chart(fig_r, use_container_width=True)


# ── TAB 2: τ DASHBOARD ───────────────────────────────────────────────────────
def tab_tau(tau_df: pd.DataFrame):
    st.markdown("### τ = Net Interest / General Fund Revenue")
    st.caption(
        "Fiscal carrying capacity metric. "
        f"**τ\\* = {TAU_STAR:.3f}** (mathematical ceiling) · "
        f"**τ° ≈ {TAU_CALVO_LOW:.2f}–{TAU_CALVO_HIGH:.2f}** (Calvo trigger) · "
        f"**Current τ = {TAU_2024:.3f}** (normalized: 36/100)"
    )

    col_m, col_s = st.columns([3, 1])

    with col_s:
        st.markdown("#### Market Signal Inputs")
        with st.expander("📡 Live Data", expanded=False):
            use_live = st.checkbox("Fetch live TLT/VIX data", value=False)
            if use_live:
                move_val = st.number_input("MOVE index (manual)", 60.0, 200.0, 95.0, 1.0)
                tp_val = st.number_input("10Y term premium % (ACM/FRBNY)", -1.0, 3.0, 0.45, 0.05)
                signals = fetch_live_signals(
                    move_manual=move_val, term_premium_manual=tp_val
                )
            else:
                signals = MarketSignals(signals_available=False)

        st.markdown("##### Manual Entry")
        tlt_now = st.number_input("TLT price (current)", 60.0, 130.0, 87.0, 0.5)
        tlt_90 = st.number_input("TLT price (90d ago)", 60.0, 130.0, 91.0, 0.5)
        tlt_180 = st.number_input("TLT price (180d ago)", 60.0, 130.0, 95.0, 0.5)
        vix_now = st.number_input("VIX level", 8.0, 80.0, 18.0, 0.5)
        corr_val = st.number_input(
            "VIX–TLT 90d correlation",
            -1.0, 1.0, -0.15, 0.05,
            help="Negative = normal safe haven. Positive = warning.",
        )
        move_manual = st.number_input("MOVE index", 50.0, 200.0, 95.0, 1.0)
        tp_manual = st.number_input("Term premium 10Y (%)", -1.0, 3.0, 0.45, 0.05)

        if not signals.signals_available:
            signals = compute_signals_manual(
                tlt_price=tlt_now,
                tlt_price_90d_ago=tlt_90,
                tlt_price_180d_ago=tlt_180,
                vix_level=vix_now,
                vix_tlt_corr_90d=corr_val,
                move_index=move_manual,
                term_premium_10y=tp_manual,
            )

        # Calvo proximity gauge
        prox = signals.calvo_proximity_score
        wlevel = signals.warning_level
        wcolor = {"low": C["safe"], "elevated": C["amber"],
                  "warning": "#F0A500", "critical": C["danger"]}.get(wlevel, C["muted"])

        st.markdown("---")
        st.markdown(f"#### Calvo Proximity Score")
        st.markdown(
            f"<h2 style='color:{wcolor};font-family:monospace;margin:0'>"
            f"{prox:.0f}<span style='font-size:16px;color:{C['muted']}'> / 100</span></h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span style='color:{wcolor};font-size:12px;font-family:monospace'>"
            f"⚠ {wlevel.upper()}</span>",
            unsafe_allow_html=True,
        )

        st.caption(
            f"TLT 90d: {signals.tlt_velocity_90d:+.1%} · "
            f"VIX–TLT corr: {signals.vix_tlt_correlation_90d:+.2f} · "
            f"MOVE: {signals.move_index:.0f}"
        )

    with col_m:
        fig_tau = styled_fig()
        years = tau_df["year"].tolist()
        tau_raw = tau_df["tau_raw"].tolist()

        # Color bars by level
        bar_colors = []
        for v in tau_raw:
            if v >= TAU_CALVO_LOW:
                bar_colors.append(C["danger"])
            elif v >= 0.25:
                bar_colors.append(C["amber"])
            else:
                bar_colors.append("rgba(110,201,196,0.6)")

        fig_tau.add_trace(go.Bar(
            x=years, y=tau_raw,
            marker_color=bar_colors,
            name="τ (raw)",
            hovertemplate="Year: %{x}<br>τ = %{y:.3f}<extra></extra>",
        ))

        # Reference lines
        fig_tau.add_hline(
            y=TAU_CALVO_LOW, line_dash="dash", line_color=C["amber"], line_width=1.5,
            annotation_text=f"τ° lower bound ({TAU_CALVO_LOW:.2f})",
            annotation_font_color=C["amber"], annotation_font_size=9,
        )
        fig_tau.add_hline(
            y=TAU_CALVO_HIGH, line_dash="dot", line_color=C["amber"], line_width=1,
            annotation_text=f"τ° upper bound ({TAU_CALVO_HIGH:.2f})",
            annotation_font_color=C["amber"], annotation_font_size=9,
        )
        fig_tau.add_hline(
            y=TAU_STAR, line_dash="dash", line_color=C["danger"], line_width=1.5,
            annotation_text=f"τ* ceiling ({TAU_STAR:.3f})",
            annotation_font_color=C["danger"], annotation_font_size=9,
        )

        # Current value annotation
        fig_tau.add_trace(go.Scatter(
            x=[2024], y=[TAU_2024],
            mode="markers+text",
            marker=dict(color="#6EC9C4", size=10),
            text=[f"  τ={TAU_2024:.3f}"],
            textfont=dict(color="#6EC9C4", size=10),
            name="2024",
            showlegend=False,
        ))

        fig_tau.update_layout(
            title="Fiscal Stress τ — Historical Series 1972–2024",
            yaxis_title="τ = Net Interest / General Fund Revenue",
            yaxis_range=[0, 0.85],
            height=350,
            **PLOTLY_LAYOUT,
        )
        st.plotly_chart(fig_tau, use_container_width=True)

        # Signal summary table
        st.markdown("##### Market Signal Summary")
        sig_data = {
            "Signal": [
                "TLT 90-day velocity",
                "TLT acceleration",
                "VIX–TLT correlation",
                "MOVE index",
                "VIX level",
                "Term premium (10Y)",
            ],
            "Value": [
                f"{signals.tlt_velocity_90d:+.2%}",
                f"{signals.tlt_acceleration:+.4f}",
                f"{signals.vix_tlt_correlation_90d:+.3f}",
                f"{signals.move_index:.1f}",
                f"{signals.vix_level:.1f}",
                f"{signals.term_premium_10y:+.2f}%",
            ],
            "Status": [
                "⚠ Watch" if signals.tlt_velocity_90d < -0.02 else "✓ OK",
                "⚠ Watch" if signals.tlt_acceleration < -0.005 else "✓ OK",
                "🔴 Critical" if signals.vix_tlt_correlation_90d > 0.25
                else "⚠ Warning" if signals.vix_tlt_correlation_90d > 0
                else "✓ Normal",
                "⚠ Elevated" if signals.move_index > 110 else "✓ Normal",
                "⚠ Elevated" if signals.vix_level > 25 else "✓ Normal",
                "⚠ Elevated" if signals.term_premium_10y > 0.75 else "✓ Normal",
            ],
        }
        st.dataframe(
            pd.DataFrame(sig_data),
            hide_index=True,
            use_container_width=True,
        )


# ── TAB 3: MONTE CARLO PROJECTIONS ───────────────────────────────────────────
def tab_projections(weights: Dict[str, float]):
    st.markdown("### Monte Carlo Forward Projections — Zone of Reduced Efficacy")
    st.caption(
        "Probability distributions over plausible trajectories. "
        "Not point predictions. Shaded bands show 10th–90th percentile range."
    )

    col_ctrl, _ = st.columns([2, 3])
    with col_ctrl:
        run_cols = st.columns(3)
        with run_cols[0]:
            scenario = st.selectbox(
                "Scenario",
                options=list(SCENARIOS.keys()),
                format_func=lambda k: SCENARIOS[k]["label"].split("—")[0].strip(),
            )
        with run_cols[1]:
            n_runs = st.selectbox("Simulation runs", [1_000, 10_000, 50_000], index=1)
        with run_cols[2]:
            horizon = st.selectbox("Horizon", [2035, 2040, 2045, 2050], index=1)

        run_btn = st.button(
            f"▶  Run {n_runs:,} simulations",
            type="primary",
            use_container_width=True,
        )

    if run_btn or "mc_results" not in st.session_state:
        with st.spinner(f"Running {n_runs:,} Monte Carlo simulations…"):
            results = run_monte_carlo(
                weights=weights,
                scenario=scenario,
                n_runs=n_runs,
                horizon=horizon,
            )
        st.session_state["mc_results"] = results
        st.session_state["mc_scenario"] = scenario

    results = st.session_state.get("mc_results")
    if results is None:
        st.info("Press **Run simulations** to generate projections.")
        return

    years = results.years.tolist()
    scen_color = SCENARIOS[results.scenario]["color"]

    # Composite projection chart
    fig_proj = styled_fig()

    # Historical composite for context (equal weight)
    df, _ = get_data()
    hist_comp = compute_composite(df, weights)
    fig_proj.add_trace(go.Scatter(
        x=df["year"].tolist(), y=hist_comp.tolist(),
        name="Historical",
        line=dict(color=C["amber_dk"], width=2),
        mode="lines",
    ))

    # Percentile band shading
    pct_labels = ["10th", "25th", "50th (median)", "75th", "90th"]
    pct_rows = [0, 1, 2, 3, 4]

    # Fill 10-90 band
    fig_proj.add_trace(go.Scatter(
        x=years + years[::-1],
        y=results.composite_pct[0].tolist() + results.composite_pct[4].tolist()[::-1],
        fill="toself",
        fillcolor=f"rgba{tuple(int(scen_color.lstrip('#')[i:i+2], 16) for i in (0,2,4)) + (0.12,)}",
        line_color="rgba(0,0,0,0)",
        name="10–90th pct band",
        showlegend=True,
    ))

    # Fill 25-75 band
    fig_proj.add_trace(go.Scatter(
        x=years + years[::-1],
        y=results.composite_pct[1].tolist() + results.composite_pct[3].tolist()[::-1],
        fill="toself",
        fillcolor=f"rgba{tuple(int(scen_color.lstrip('#')[i:i+2], 16) for i in (0,2,4)) + (0.22,)}",
        line_color="rgba(0,0,0,0)",
        name="25–75th pct band",
        showlegend=True,
    ))

    # Median line
    fig_proj.add_trace(go.Scatter(
        x=years, y=results.composite_pct[2].tolist(),
        name=f"Median — {SCENARIOS[results.scenario]['label'].split('—')[0]}",
        line=dict(color=scen_color, width=2.5),
        mode="lines",
    ))

    # Zone of Reduced Efficacy
    fig_proj.add_hrect(
        y0=60, y1=100,
        fillcolor="rgba(226,75,74,0.06)",
        line_width=0,
        annotation_text="Zone of Reduced Efficacy",
        annotation_position="top left",
        annotation_font_color=C["danger"],
        annotation_font_size=9,
    )

    fig_proj.update_layout(
        title=f"NFI Composite Projection — {SCENARIOS[results.scenario]['label']}",
        xaxis_title="Year",
        yaxis_title="Composite NFI Score",
        yaxis_range=[0, 100],
        height=360,
        **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig_proj, use_container_width=True)

    # Probability metrics
    st.markdown("#### Threshold Crossing Probabilities")
    metric_cols = st.columns(len(results.calvo_crossing_probs))
    for i, (yr, prob) in enumerate(sorted(results.calvo_crossing_probs.items())):
        with metric_cols[i]:
            color = C["danger"] if prob > 0.5 else C["amber"] if prob > 0.25 else C["safe"]
            st.markdown(
                f"**P(τ > τ°) by {yr}**\n\n"
                f"<h3 style='color:{color};font-family:monospace;margin:0'>"
                f"{prob:.0%}</h3>",
                unsafe_allow_html=True,
            )

    # Monte Carlo stats
    st.markdown("---")
    info_cols = st.columns(4)
    with info_cols[0]:
        st.metric("Simulation runs", f"{results.n_runs:,}")
    with info_cols[1]:
        st.metric("Calvo events", f"{results.n_calvo_events:,}",
                  delta=f"{results.n_calvo_events/results.n_runs:.1%} of runs",
                  delta_color="inverse")
    with info_cols[2]:
        median_2040_idx = min(horizon - 2024, len(years) - 1)
        st.metric(f"Median NFI {horizon}",
                  f"{results.composite_pct[2, median_2040_idx]:.1f}")
    with info_cols[3]:
        band_width = (results.composite_pct[4, median_2040_idx] -
                      results.composite_pct[0, median_2040_idx])
        st.metric("10–90th band width", f"±{band_width/2:.1f} pts",
                  help="Width of uncertainty envelope at projection horizon")

    # τ projection chart
    st.markdown("#### τ Forward Trajectory")
    fig_tau_proj = styled_fig()

    fig_tau_proj.add_trace(go.Scatter(
        x=years + years[::-1],
        y=results.tau_pct[0].tolist() + results.tau_pct[4].tolist()[::-1],
        fill="toself",
        fillcolor="rgba(110,201,196,0.10)",
        line_color="rgba(0,0,0,0)",
        name="τ 10–90th band",
    ))
    fig_tau_proj.add_trace(go.Scatter(
        x=years, y=results.tau_pct[2].tolist(),
        name="τ median (normalized)",
        line=dict(color="#6EC9C4", width=2),
    ))

    # τ thresholds (normalized)
    tau_low_norm = (TAU_CALVO_LOW / TAU_STAR) * 100
    tau_high_norm = (TAU_CALVO_HIGH / TAU_STAR) * 100
    tau_star_norm = 100.0

    fig_tau_proj.add_hline(
        y=tau_low_norm, line_dash="dash", line_color=C["amber"], line_width=1.5,
        annotation_text=f"τ° lower ({TAU_CALVO_LOW:.2f})",
        annotation_font_color=C["amber"], annotation_font_size=9,
    )
    fig_tau_proj.add_hline(
        y=tau_high_norm, line_dash="dot", line_color=C["amber"], line_width=1,
        annotation_text=f"τ° upper ({TAU_CALVO_HIGH:.2f})",
        annotation_font_color=C["amber"], annotation_font_size=9,
    )

    fig_tau_proj.update_layout(
        xaxis_title="Year",
        yaxis_title="τ Normalized (0–100)",
        yaxis_range=[0, 85],
        height=260,
        **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig_tau_proj, use_container_width=True)


# ── TAB 4: SCENARIO COMPARISON ───────────────────────────────────────────────
def tab_scenarios(weights: Dict[str, float]):
    st.markdown("### Scenario Comparison")
    st.caption(
        "Three structural scenarios compared across the same weight configuration. "
        "Median trajectories shown. Click **Run All Scenarios** to compute."
    )

    horizon = st.selectbox("Horizon", [2035, 2040, 2050], index=1, key="scen_horizon")
    n_runs_scen = st.selectbox("Runs per scenario", [1_000, 5_000], index=0, key="scen_runs")

    if st.button("▶  Run All Scenarios", type="primary"):
        all_results = {}
        for scen_key in SCENARIOS:
            with st.spinner(f"Running {scen_key}…"):
                all_results[scen_key] = run_monte_carlo(
                    weights=weights,
                    scenario=scen_key,
                    n_runs=n_runs_scen,
                    horizon=horizon,
                    seed=42,
                )
        st.session_state["scen_results"] = all_results

    if "scen_results" not in st.session_state:
        st.info("Press **Run All Scenarios** to compare trajectories.")
        return

    all_results = st.session_state["scen_results"]

    # Composite comparison
    fig_comp = styled_fig()
    df, _ = get_data()
    hist_comp = compute_composite(df, weights)
    fig_comp.add_trace(go.Scatter(
        x=df["year"].tolist(), y=hist_comp.tolist(),
        name="Historical", line=dict(color=C["muted"], width=1.5, dash="dot"),
    ))

    for scen_key, res in all_results.items():
        c = SCENARIOS[scen_key]["color"]
        years = res.years.tolist()
        # Band
        fig_comp.add_trace(go.Scatter(
            x=years + years[::-1],
            y=res.composite_pct[1].tolist() + res.composite_pct[3].tolist()[::-1],
            fill="toself",
            fillcolor=f"rgba{tuple(int(c.lstrip('#')[i:i+2], 16) for i in (0,2,4)) + (0.12,)}",
            line_color="rgba(0,0,0,0)",
            showlegend=False,
        ))
        # Median
        fig_comp.add_trace(go.Scatter(
            x=years, y=res.composite_pct[2].tolist(),
            name=SCENARIOS[scen_key]["label"].split("—")[0].strip(),
            line=dict(color=c, width=2.5),
        ))

    fig_comp.add_hrect(
        y0=60, y1=100, fillcolor="rgba(226,75,74,0.06)", line_width=0,
    )
    fig_comp.update_layout(
        title="Composite NFI — Scenario Comparison (Median ± IQR)",
        yaxis_range=[0, 100], height=340, **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # Probability table
    st.markdown("#### P(τ > τ°) by Scenario and Year")
    prob_rows = []
    for scen_key, res in all_results.items():
        row = {"Scenario": SCENARIOS[scen_key]["label"].split("—")[0].strip()}
        for yr, prob in sorted(res.calvo_crossing_probs.items()):
            row[str(yr)] = f"{prob:.0%}"
        row["Calvo Events"] = f"{res.n_calvo_events:,} / {res.n_runs:,}"
        prob_rows.append(row)
    st.dataframe(pd.DataFrame(prob_rows), hide_index=True, use_container_width=True)


# ── TAB 5: METHODOLOGY ───────────────────────────────────────────────────────
def tab_methodology():
    st.markdown("### NFI R1 — Analytical Framework")

    with st.expander("📖 What This Model Is — and Is NOT", expanded=True):
        st.markdown("""
**The NFI R1 is an analytical instrument, not a validated predictive model.**

It produces *Zone of Reduced Efficacy* projections — probability distributions
over plausible system trajectories given current observed conditions and the
conditional dependency structure encoded in the Bayesian network.

It **does not** predict specific events, specific dates, or precise outcomes.
It **does** provide a structured probabilistic framework for reasoning about
the direction, acceleration, and interaction of social, institutional, and
fiscal fracture dynamics in the United States.

The appropriate use is: *"Given current conditions, what range of futures
is structurally plausible over what time horizon?"* — not: *"When will X happen?"*
        """)

    with st.expander("📚 Theoretical Foundations"):
        frameworks = [
            ("Rodgers — Age of Fracture (2011)",
             "The dissolution of collective conceptual vocabulary beginning ~1974. "
             "Operationalized as Cultural Solidarity dimension."),
            ("Acemoglu & Robinson — Why Nations Fail (2012)",
             "Inclusive vs. extractive institutional dynamics; the vicious circle "
             "of extraction. Operationalized as Institutional Capture dimension."),
            ("Piketty — Capital in the 21st Century (2013)",
             "r > g capital concentration as the structural driver of inequality "
             "and political capture. Income Inequality dimension uses top wealth "
             "concentration (Saez-Zucman) rather than Gini alone."),
            ("Becker — Denial of Death (1973) / Terror Management Theory",
             "Immortality projects as political identity; mortality salience "
             "→ identity-protective cognition. Models the Becker-Bonhoeffer "
             "condition as a Political Responsiveness floor."),
            ("Bonhoeffer — Sociological Stupidity Condition",
             "The distinction between individual and socially-induced "
             "epistemic closure. Liberation requires structural change, "
             "not persuasion. Informs forecasting horizon assumptions."),
            ("Club of Rome — Limits to Growth (1972)",
             "Zone-based trajectory forecasting rather than point prediction. "
             "System overshoot dynamics. NFI output framing follows this precedent."),
            ("Turchin — Structural-Demographic Theory",
             "Elite overproduction, popular immiseration cycles, instability "
             "index. Informs Elite Misalignment dimension and cycle timing."),
        ]
        for title, desc in frameworks:
            st.markdown(f"**{title}**\n\n{desc}\n\n---")

    with st.expander("⚙️ Model Architecture"):
        st.markdown("""
**11 Dimensions** (0–100 scale, higher = more fracture/stress):
Equal weighting default; user-adjustable via sidebar.

**Dynamic Bayesian Network**: Conditional dependency structure
encoding theoretical feedback loops. Time-step unrolling handles
cyclic dependencies. Full pgmpy inference optional; MC approximation
available for all users.

**Monte Carlo Simulation**: 10,000 runs default; 50,000 extended.
Annual time steps from 2024 to selected horizon.
Outputs: percentile envelopes (10th–90th), P(τ > τ°), zone exit probs.

**τ Function**: Net Interest / General Fund Revenue.
τ\\* = 0.769 (mathematical ceiling). τ° ≈ 0.38–0.45 (Calvo trigger).
Dynamic: effective τ° decreases as NFI social composite rises.

**Market Signal Layer**: TLT velocity/acceleration, VIX–TLT rolling
correlation (primary discontinuity indicator), MOVE index, term premium.
Real-time conditioning variables for τ forward trajectory.
        """)

    with st.expander("⚠️ Limitations"):
        st.markdown("""
- **Data scarcity**: n=14 observations (4-year intervals, 1972–2024).
  CPT estimation is statistically underdetermined. Results are
  indicative probability ranges, not precise estimates.
- **Non-stationarity**: Conditional relationships may change over time.
  Citizens United (2010) treated as structural break; others may exist.
- **False correlation risk**: Multiple upward-trending series in a
  50-year time window create spurious correlation hazards.
  Weight sensitivity analysis is the primary mitigation.
- **Single country**: No cross-national validation in R1.
  Planned for R2 (V-Dem dataset integration).
- **Forecasting horizon**: Complex social systems resist precise
  long-horizon prediction. The 2040 horizon should be treated as
  indicative of trajectory, not specific outcomes.
        """)


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    df, tau_df = get_data()
    weights = build_sidebar()

    # Header
    composite_2024 = float(compute_composite(df, weights).iloc[-1])
    st.markdown(
        f"<h1 style='margin-bottom:0;font-family:IBM Plex Mono,monospace;"
        f"font-size:24px;font-weight:500'>National Fracture Index"
        f"<span style='color:{C['muted']};font-size:14px;margin-left:12px'>"
        f"R1 · United States · 1972–2024 · 11-Dimension Model</span></h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-family:monospace;font-size:11px;color:{C['muted']};margin-bottom:16px'>"
        f"Analytical instrument — not a validated predictive model · "
        f"Zone of Reduced Efficacy projections · "
        f"<span style='color:{C['amber']}'>"
        f"Current composite: {composite_2024:.0f} / 100</span></div>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "💹 τ Dashboard",
        "🎲 Projections",
        "🔀 Scenarios",
        "📖 Methodology",
    ])

    with tab1:
        tab_overview(df, weights)
    with tab2:
        tab_tau(tau_df)
    with tab3:
        tab_projections(weights)
    with tab4:
        tab_scenarios(weights)
    with tab5:
        tab_methodology()

    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='font-family:monospace;font-size:10px;color:{C['muted']}'>"
        f"NFI R1 · Analytical instrument only · Not a validated predictive model · "
        f"For research and analytical purposes · "
        f"Theoretical foundations: Rodgers · Acemoglu & Robinson · Piketty · "
        f"Becker · Bonhoeffer · Club of Rome · Turchin</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
