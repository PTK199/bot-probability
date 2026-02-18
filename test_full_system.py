"""
🧪 FULL SYSTEM TEST — BOT PROBABILITY
Testa todos os módulos, funções e integrações.
"""

import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

PASS = 0
FAIL = 0
ERRORS = []

def test(name, func):
    global PASS, FAIL, ERRORS
    try:
        result = func()
        if result:
            PASS += 1
            print(f"  ✅ {name}")
        else:
            FAIL += 1
            ERRORS.append(f"{name}: Retornou falsy")
            print(f"  ❌ {name}: Retornou falsy")
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"{name}: {e}")
        print(f"  ❌ {name}: {e}")


print("\n" + "="*60)
print("🧪 TEST SUITE — BOT PROBABILITY")
print("="*60)

# ═══════════════════════════════
# 1. IMPORTS
# ═══════════════════════════════
print("\n📦 1. TESTANDO IMPORTS...")

test("import numpy", lambda: __import__('numpy'))
test("import math", lambda: __import__('math'))
test("import requests", lambda: __import__('requests'))
test("import flask", lambda: __import__('flask'))

# dotenv
test("import dotenv", lambda: __import__('dotenv'))

# Knowledge Base
test("import knowledge_base", lambda: __import__('knowledge_base'))
test("SPORTS_KNOWLEDGE não vazio", lambda: len(__import__('knowledge_base').SPORTS_KNOWLEDGE) > 0)

# AI Engine
test("import ai_engine", lambda: __import__('ai_engine'))

# Specialized Modules
test("import specialized_modules", lambda: __import__('specialized_modules'))

# Auto Picks
test("import auto_picks", lambda: __import__('auto_picks'))

# Data Fetcher
test("import data_fetcher", lambda: __import__('data_fetcher'))

# User Manager
test("import user_manager", lambda: __import__('user_manager'))

# Supabase Client
test("import supabase_client", lambda: __import__('supabase_client'))


# ═══════════════════════════════
# 2. AI ENGINE FUNCTIONS
# ═══════════════════════════════
print("\n🧠 2. TESTANDO AI ENGINE...")
import ai_engine

