import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4:31b-cloud"

def clean_json_response(text):
    """
    Robustly extracts JSON from a string that may contain markdown code blocks
    or extra conversational text before/after the JSON object.
    """
    # 1. Try to find a JSON block wrapped in ```json ... ```
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    # 2. Try to find any block wrapped in ``` ... ```
    generic_match = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
    if generic_match:
        return generic_match.group(1)

    # 3. Find the first '{' and last '}' and extract everything between them
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]

    return text

def get_ai_decision(trade_data):
    """
    Uses a local Ollama model to make the final 'Go/No-Go' decision on a trade.
    Integrates all technical, structural, and risk data to provide an intelligent filter.
    """

    # --- HARD REJECTIONS (Pre-AI) ---
    # During strategy testing, trade quality grade is context for the model,
    # not a hard pre-model rejection. Keep only true safety checks here.
    if trade_data.get("news_risk", False):
        return {
            "approved": False,
            "confidence": 0,
            "reason": "Rejected: High-impact news risk detected."
        }

    if not trade_data.get("entry") or not trade_data.get("stop_loss"):
        return {
            "approved": False,
            "confidence": 0,
            "reason": "Rejected: Risk plan is incomplete or invalid."
        }

    # --- AI ANALYSIS ---
    prompt = f"""
    Act as a Senior Institutional Forex Trader. Analyze the following trade setup and decide if we should execute.

    TRADE DATA:
    - Pair: {trade_data.get('pair')}
    - Direction: {trade_data.get('direction')}
    - Entry: {trade_data.get('entry')}
    - Stop Loss: {trade_data.get('stop_loss')}
    - Take Profit: {trade_data.get('take_profit')}
    - Trade Quality: {trade_data.get('grade')} Grade (Score: {trade_data.get('score')})
    - SMC Structure: {trade_data.get('smc_structure')}
    - FVG Details: {trade_data.get('fvg_details')}
    - Currency Strength: {trade_data.get('currency_strength')}
    - Session: {trade_data.get('session')}

    Your goal is to find high-probability institutional setups.

    Return ONLY a JSON object in this format:
    {{
        "approved": true/false,
        "confidence": 0-100,
        "reason": "one sentence explanation"
    }}
    """

    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        headers = {'Content-Type': 'application/json'}

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()

        result = response.json()
        ai_response_text = result.get("response", "{}")

        # Clean and extract JSON
        cleaned_json = clean_json_response(ai_response_text)
        decision = json.loads(cleaned_json)

        return {
            "approved": decision.get("approved", False),
            "confidence": decision.get("confidence", 0),
            "reason": decision.get("reason", "Lacking sufficient data to determine a clear reason.")
        }

    except Exception as e:
        # Fail-safe: Reject trade if AI is offline or parsing fails
        return {
            "approved": False,
            "confidence": 0,
            "reason": f"AI Decision Agent Error: {str(e)}. Rejecting for safety."
        }
