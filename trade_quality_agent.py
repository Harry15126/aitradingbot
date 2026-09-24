"""
Trade Quality Agent
Calculates a weighted score for a potential trade based on institutional SMC and quantitative confluence.
"""

def calculate_trade_quality(criteria):
    """
    Evaluates the quality of a trade setup using a weighted scoring system.

    Expected criteria keys:
    - market_structure: { "signal": str, "bos": bool, "choch": bool, "sweep": bool }
    - fvg: { "detected": bool, "strength": str }
    - currency_strength_diff: float
    - ema_distance_pips: float
    - session_quality: str (e.g., "High", "Medium", "Low")
    - news_risk: bool
    - volatility_atr: float (Current ATR)
    - avg_atr: float (Baseline ATR for comparison)
    """

    score = 0
    reasons = []

    # --- 1. Market Structure Weighting (Max 45 pts) ---
    ms = criteria.get("market_structure", {})
    ms_signal = ms.get("signal", "Neutral")

    if ms_signal != "Neutral":
        score += 15
        reasons.append(f"Market structure is aligned ({ms_signal})")

    if ms.get("sweep"):
        score += 15
        reasons.append("Liquidity sweep detected (High Probability)")

    if ms.get("choch"):
        score += 15
        reasons.append("Market Structure Shift (CHOCH) confirmed")
    elif ms.get("bos"):
        score += 5
        reasons.append("Break of Structure (BOS) confirmed")

    # --- 2. FVG / Imbalance Weighting (Max 20 pts) ---
    fvg = criteria.get("fvg", {})
    if fvg.get("detected"):
        score += 10
        reasons.append("Fair Value Gap (FVG) detected as entry zone")
        if fvg.get("strength") == "Strong":
            score += 10
            reasons.append("FVG shows strong impulsive movement")

    # --- 3. Currency Strength Weighting (Max 15 pts) ---
    strength_diff = criteria.get("currency_strength_diff", 0)
    if strength_diff > 3.0:
        score += 15
        reasons.append(f"Extremely strong currency divergence ({strength_diff:.2f})")
    elif strength_diff > 1.5:
        score += 10
        reasons.append(f"Strong currency divergence ({strength_diff:.2f})")
    elif strength_diff > 0.5:
        score += 5
        reasons.append(f"Moderate currency divergence ({strength_diff:.2f})")

    # --- 4. EMA Alignment (Max 10 pts) ---
    # Ideal distance from 200 EMA is 10-50 pips (not too far, not too close)
    ema_dist = criteria.get("ema_distance_pips", 0)
    if 10 <= ema_dist <= 50:
        score += 10
        reasons.append("Price is at an ideal distance from 200 EMA (Good RR)")
    elif ema_dist > 60:
        score -= 10
        reasons.append("Price is over-extended from 200 EMA (Bad RR)")

    # --- 5. Session & Volatility (Max 10 pts) ---
    session = criteria.get("session_quality", "Low")
    if session == "High":
        score += 5
        reasons.append("High quality trading session (London/NY)")

    atr = criteria.get("volatility_atr", 0)
    avg_atr = criteria.get("avg_atr", 1) # Prevent div by zero
    if avg_atr > 0:
        vol_ratio = atr / avg_atr
        if 0.8 <= vol_ratio <= 1.5:
            score += 5
            reasons.append("Volatility is within optimal range")
        elif vol_ratio > 2.0:
            score -= 10
            reasons.append("Market is hyper-volatile (High Risk)")

    # --- CRITICAL FILTERS (Multipliers/Penalties) ---

    # News Risk is a dealbreaker
    if criteria.get("news_risk", False):
        score = 0
        reasons.insert(0, "CRITICAL: High impact news event imminent. Trade quality invalidated.")

    # Cap score at 100 and floor at 0
    final_score = max(0, min(100, score))

    # Grade assignment
    if final_score >= 80:
        grade = "A"
        quality = "Excellent"
    elif final_score >= 65:
        grade = "B"
        quality = "Good"
    elif final_score >= 50:
        grade = "C"
        quality = "Average"
    else:
        grade = "D"
        quality = "Poor"

    return {
        "score": final_score,
        "grade": grade,
        "trade_quality": quality,
        "reasons": reasons
    }