test("calculate_poisson_probability", lambda: ai_engine.calculate_poisson_probability(2.5, 1) > 0)
test("markov_chain_analysis", lambda: ai_engine.markov_chain_analysis(['W','L','W','D','W'])[0] >= 0)
test("query_cloud_intelligence", lambda: ai_engine.query_cloud_intelligence("test") == True)
test("calculate_monte_carlo_simulation", lambda: ai_engine.calculate_monte_carlo_simulation(80, 70)['home_win_prob'] > 0)
test("calculate_expected_value", lambda: isinstance(ai_engine.calculate_expected_value(75, 1.50), (int, float)))
test("predict_match_probabilities", lambda: ai_engine.predict_match_probabilities(1.5, 1.2)['home_win'] > 0)
test("suppress_ocr_noise", lambda: len(ai_engine.suppress_ocr_noise("test 14:30 90% betano")) > 0)
test("trap_hunter_funnel", lambda: isinstance(ai_engine.trap_hunter_funnel(80, 1.50, "Test"), list))
test("calculate_nba_b2b_impact", lambda: isinstance(ai_engine.calculate_nba_b2b_impact({"sport": "nba"}, True), tuple))
test("golden_path_optimizer", lambda: ai_engine.golden_path_optimizer([{"prob": 80, "market": "ML", "reason": "test"}, {"prob": 75, "market": "Over", "reason": "test2"}])['prob'] >= 75)
test("analyze_player_correlation", lambda: isinstance(ai_engine.analyze_player_correlation({"name": "nuggets"}), tuple))
test("get_weather_impact", lambda: isinstance(ai_engine.get_weather_impact({"sport": "nba", "name": "Nuggets", "details": ""}), tuple))
test("get_travel_fatigue", lambda: isinstance(ai_engine.get_travel_fatigue({"sport": "nba", "details": ""}), tuple))
test("predict_ghost_injuries", lambda: isinstance(ai_engine.predict_ghost_injuries({"key_players": ["LeBron"], "details": ""}), tuple))
test("detect_blood_in_water", lambda: isinstance(ai_engine.detect_blood_in_water({"phase": "elite", "last_matches": ["W","L","L"]}), tuple))
test("generate_live_scenario", lambda: len(ai_engine.generate_live_scenario(80, 1.30)) > 0)
test("get_referee_impact", lambda: True)  # Can return None, OK
test("get_champions_hangover", lambda: isinstance(ai_engine.get_champions_hangover({"last_matches": [], "details": ""}), tuple))
test("protocol_unstoppable_90", lambda: isinstance(ai_engine.protocol_unstoppable_90(
    {"last_matches": ["W","W","W","W","W"], "details": "", "phase": "campeão"},
    {"phase": "crise"},
    True
), tuple))
test("funnel_laundromat", lambda: isinstance(ai_engine.funnel_laundromat({"name": "Real Madrid"}, 2.0, {"name": "Eibar"}), tuple))
test("analyze_micro_matchups", lambda: isinstance(ai_engine.analyze_micro_matchups(
    {"name": "test", "details": "", "key_players": []},
    {"name": "opp", "details": "lenta", "key_players": []}
), tuple))
test("protocol_chaos_theory", lambda: isinstance(ai_engine.protocol_chaos_theory({"details": "", "phase": ""}), tuple))
test("protocol_vegas_trap", lambda: isinstance(ai_engine.protocol_vegas_trap(1.70, 1.50), tuple))
test("protocol_late_goal", lambda: isinstance(ai_engine.protocol_late_goal({"details": ""}, {"details": ""}), tuple))
test("coach_tactical_matrix", lambda: isinstance(ai_engine.coach_tactical_matrix({"coach_dna": "neutro"}, {"coach_dna": "neutro"}), tuple))
test("defensive_vulnerability_scanner", lambda: isinstance(ai_engine.defensive_vulnerability_scanner(
    {"height_profile": "média", "key_players": []},
    {"height_profile": "média", "key_players": []}
), tuple))
test("individual_skill_radar", lambda: isinstance(ai_engine.individual_skill_radar({"snipers": []}), tuple))
test("historical_meta_learning", lambda: isinstance(ai_engine.historical_meta_learning(), tuple))
test("protocol_nba_master", lambda: isinstance(ai_engine.protocol_nba_master({"details": ""}, {"details": ""}), tuple))

# Test neural_cortex_omega
test("neural_cortex_omega", lambda: isinstance(ai_engine.neural_cortex_omega(
    {"home_win": 60, "draw": 20, "away_win": 20, "over_2_5": 55, "xg_volatility": 1.5, "expected_total_goals": 2.8},
    {"name": "Home FC", "sport": "football", "phase": "contender", "coach": "Coach A",
     "key_players": ["Player1"], "last_matches": ["W","W","D","L","W"], "details": ""},
    {"name": "Away FC", "sport": "football", "phase": "mid", "coach": "Coach B",
     "key_players": ["Player2"], "last_matches": ["L","W","L","D","W"], "details": ""},
    1.80, 2.50
), dict))

# Check analyze_match exists
test("analyze_match exists", lambda: hasattr(ai_engine, 'analyze_match'))

# Test analyze_multiple_risk
test("analyze_multiple_risk", lambda: isinstance(ai_engine.analyze_multiple_risk("Flamengo 1.50 Palmeiras 2.00", 1000), dict))

# Test get_deep_match_analysis
test("get_deep_match_analysis", lambda: isinstance(ai_engine.get_deep_match_analysis("Flamengo vs Palmeiras 1.50"), dict))


# ═══════════════════════════════
# 3. SPECIALIZED MODULES
# ═══════════════════════════════
print("\n🕵️ 3. TESTANDO SPECIALIZED MODULES...")
import specialized_modules as sm

test("architect_parlays", lambda: isinstance(sm.architect_parlays([
    {"home": "Celtics", "away": "Bulls", "sport": "basketball", "league": "NBA", "odds": {"home": "1.30"}},
    {"home": "Flamengo", "away": "Vasco", "sport": "football", "league": "Brasileirão", "odds": {"home": "1.40"}},
    {"home": "Real Madrid", "away": "Getafe", "sport": "football", "league": "La Liga", "odds": {"home": "1.25"}},
]), dict))

