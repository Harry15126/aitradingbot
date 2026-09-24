def calculate_confidence(result, risk_plan, session_name):
    score = 0
    reasons = []

    # 1. Bias check
    if result["bias"] in ["BUY ONLY", "SELL ONLY"]:
        score += 25
        reasons.append("Clear directional bias")
    else:
        reasons.append("No clear directional bias")

    # 2. Trend check
    if result["trend"] in ["Bullish", "Bearish"]:
        score += 20
        reasons.append("Trend is clear")
    else:
        reasons.append("Trend is neutral")

    # 3. RSI check
    rsi = result["rsi"]

    if 40 <= rsi <= 60:
        score += 20
        reasons.append("RSI is healthy/neutral")
    elif 30 <= rsi < 40 or 60 < rsi <= 70:
        score += 10
        reasons.append("RSI is acceptable")
    else:
        reasons.append("RSI is overextended")

    # 4. Stop loss quality
    if risk_plan and risk_plan["stop_loss_quality"].startswith("GOOD"):
        score += 20
        reasons.append("Stop loss distance is acceptable")
    else:
        reasons.append("Stop loss distance is not acceptable")

    # 5. Session quality
    if session_name in ["London Session", "London/New York Overlap", "New York Session"]:
        score += 15
        reasons.append("Good trading session")
    else:
        reasons.append("Lower-quality session")

    if score >= 85:
        level = "Very High"
    elif score >= 75:
        level = "High"
    elif score >= 60:
        level = "Medium"
    else:
        level = "Low"

    trade_allowed_by_confidence = score >= 75

    return {
        "confidence_score": score,
        "confidence_level": level,
        "trade_allowed_by_confidence": trade_allowed_by_confidence,
        "reasons": reasons
    }