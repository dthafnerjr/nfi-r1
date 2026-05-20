"""
market_signals.py — NFI R1 Market Signal Integration Layer
===========================================================
Purpose:
    Processes real-time market data (TLT, VIX, MOVE) to compute
    Calvo proximity indicators and update τ forward trajectory
    conditioning variables. Provides the real-time market signal
    overlay for the τ dashboard.

Dependencies:
    numpy, pandas, yfinance (optional — degrades gracefully)

Key Assumptions:
    See ASSUMPTIONS dict below.

Changelog:
    R1.0 (2026): Initial implementation. yfinance integration.
                 Manual override inputs for offline use.
                 ACM term premium requires manual input (FRBNY data).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

# ── ASSUMPTIONS ─────────────────────────────────────────────────────────────
MARKET_ASSUMPTIONS: Dict[str, str] = {
    "tlt_proxy": (
        "TLT (iShares 20+ Year Treasury Bond ETF) used as proxy for "
        "20-year Treasury yield dynamics. TLT price moves inversely "
        "to yields. Falling TLT = rising long-duration yields = "
        "higher future τ. See METHODOLOGY §4.4."
    ),
    "vix_tlt_correlation": (
        "Rolling 90-day correlation between daily VIX changes and TLT "
        "returns. Normal: negative (safe haven bid). Warning: near zero. "
        "Critical: positive (Treasury losing safe haven status). "
        "Correlation inversion is the primary Calvo proximity signal. "
        "See METHODOLOGY §4.4."
    ),
    "move_index": (
        "MOVE index (Merrill Lynch Option Volatility Estimate) measures "
        "Treasury options implied volatility — the bond market's VIX. "
        "Elevated MOVE + elevated VIX simultaneously signals dual "
        "market stress preceding Calvo-type discontinuity. "
        "See METHODOLOGY §4.4."
    ),
    "acceleration_signal": (
        "Second derivative of TLT price (rate of change of yield velocity) "
        "is the critical warning signal. Accelerating TLT decline indicates "
        "self-reinforcing dynamic beginning to engage — Calvo approach. "
        "See METHODOLOGY §4.4."
    ),
    "term_premium": (
        "ACM term premium decomposition (FRBNY) separates yield movements "
        "into rate-expectations and risk-premium components. Rising term "
        "premium with stable rate expectations = fiscal risk pricing = "
        "direct Calvo proximity indicator. Manual input required. "
        "Source: https://www.newyorkfed.org/research/data_indicators/term_premia"
    ),
}

# ── SIGNAL THRESHOLDS ────────────────────────────────────────────────────────
THRESHOLDS = {
    "vix_tlt_corr_warning":  0.0,   # Correlation above zero = warning
    "vix_tlt_corr_critical": 0.25,  # Strong positive = critical
    "tlt_velocity_warning":  -0.02, # 90-day return below -2%
    "tlt_accel_warning":     -0.005,# Acceleration below threshold
    "move_warning":           110,  # MOVE > 110 = elevated bond vol
    "move_critical":          140,  # MOVE > 140 = severe bond stress
    "vix_warning":            25,   # VIX > 25 = elevated equity stress
    "vix_critical":           35,   # VIX > 35 = severe equity stress
}

# ── SIGNAL DATACLASS ─────────────────────────────────────────────────────────
@dataclass
class MarketSignals:
    """
    Container for current market signal readings.

    Attributes
    ----------
    tlt_price : float
        Current TLT closing price.
    tlt_velocity_90d : float
        TLT 90-day return (1st derivative proxy).
    tlt_acceleration : float
        Rate of change of 90-day TLT return (2nd derivative proxy).
    vix_level : float
        Current VIX index level.
    vix_tlt_correlation_90d : float
        Rolling 90-day correlation between VIX changes and TLT returns.
    move_index : float
        Current MOVE index level (manual input).
    term_premium_10y : float
        10-year ACM term premium (manual input, from FRBNY).
    dxy_trend : float
        DXY 90-day return (dollar trend).
    calvo_proximity_score : float
        Composite Calvo proximity score 0-100.
    warning_level : str
        'low', 'elevated', 'warning', or 'critical'.
    signals_available : bool
        False if live data unavailable (offline mode).
    data_date : str
        Date of most recent data point.
    """
    tlt_price: float = 0.0
    tlt_velocity_90d: float = 0.0
    tlt_acceleration: float = 0.0
    vix_level: float = 0.0
    vix_tlt_correlation_90d: float = 0.0
    move_index: float = 0.0
    term_premium_10y: float = 0.0
    dxy_trend: float = 0.0
    calvo_proximity_score: float = 0.0
    warning_level: str = "low"
    signals_available: bool = False
    data_date: str = "N/A"


def fetch_live_signals(
    move_manual: float = 95.0,
    term_premium_manual: float = 0.45,
    period: str = "1y",
) -> MarketSignals:
    """
    Fetch live market signals from yfinance.

    Parameters
    ----------
    move_manual : float
        MOVE index level (not available via yfinance, manual entry).
        Default: 95.0 (approximate recent level).
    term_premium_manual : float
        10-year ACM term premium (manual from FRBNY).
        Default: 0.45%.
    period : str
        Data history period for rolling calculations. Default: '1y'.

    Returns
    -------
    MarketSignals
        Populated signal container.
        If yfinance unavailable, returns signals_available=False
        with zero values.

    Notes
    -----
    Requires: pip install yfinance
    MOVE index: manual entry required. Source: Bloomberg or
                https://www.ice.com/marketdata/reports/170
    ACM term premium: manual from
                https://www.newyorkfed.org/research/data_indicators/term_premia
    """
    try:
        import yfinance as yf

        tlt = yf.download("TLT", period=period, interval="1d",
                          progress=False, auto_adjust=True)
        vix = yf.download("^VIX", period=period, interval="1d",
                          progress=False, auto_adjust=True)
        dxy = yf.download("DX-Y.NYB", period=period, interval="1d",
                          progress=False, auto_adjust=True)

        if tlt.empty or vix.empty:
            return MarketSignals(signals_available=False)

        # Align on common dates
        tlt_close = tlt["Close"].dropna()
        vix_close = vix["Close"].dropna()

        common_idx = tlt_close.index.intersection(vix_close.index)
        tlt_close = tlt_close.loc[common_idx]
        vix_close = vix_close.loc[common_idx]

        # Compute signals
        tlt_ret_90 = tlt_close.pct_change(90).dropna()
        tlt_vel_current = float(tlt_ret_90.iloc[-1]) if len(tlt_ret_90) > 0 else 0.0
        tlt_accel = float(tlt_ret_90.diff().iloc[-1]) if len(tlt_ret_90) > 1 else 0.0

        vix_chg = vix_close.pct_change().dropna()
        tlt_chg = tlt_close.pct_change().dropna()
        common2 = vix_chg.index.intersection(tlt_chg.index)

        if len(common2) >= 90:
            vix_tlt_corr = float(
                vix_chg.loc[common2].rolling(90).corr(tlt_chg.loc[common2]).iloc[-1]
            )
        else:
            vix_tlt_corr = -0.3  # default negative correlation assumption

        dxy_close = dxy["Close"].dropna() if not dxy.empty else pd.Series()
        dxy_trend = (
            float(dxy_close.pct_change(90).iloc[-1])
            if len(dxy_close) >= 90 else 0.0
        )

        tlt_price = float(tlt_close.iloc[-1])
        vix_level = float(vix_close.iloc[-1])
        data_date = str(tlt_close.index[-1].date())

        # Compute composite Calvo proximity
        proximity = _compute_calvo_proximity_score(
            tlt_velocity=tlt_vel_current,
            tlt_acceleration=tlt_accel,
            vix_tlt_corr=vix_tlt_corr,
            move=move_manual,
            vix=vix_level,
            term_premium=term_premium_manual,
        )

        warning = _classify_warning_level(proximity)

        return MarketSignals(
            tlt_price=tlt_price,
            tlt_velocity_90d=tlt_vel_current,
            tlt_acceleration=tlt_accel,
            vix_level=vix_level,
            vix_tlt_correlation_90d=vix_tlt_corr,
            move_index=move_manual,
            term_premium_10y=term_premium_manual,
            dxy_trend=dxy_trend,
            calvo_proximity_score=proximity,
            warning_level=warning,
            signals_available=True,
            data_date=data_date,
        )

    except Exception:
        return MarketSignals(signals_available=False)


def compute_signals_manual(
    tlt_price: float,
    tlt_price_90d_ago: float,
    tlt_price_180d_ago: float,
    vix_level: float,
    vix_tlt_corr_90d: float,
    move_index: float,
    term_premium_10y: float,
    dxy_90d_change_pct: float = 0.0,
) -> MarketSignals:
    """
    Compute market signals from manually entered values.

    Use when live data feed is unavailable or for scenario testing.

    Parameters
    ----------
    tlt_price : float
        Current TLT price.
    tlt_price_90d_ago : float
        TLT price 90 trading days ago.
    tlt_price_180d_ago : float
        TLT price 180 trading days ago (for acceleration).
    vix_level : float
        Current VIX level.
    vix_tlt_corr_90d : float
        Rolling 90-day VIX-TLT return correlation.
        Negative = normal. Zero or positive = warning.
    move_index : float
        Current MOVE index level.
    term_premium_10y : float
        10-year ACM term premium (%).
    dxy_90d_change_pct : float
        DXY 90-day percentage change. Default: 0.

    Returns
    -------
    MarketSignals
    """
    tlt_vel = (tlt_price - tlt_price_90d_ago) / tlt_price_90d_ago
    tlt_vel_prior = (tlt_price_90d_ago - tlt_price_180d_ago) / tlt_price_180d_ago
    tlt_accel = tlt_vel - tlt_vel_prior

    proximity = _compute_calvo_proximity_score(
        tlt_velocity=tlt_vel,
        tlt_acceleration=tlt_accel,
        vix_tlt_corr=vix_tlt_corr_90d,
        move=move_index,
        vix=vix_level,
        term_premium=term_premium_10y,
    )
    warning = _classify_warning_level(proximity)

    return MarketSignals(
        tlt_price=tlt_price,
        tlt_velocity_90d=tlt_vel,
        tlt_acceleration=tlt_accel,
        vix_level=vix_level,
        vix_tlt_correlation_90d=vix_tlt_corr_90d,
        move_index=move_index,
        term_premium_10y=term_premium_10y,
        dxy_trend=dxy_90d_change_pct / 100,
        calvo_proximity_score=proximity,
        warning_level=warning,
        signals_available=True,
        data_date="Manual entry",
    )


def _compute_calvo_proximity_score(
    tlt_velocity: float,
    tlt_acceleration: float,
    vix_tlt_corr: float,
    move: float,
    vix: float,
    term_premium: float,
) -> float:
    """
    Compute composite Calvo proximity score (0-100).

    Weights five independent signal components:
    1. TLT velocity (direction of yield movement)
    2. TLT acceleration (self-reinforcing dynamic)
    3. VIX-TLT correlation (safe haven breakdown — primary signal)
    4. Bond/equity dual stress (MOVE + VIX elevated simultaneously)
    5. Term premium level (fiscal risk premium in bond pricing)

    Returns
    -------
    float
        Score 0-100. See THRESHOLDS for interpretation.
    """
    scores = []

    # 1. TLT velocity: falling TLT = rising yields = τ pressure
    vel_score = np.clip((-tlt_velocity) * 300, 0, 100)
    scores.append(vel_score * 0.20)

    # 2. TLT acceleration (negative acceleration = accelerating yield rise)
    accel_score = np.clip((-tlt_acceleration) * 5000, 0, 100)
    scores.append(accel_score * 0.25)

    # 3. VIX-TLT correlation (primary signal — correlation inversion)
    corr_score = np.clip((vix_tlt_corr + 0.4) / 0.9 * 100, 0, 100)
    scores.append(corr_score * 0.30)

    # 4. Dual stress: MOVE and VIX both elevated
    move_score = np.clip((move - 80) / 80 * 100, 0, 100)
    vix_score = np.clip((vix - 15) / 45 * 100, 0, 100)
    dual_score = (move_score + vix_score) / 2
    scores.append(dual_score * 0.15)

    # 5. Term premium (positive = fiscal risk pricing)
    tp_score = np.clip((term_premium - 0.0) / 1.5 * 100, 0, 100)
    scores.append(tp_score * 0.10)

    return round(min(sum(scores), 100), 1)


def _classify_warning_level(proximity_score: float) -> str:
    """Classify proximity score into warning level."""
    if proximity_score < 25:
        return "low"
    elif proximity_score < 50:
        return "elevated"
    elif proximity_score < 72:
        return "warning"
    else:
        return "critical"
