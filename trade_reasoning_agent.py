def generate_trade_reasoning(result,
                              confidence,
                              risk_plan,
                              final_trade_allowed,
                              multi_tf_confirmation,
                              session_name):

    reasons = []

    if result["bias"] == "WAIT":
        reasons.append(
            "No directional bias detected."
        )

    else:
        reasons.append(
            f"Bias detected: {result['bias']}"
        )

    if multi_tf_confirmation == "Confirmed":
        reasons.append(
            "15m and 1H trends are aligned."
        )

    else:
        reasons.append(
            "Multi-timeframe trends are mixed."
        )

    if result["rsi"] > 70:
        reasons.append(
            "RSI indicates overbought conditions."
        )

    elif result["rsi"] < 30:
        reasons.append(
            "RSI indicates oversold conditions."
        )

    else:
        reasons.append(
            "RSI conditions acceptable."
        )

    if risk_plan:

        reasons.append(
            f"Stop-loss quality: "
            f"{risk_plan['stop_loss_quality']}"
        )

    if confidence["confidence_score"] >= 75:

        reasons.append(
            "Confidence score is strong."
        )

    else:

        reasons.append(
            "Confidence score too low."
        )

    if session_name in [
        "London Session",
        "London/New York Overlap",
        "New York Session"
    ]:

        reasons.append(
            "Trading session quality is strong."
        )

    else:

        reasons.append(
            "Current session has lower liquidity."
        )

    if final_trade_allowed:

        final_decision = (
            "TRADE APPROVED"
        )

    else:

        final_decision = (
            "NO TRADE"
        )

    return {
        "decision": final_decision,
        "reasons": reasons
    }