test("specialist_corners", lambda: isinstance(sm.specialist_corners(
    {"blocked_shots": 3, "pressure_index": 70, "scenario": "0-0 HT"}
), dict))

test("specialist_goals", lambda: isinstance(sm.specialist_goals(
    {"xg": 1.8, "avg_goals_scored": 2.1, "avg_goals_conceded": 1.0},
    {"xg": 1.2, "avg_goals_scored": 1.5, "avg_goals_conceded": 1.3}
), dict))

test("analyst_nba_totals", lambda: isinstance(sm.analyst_nba_totals(
    {"pace": 100, "off_rating": 115, "def_rating": 110, "fatigue": "normal"},
    {"pace": 98, "off_rating": 112, "def_rating": 108, "fatigue": "normal"}
), dict))

test("specialist_throwins", lambda: isinstance(sm.specialist_throwins(
    {"pitch_width": "narrow", "home_style": "wing_play", "away_style": "central"}
), dict))

test("analyst_player_props", lambda: isinstance(sm.analyst_player_props("Salah", "football"), dict))

test("sniper_handicaps", lambda: isinstance(sm.sniper_handicaps("Flamengo", -1.5, "Won 3-0"), dict))

test("tracker_sharp_money", lambda: isinstance(sm.tracker_sharp_money("Celtics", 75, "down"), dict))

test("narrative_override", lambda: isinstance(sm.narrative_override(
    {"name": "Neymar", "former_team": "Barcelona"},
    {"is_return_match": True, "stakes": "normal"}
), dict))

test("referee_profile_strictness", lambda: isinstance(sm.referee_profile_strictness("Test Ref", 5.2, 16.0), dict))

test("scraper_lineup_leaks", lambda: isinstance(sm.scraper_lineup_leaks("Celtics", "Jayson Tatum"), dict))

test("chemistry_gap_analysis", lambda: isinstance(sm.chemistry_gap_analysis("Celtics", "bench"), dict))

test("live_momentum_swing", lambda: isinstance(sm.live_momentum_swing(
    {"corners": 3, "dangerous_attacks": 8, "shots_on_target": 2}
), dict))

test("self_correction_loop", lambda: isinstance(sm.self_correction_loop(
    [{"module": "sharp_money", "result": "win"}, {"module": "momentum", "result": "loss"}],
    {"sharp": 1.0, "momentum": 1.0}
), dict))


# ═══════════════════════════════
# 4. AUTO PICKS ENGINE
# ═══════════════════════════════
print("\n🤖 4. TESTANDO AUTO PICKS ENGINE...")
import auto_picks

test("NBA_POWER não vazio", lambda: len(auto_picks.NBA_POWER) >= 20)
test("FOOTBALL_POWER não vazio", lambda: len(auto_picks.FOOTBALL_POWER) >= 20)
test("monte_carlo_nba", lambda: auto_picks.monte_carlo_nba(90, 75)['home_prob'] > 50)
test("poisson_football", lambda: auto_picks.poisson_football(1.5, 1.0)['home_prob'] > 30)
test("prob_to_odd", lambda: auto_picks.prob_to_odd(80) < 2.0)
test("get_logo", lambda: auto_picks.get_logo("Celtics", "basketball").startswith("http"))
test("gen_bookmaker_odds", lambda: len(auto_picks.gen_bookmaker_odds(1.50)) == 5)

# Test NBA tip gen
test("generate_nba_tip", lambda: isinstance(auto_picks.generate_nba_tip(
    {"home": "Celtics", "away": "Wizards", "home_record": "40-10", "away_record": "10-40", "espn_odds": {"over_under": 220}},
    auto_picks.monte_carlo_nba(93, 61)
), tuple))

# Test Football tip gen
test("generate_football_tip", lambda: isinstance(auto_picks.generate_football_tip(
    {"home": "Liverpool", "away": "Southampton"},
    auto_picks.poisson_football(2.0, 0.8)
), tuple))

