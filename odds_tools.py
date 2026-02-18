"""
📊 ODDS & BETTING TOOLS MODULE
Extracted from data_fetcher.py for modularity.
Contains: Kelly Criterion, odds checking, calibration engine.
"""

import os
import json
import random


def check_odds_value(market_code, betano_odd, sport="football"):
    """
    Simulates a comparison with Pinnacle (Sharp Bookmaker) to find EV+.
    Returns a string analysis.
    """
    sharp_lines = {
        "Nuggets -5.5": 1.75,
        "Lakers ML": 1.70,
        "Magic -6.5": 1.85,
        "Over 234.5": 1.88,
        "River Vence": 1.25,
    }
    
    fair_odd = sharp_lines.get(market_code, betano_odd)
    
    if betano_odd > fair_odd:
        ev = ((betano_odd / fair_odd) - 1) * 100
        return f"💎 VALOR ENCONTRADO: Odd Betano ({betano_odd}) está acima da Pinnacle ({fair_odd}). EV+ de {round(ev, 1)}%. Aproveite antes que ajustem."
    else:
        return "⚖️ ODD JUSTA: Alinhada com o mercado mundial."


def calculate_kelly_criterion(win_prob_percent, decimal_odds):
    """
    Calculates the optimal stake percentage using the Kelly Criterion.
    Returns a safe fraction (Half-Kelly) to avoid ruin.
    """
    p = win_prob_percent / 100
    q = 1 - p
    b = decimal_odds - 1
    
    if b <= 0: return 0
    
    kelly_fraction = (b * p - q) / b
    safe_stake = max(0, kelly_fraction * 0.3) * 100
    
    if safe_stake > 5:
        safe_stake = 5.0
        
    return round(safe_stake, 1)


def get_calibration_adjustments():
    """
    Reads history.json and computes REAL hit rates by league and odds range.
    Returns adjustment factors that modify displayed probabilities.
    """
    history_file = 'history.json'
    if not os.path.exists(history_file):
        return {"by_league": {}, "by_odds_range": {}, "global_accuracy": 0}
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        return {"by_league": {}, "by_odds_range": {}, "global_accuracy": 0}
    
    if not history:
        return {"by_league": {}, "by_odds_range": {}, "global_accuracy": 0}

    league_stats = {}
    odds_range_stats = {}
    total_resolved = 0
    total_wins = 0

    for entry in history:
        status = entry.get('status', 'PENDING')
        if status not in ('WON', 'LOST'):
            continue
        
        total_resolved += 1
        is_win = status == 'WON'
        if is_win:
            total_wins += 1

        league = entry.get('league', 'Unknown')
        if league not in league_stats:
            league_stats[league] = {"wins": 0, "total": 0}
        league_stats[league]["total"] += 1
        if is_win:
            league_stats[league]["wins"] += 1

        odd = float(entry.get('odd', 1.5))
        if odd < 1.40:
            range_key = "1.10-1.40"
        elif odd < 1.70:
            range_key = "1.40-1.70"
        elif odd < 2.00:
            range_key = "1.70-2.00"
        else:
            range_key = "2.00+"
        
        if range_key not in odds_range_stats:
            odds_range_stats[range_key] = {"wins": 0, "total": 0}
        odds_range_stats[range_key]["total"] += 1
        if is_win:
            odds_range_stats[range_key]["wins"] += 1

    by_league = {}
    for lg, data in league_stats.items():
        hit_rate = round((data["wins"] / data["total"]) * 100, 1) if data["total"] > 0 else 50
        adjustment = 1.0
        if data["total"] >= 5:
            if hit_rate < 50:
                adjustment = 0.90
            elif hit_rate > 85:
                adjustment = 1.05
        by_league[lg] = {"hit_rate": hit_rate, "sample": data["total"], "adjustment": adjustment}

    by_odds_range = {}
    for rng, data in odds_range_stats.items():
        hit_rate = round((data["wins"] / data["total"]) * 100, 1) if data["total"] > 0 else 50
        adjustment = 1.0
        if data["total"] >= 5:
            if hit_rate < 50:
                adjustment = 0.85
            elif hit_rate > 80:
                adjustment = 1.05
        by_odds_range[rng] = {"hit_rate": hit_rate, "sample": data["total"], "adjustment": adjustment}

    global_accuracy = round((total_wins / total_resolved) * 100, 1) if total_resolved > 0 else 0

    return {
        "by_league": by_league,
        "by_odds_range": by_odds_range,
        "global_accuracy": global_accuracy
    }


def apply_calibration(prob, odd, league):
    """
    Applies calibration adjustments to a probability estimate.
    """
    calibration = get_calibration_adjustments()
    adjusted = prob
    
    league_data = calibration.get("by_league", {}).get(league)
    if league_data and league_data.get("sample", 0) >= 5:
        adjusted *= league_data["adjustment"]

    if odd < 1.40:
        range_key = "1.10-1.40"
    elif odd < 1.70:
        range_key = "1.40-1.70"
    elif odd < 2.00:
        range_key = "1.70-2.00"
    else:
        range_key = "2.00+"
    
    odds_data = calibration.get("by_odds_range", {}).get(range_key)
    if odds_data and odds_data.get("sample", 0) >= 5:
        adjusted *= odds_data["adjustment"]

    adjusted = max(30, min(95, adjusted))
    return round(adjusted, 1)
