from ai_decision_agent import get_ai_decision

def test_ai_decision_grade_a():
    print("\n--- Testing AI Decision Agent: Grade A Setup ---")

    # Construct a high-quality fake setup
    fake_trade_data = {
        "pair": "USD/JPY",
        "direction": "BUY",
        "entry": 158.50,
        "stop_loss": 158.20,
        "take_profit": 159.50,
        "grade": "A",
        "score": 85,
        "smc_structure": "Bullish BOS detected; Market shifting from bearish to bullish character.",
        "fvg_details": "Strong Bullish FVG detected between 158.30 and 158.40.",
        "currency_strength": "USD Strong (4.5), JPY Weak (1.2) - Difference: 3.3",
        "news_risk": False,
        "session": "London/NY overlap (High Quality)"
    }

    print("Sending Grade A setup to AI...")
    decision = get_ai_decision(fake_trade_data)

    print("\n===== AI DECISION OUTPUT =====")
    print(f"Approved: {decision['approved']}")
    print(f"Confidence: {decision['confidence']}%")
    print(f"Reason: {decision['reason']}")
    print("=============================\n")

if __name__ == "__main__":
    try:
        test_ai_decision_grade_a()
    except Exception as e:
        print(f"Test failed with error: {e}")
        print("\nNote: Ensure Ollama is running at http://localhost:11434 and gemma4:31b is pulled.")
