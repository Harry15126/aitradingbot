from data_sources import get_forex_data
from strategies import analyze_pair
from agents import get_current_session
from risk_rules import calculate_risk_plan
from daily_risk_manager import daily_loss_limit_reached
from daily_trade_manager import daily_trade_limit_reached
from trade_exit_manager import check_trade_exits
from trailing_stop_manager import update_trailing_stops
from execution_engine import execute_trade

from currency_strength_agent import (
    get_pair_strength_signal,
    currency_strength_supports_trade
)

from market_structure_agent import analyze_market_structure
from news_risk_agent import check_news_risk
from candlestick_agent import analyze_candlesticks
from trade_quality_agent import calculate_trade_quality
from ai_decision_agent import get_ai_decision
from multi_timeframe_agent import analyze_pair_timeframe, trend_supports_trade
from volatility_agent import calculate_atr, volatility_supports_trade

from open_trade_manager import (
    initialize_open_trades,
    has_open_trade,
    show_open_trades,
    get_open_trades
)

from paper_trader import (
    initialize_account,
    get_account_balance,
    log_paper_trade,
    log_strategy_setup
)

from bot_control import (
    BOT_ACTIVE,
    ALLOW_NEW_TRADES,
    PAPER_TRADING_ONLY,
    MAX_OPEN_TRADES
)

print("\n===== LIVE 200 EMA TRADING BOT STARTED =====")

if not BOT_ACTIVE:
    print("\nBOT IS DISABLED FROM bot_control.py")
    quit()

if not PAPER_TRADING_ONLY:
    print("\nWARNING: PAPER_TRADING_ONLY is False.")
    print("Only continue if you are intentionally testing broker execution.")

initialize_account()
initialize_open_trades()

session_info = get_current_session()
market_data = get_forex_data()

show_open_trades()

update_trailing_stops(market_data)

check_trade_exits(
    market_data,
    session_info["session"]
)

daily_risk = daily_loss_limit_reached()
daily_trades = daily_trade_limit_reached()
open_trades = get_open_trades()

print("\n===== PAPER ACCOUNT =====")
print("Current Balance: $", get_account_balance())

print("\n===== BOT CONTROL STATUS =====")
print("BOT ACTIVE:", BOT_ACTIVE)
print("ALLOW NEW TRADES:", ALLOW_NEW_TRADES)
print("PAPER TRADING ONLY:", PAPER_TRADING_ONLY)
print("MAX OPEN TRADES:", MAX_OPEN_TRADES)
print("CURRENT OPEN TRADES:", len(open_trades))

print("\n===== DAILY LIMIT CHECK =====")
print("Today Loss: $", daily_risk["today_loss"])
print("Daily Loss Limit Reached:", daily_risk["limit_reached"])
print("Today Trades:", daily_trades["today_trades"])
print("Daily Trade Limit Reached:", daily_trades["limit_reached"])

if daily_risk["limit_reached"]:
    print("\nDaily loss limit reached.")
    print("No more trades today.")

elif daily_trades["limit_reached"]:
    print("\nDaily trade limit reached.")
    print("No more trades today.")

elif not ALLOW_NEW_TRADES:
    print("\nNew trades disabled from bot_control.py")

elif len(open_trades) >= MAX_OPEN_TRADES:
    print("\nMaximum open trades reached.")