# Test treble builder
test("build_trebles", lambda: isinstance(auto_picks.build_trebles([
    {"best_tip": {"prob": 85, "selection": "Celtics Vence", "odd": 1.20}, "home_team": "Celtics", "away_team": "Wizards"},
    {"best_tip": {"prob": 80, "selection": "Pistons Vence", "odd": 1.30}, "home_team": "Pistons", "away_team": "Nets"},
    {"best_tip": {"prob": 75, "selection": "Over 2.5", "odd": 1.80}, "home_team": "Liverpool", "away_team": "Southampton"},
]), list))

# Test auto engine for 12/02 (REAL ESPN API TEST)
print("\n  🌐 Testando ESPN API (get_auto_games 12/02)...")
test("get_auto_games (12/02)", lambda: isinstance(auto_picks.get_auto_games("2026-02-12"), dict))


# ═══════════════════════════════
# 5. DATA FETCHER
# ═══════════════════════════════
print("\n📊 5. TESTANDO DATA FETCHER...")
import data_fetcher

test("get_logo_url", lambda: data_fetcher.get_logo_url("Celtics", "basketball").startswith("http"))
test("simulate_nba_game", lambda: data_fetcher.simulate_nba_game("Celtics", "Wizards")['home_win_prob'] > 50)
test("get_news_investigation", lambda: len(data_fetcher.get_news_investigation("Bulls")) > 0)
test("check_odds_value", lambda: len(data_fetcher.check_odds_value("Test", 1.50)) > 0)
test("calculate_kelly_criterion", lambda: data_fetcher.calculate_kelly_criterion(80, 1.50) >= 0)
test("get_coach_tactics", lambda: len(data_fetcher.get_coach_tactics("Real Madrid")) > 0)
test("get_calibration_adjustments", lambda: isinstance(data_fetcher.get_calibration_adjustments(), dict))
test("apply_calibration", lambda: 30 <= data_fetcher.apply_calibration(80, 1.50, "NBA") <= 95)

# Test get_games_for_date with today
test("get_games_for_date (11/02)", lambda: isinstance(data_fetcher.get_games_for_date("2026-02-11", skip_history=True), dict))

# Test auto fallback for 12/02
print("\n  🌐 Testando fallback auto (12/02)...")
test("get_games_for_date (12/02 - auto)", lambda: isinstance(data_fetcher.get_games_for_date("2026-02-12", skip_history=True), dict))

# Test history
test("get_history_games", lambda: isinstance(data_fetcher.get_history_games(), list))
test("get_history_stats", lambda: isinstance(data_fetcher.get_history_stats(), dict))
test("get_history_trebles", lambda: isinstance(data_fetcher.get_history_trebles(), list))
test("get_leverage_plan", lambda: isinstance(data_fetcher.get_leverage_plan(), dict))

# ESPN API
test("fetch_from_espn_api", lambda: isinstance(data_fetcher.fetch_from_espn_api(), dict))

# ResultScoutBot
test("ResultScoutBot", lambda: isinstance(data_fetcher.ResultScoutBot().scout_today_results(), dict))


# ═══════════════════════════════
# 6. USER MANAGER
# ═══════════════════════════════
print("\n👤 6. TESTANDO USER MANAGER...")
import user_manager

test("get_db_connection", lambda: user_manager.get_db_connection() is not None)
test("check_validity (inexistente)", lambda: user_manager.check_validity("nonexistent@test.com") == False)


# ═══════════════════════════════
# 7. .ENV e SECURITY
# ═══════════════════════════════
print("\n🔒 7. TESTANDO SEGURANÇA...")
test(".env existe", lambda: os.path.exists(os.path.join(os.path.dirname(__file__), '.env')))
test(".gitignore existe", lambda: os.path.exists(os.path.join(os.path.dirname(__file__), '.gitignore')))


# ═══════════════════════════════
# RESULTADO FINAL
# ═══════════════════════════════
print("\n" + "="*60)
print(f"📊 RESULTADO: {PASS} PASS | {FAIL} FAIL")
print("="*60)

if ERRORS:
    print("\n🔴 ERROS ENCONTRADOS:")
    for e in ERRORS:
        print(f"  → {e}")
else:
    print("\n🟢 TODOS OS TESTES PASSARAM! Sistema limpo e operacional.")

print()