else:
    print("\n===== LIVE STRATEGY SCAN =====")

    for pair, data in market_data.items():

        open_trades = get_open_trades()

        if len(open_trades) >= MAX_OPEN_TRADES:
            print("\nMaximum open trades reached during scan.")
            break

        print(f"\n--- {pair} ---")

        if data is None:
            print("No data available.")
            continue

        # NEWS CIRCUIT BREAKER
        news_check = check_news_risk(pair)
        if news_check["news_risk"]:
            print(f"\n[NEWS PAUSE] {pair}: {news_check['message']} (Event: {news_check['event']})")
            continue

        if has_open_trade(pair):
            print("Trade already open for this pair.")
            continue

        # Strategy Analysis
        result = analyze_pair(data)

        # Higher-timeframe trend filter
        higher_timeframe = analyze_pair_timeframe(pair, "1h")
        higher_timeframe_supported = trend_supports_trade(
            result["bias"],
            higher_timeframe
        )

        # ATR volatility filter
        volatility = calculate_atr(data)
        volatility_supported = volatility_supports_trade(volatility)

        # Market Structure Analysis (SMC)
        structure = analyze_market_structure(data)

        # Candlestick Analysis (FVG)
        candles = analyze_candlesticks(data)

        strength_signal = get_pair_strength_signal(pair)

        strength_filter = currency_strength_supports_trade(
            pair,
            result["bias"]
        )

        # --- TRADE QUALITY CALCULATION ---
        quality_criteria = {
            "market_structure": structure,
            "fvg": candles["fvg"],
            "currency_strength_diff": strength_signal.get("absolute_difference", 0),
            "ema_distance_pips": result["ema_distance_pips"],
            "session_quality": session_info.get("session_quality", "Medium"),
            "news_risk": news_check["news_risk"],
            "volatility_atr": volatility.get("atr", 0),
            "avg_atr": 1
        }
        quality = calculate_trade_quality(quality_criteria)

        setup_log = {
            "session": session_info["session"],
            "session_quality": session_info.get("session_quality", "Medium"),
            "pair": pair,
            "entry_type": result["entry_type"],
            "bias": result["bias"],
            "price": result["price"],
            "ema200": result["ema200"],
            "ema9": result["ema9"],
            "ema_distance_pips": result["ema_distance_pips"],
            "higher_timeframe_trend": higher_timeframe.get("trend"),
            "higher_timeframe_supported": higher_timeframe_supported,
            "atr": volatility.get("atr"),
            "atr_percent": volatility.get("atr_percent", ""),
            "volatility_level": volatility.get("volatility_level"),
            "volatility_supported": volatility_supported,
            "quality_grade": quality["grade"],
            "quality_score": quality["score"],
            "smc_signal": structure["signal"],
            "smc_reason": structure["reason"],
            "fvg_detected": candles["fvg"]["detected"],
            "fvg_type": candles["fvg"]["type"],
            "fvg_strength": candles["fvg"]["strength"],
            "currency_strength_signal": strength_signal.get("signal"),
            "currency_strength_difference": strength_signal.get("absolute_difference"),
            "currency_strength_supported": strength_filter["supported"]
        }

        print("Strategy:", result["strategy_name"])
        print("Entry Type:", result["entry_type"])
        print("Price:", result["price"])
        print("200 EMA:", result["ema200"])
        print("9 EMA:", result["ema9"])
        print("Distance From 200 EMA Pips:", result["ema_distance_pips"])
        print("Bias:", result["bias"])
        print("Reason:", result["strategy_reason"])

        print("\n===== 1H TREND FILTER =====")
        print("1H Trend:", higher_timeframe.get("trend"))
        print("Supports Trade:", higher_timeframe_supported)
        print("Message:", higher_timeframe.get("message"))

        print("\n===== ATR VOLATILITY FILTER =====")
        print("ATR Available:", volatility.get("atr_available"))
        print("ATR:", volatility.get("atr"))
        print("ATR Percent:", volatility.get("atr_percent"))
        print("Volatility Level:", volatility.get("volatility_level"))
        print("Supports Trade:", volatility_supported)
        print("Message:", volatility.get("message"))

        print("\n===== MARKET STRUCTURE (SMC) =====")
        print("Structure Signal:", structure["signal"])
        print("BOS Status:", "Detected" if structure["bos"] else "None")
        print("CHOCH Status:", "Detected" if structure["choch"] else "None")
        print("Liquidity Sweep:", "Detected" if structure["sweep"] else "None")
        print("Structure Reason:", structure["reason"])

        print("\n===== FVG ANALYSIS =====")
        fvg = candles["fvg"]
        print("FVG Detected:", "Yes" if fvg["detected"] else "No")
        print("FVG Type:", fvg["type"])
        print("FVG Zone:", fvg["zone"])
        print("FVG Size:", fvg["size"])
        print("FVG Strength:", fvg["strength"])

        print("\n===== TRADE QUALITY SCORE =====")
        print("Score:", quality["score"])
        print("Grade:", quality["grade"])
        print("Quality Label:", quality["trade_quality"])
        print("Reasons:")
        for r in quality["reasons"]:
            print(f" - {r}")

        print("\n===== CURRENCY STRENGTH CHECK =====")
        print("Base:", strength_signal.get("base"))
        print("Quote:", strength_signal.get("quote"))
        print("Base Strength:", strength_signal.get("base_strength"))
        print("Quote Strength:", strength_signal.get("quote_strength"))
        print("Difference:", strength_signal.get("absolute_difference"))
        print("Strength Signal:", strength_signal.get("signal"))
        print("Supports Trade:", strength_filter["supported"])
        if not strength_filter["supported"]:
            print("[TESTING MODE] Currency strength is report-only. Trade not rejected here.")

        if result["bias"] == "WAIT":
            print("\nNo trade.")
            print("EMA strategy setup not valid.")

            trade_result = {
                "trade_taken": False,
                "profit_loss": 0,
                "new_balance": get_account_balance()
            }

            log_paper_trade(
                pair,
                session_info["session"],
                False,
                0,
                trade_result
            )
            setup_log["decision"] = "REJECTED_EMA_WAIT"
            log_strategy_setup(setup_log)

            continue

        if not higher_timeframe_supported:
            print("\nNo trade.")
            print("1H trend does not support the 15m setup.")

            trade_result = {
                "trade_taken": False,
                "profit_loss": 0,
                "new_balance": get_account_balance()
            }

            log_paper_trade(
                pair,
                session_info["session"],
                False,
                quality["score"],
                trade_result
            )
            setup_log["decision"] = "REJECTED_1H_TREND"
            log_strategy_setup(setup_log)

            continue

        if not volatility_supported:
            print("\nNo trade.")
            print("ATR volatility filter rejected setup.")

            trade_result = {
                "trade_taken": False,
                "profit_loss": 0,
                "new_balance": get_account_balance()
            }

            log_paper_trade(
                pair,
                session_info["session"],
                False,
                quality["score"],
                trade_result
            )
            setup_log["decision"] = "REJECTED_VOLATILITY"
            log_strategy_setup(setup_log)

            continue

        # --- QUALITY GATE ---
        # Only high-quality strategy setups are sent to AI. The AI is the final
        # review layer, not the primary strategy selector.
        if quality["grade"] not in ["A", "B"]:
            print("\n[AI SKIPPED] Reason: Low-quality setup")
            print("[QUALITY FILTER] Trade rejected before AI review.")
            trade_result = {
                "trade_taken": False,
                "profit_loss": 0,
                "new_balance": get_account_balance()
            }
            log_paper_trade(
                pair,
                session_info["session"],
                False,
                quality["score"],
                trade_result
            )
            setup_log["decision"] = "REJECTED_LOW_QUALITY"
            log_strategy_setup(setup_log)
            continue

        stop_loss = result["stop_loss_zone"]

        risk_plan = calculate_risk_plan(
            get_account_balance(),
            result["price"],
            stop_loss
        )

        if not risk_plan["trade_allowed"]:
            print("\nNo trade.")
            print("Risk rules rejected setup.")

            trade_result = {
                "trade_taken": False,
                "profit_loss": 0,
                "new_balance": get_account_balance()
            }

            log_paper_trade(
                pair,
                session_info["session"],
                False,
                0,
                trade_result
            )
            setup_log["decision"] = "REJECTED_RISK_RULES"
            log_strategy_setup(setup_log)

            continue

        # --- AI DECISION GATE ---
        # Only call AI if all previous filters passed
        print("\n[AI REVIEW] Sending setup to AI")

        # Construct trade data for the AI agent
        trade_data = {
            "pair": pair,
            "direction": risk_plan["direction"],
            "entry": risk_plan["entry_price"],
            "stop_loss": risk_plan["stop_loss"],
            "take_profit": risk_plan["take_profit"],
            "grade": quality["grade"],
            "score": quality["score"],
            "smc_structure": structure["reason"],
            "fvg_details": f"Type: {candles['fvg']['type']}, Zone: {candles['fvg']['zone']}, Strength: {candles['fvg']['strength']}",
            "currency_strength": f"Diff: {strength_signal.get('absolute_difference', 0)}",
            "session": session_info.get("session_quality", "Medium"),
            "news_risk": news_check["news_risk"]
        }

        ai_decision = get_ai_decision(trade_data)

        if not ai_decision["approved"]:
            print(f"\n[AI REJECTED] {ai_decision['reason']}")
            trade_result = {
                "trade_taken": False,
                "profit_loss": 0,
                "new_balance": get_account_balance()
            }
            log_paper_trade(
                pair,
                session_info["session"],
                False,
                0,
                trade_result
            )
            setup_log["decision"] = "REJECTED_AI"
            setup_log["ai_approved"] = ai_decision["approved"]
            setup_log["ai_confidence"] = ai_decision["confidence"]
            setup_log["ai_reason"] = ai_decision["reason"]
            log_strategy_setup(setup_log)
            continue

        print(f"\n[AI APPROVED] Confidence: {ai_decision['confidence']}% - {ai_decision['reason']}")

        print("\n===== RISK PLAN =====")
        print("Direction:", risk_plan["direction"])
        print("Entry:", risk_plan["entry_price"])
        print("Stop Loss:", risk_plan["stop_loss"])
        print("Take Profit:", risk_plan["take_profit"])
        print("Stop Loss Pips:", risk_plan["stop_loss_pips"])
        print("Stop Loss Quality:", risk_plan["stop_loss_quality"])
        print("Risk Amount: $", risk_plan["risk_amount"])
        print("Lot Size:", risk_plan["recommended_lot_size"])

        execute_trade(pair, risk_plan)

        print("\n===== TRADE EXECUTED THROUGH EXECUTION ENGINE =====")
        print("Pair:", pair)
        print("Direction:", risk_plan["direction"])
        print("Entry:", risk_plan["entry_price"])
        print("Stop Loss:", risk_plan["stop_loss"])
        print("Take Profit:", risk_plan["take_profit"])
        print("Risk Amount: $", risk_plan["risk_amount"])

        trade_result = {
            "trade_taken": True,
            "profit_loss": 0,
            "new_balance": get_account_balance()
        }

        log_paper_trade(
            pair,
            session_info["session"],
            True,
            100,
            trade_result
        )
        setup_log["decision"] = "TRADE_EXECUTED"
        setup_log["ai_approved"] = ai_decision["approved"]
        setup_log["ai_confidence"] = ai_decision["confidence"]
        setup_log["ai_reason"] = ai_decision["reason"]
        log_strategy_setup(setup_log)

print("\n===== SYSTEM COMPLETE =====")
print("Live scan finished.")
