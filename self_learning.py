"""
self_learning.py — SISTEMA DE AUTOCONHECIMENTO 🧠
===================================================
Motor de aprendizado contínuo que analisa histórico de acertos/erros
e gera correções automáticas para melhorar previsões futuras.

COMO FUNCIONA:
1. Lê history.json (todos os resultados passados)
2. Analisa padrões por:
   - Liga (NBA, Premier League, La Liga...)
   - Tipo de mercado (ML, DC, Over/Under)
   - Faixa de odds (1.01-1.30, 1.30-1.60, 1.60-2.00, 2.00+)
   - Times específicos (quais acertamos bem/mal)
   - Dia da semana
   - Home vs Away picks
3. Gera "lições aprendidas" (insights)
4. Calcula fatores de correção para cada dimensão
5. Salva estado em learning_state.json
6. Aplica correções automaticamente no pipeline

INTEGRAÇÃO:
  from self_learning import apply_learning_correction, study_results
  
  # No pipeline:
  corrected_prob = apply_learning_correction(prob, odd, league, market, home, away)
  
  # Após resultados:
  study_results()  # Atualiza o estado de aprendizado
"""

import json
import os
import sys
import datetime
import math

os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ═══════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════
HISTORY_FILE = "history.json"
LEARNING_STATE_FILE = "learning_state.json"

# Minimum samples needed before applying corrections
MIN_SAMPLES = 3
MIN_SAMPLES_TEAM = 2

# Maximum correction allowed (prevent wild swings)
MAX_CORRECTION = 15  # ±15% max adjustment

# ═══════════════════════════════════════
# LEARNING STATE STRUCTURE
# ═══════════════════════════════════════
DEFAULT_STATE = {
    "version": 3,
    "last_study": None,
    "total_studied": 0,
    "global_stats": {
        "total": 0,
        "won": 0,
        "lost": 0,
        "void": 0,
        "pending": 0,
        "accuracy": 0.0,
        "roi": 0.0,
    },
    "thresholds": {
        "sniper": 76,
        "banker": 84,
        "minimum": 62
    },
    # Performance by league
    "by_league": {},
    # Performance by market type (ML, DC, Over, Under)
    "by_market": {},
    # Performance by odds range
    "by_odds_range": {
        "ultra_safe": {"range": [1.01, 1.30], "won": 0, "lost": 0, "total": 0},
        "safe": {"range": [1.30, 1.60], "won": 0, "lost": 0, "total": 0},
        "value": {"range": [1.60, 2.00], "won": 0, "lost": 0, "total": 0},
        "risky": {"range": [2.00, 3.00], "won": 0, "lost": 0, "total": 0},
        "longshot": {"range": [3.00, 99.0], "won": 0, "lost": 0, "total": 0},
    },
    # Performance by specific team (when we pick FOR or AGAINST them)
    "by_team": {},
    # Performance by day of week
    "by_day": {},
    # Performance home vs away picks
    "by_side": {
        "home": {"won": 0, "lost": 0, "total": 0},
        "away": {"won": 0, "lost": 0, "total": 0},
    },
    # Generated insights (human-readable lessons)
    "insights": [],
    "toxic_teams": {},
    "top_leagues": [],
    "blacklisted_leagues": [],
    "market_efficiency": {},
    # Correction factors applied to future predictions
    "corrections": {
        "by_league": {},
        "by_market": {},
        "by_odds_range": {},
        "by_team": {},
    },
    # Streak tracking
    "current_streak": 0,  # positive = wins, negative = losses
    "best_streak": 0,
    "worst_streak": 0,
}


# ═══════════════════════════════════════
# LOAD / SAVE STATE
# ═══════════════════════════════════════
def _load_state():
    """Load learning state from file, or create default."""
    if os.path.exists(LEARNING_STATE_FILE):
        try:
            with open(LEARNING_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                # Migrate old versions
                if state.get("version", 1) < 3:
                    state.update({k: v for k, v in DEFAULT_STATE.items() if k not in state})
                    state["version"] = 3
                return state
        except:
            pass
    return json.loads(json.dumps(DEFAULT_STATE))


def _save_state(state):
    """Save learning state to file."""
    try:
        with open(LEARNING_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[LEARN] ❌ Erro ao salvar estado: {e}")


def _load_history():
    """Load history.json."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


# ═══════════════════════════════════════
# CLASSIFY MARKET TYPE
# ═══════════════════════════════════════
def _classify_market(selection):
    """Classify a selection into market type."""
    sel = selection.lower()
    if "ou empate" in sel or "dupla chance" in sel:
        return "DC"
    elif "vence" in sel or "ml" in sel:
        return "ML"
    elif "over" in sel:
        return "OVER"
    elif "under" in sel:
        return "UNDER"
    elif "btts" in sel or "ambas" in sel:
        return "BTTS"
    else:
        return "OTHER"


def _classify_odds_range(odd):
    """Classify odds into a range bucket."""
    odd = float(odd)
    if odd < 1.30:
        return "ultra_safe"
    elif odd < 1.60:
        return "safe"
    elif odd < 2.00:
        return "value"
    elif odd < 3.00:
        return "risky"
    else:
        return "longshot"


def _is_home_pick(entry):
    """Determine if the pick was for the home team."""
    sel = entry.get("selection", "").lower()
    home = entry.get("home", "").lower()
    # Check if home team name appears in selection
    return any(word in sel for word in home.split() if len(word) > 3)


# ═══════════════════════════════════════
# CORE: STUDY RESULTS
# ═══════════════════════════════════════
def study_results():
    """
    Main learning function. Reads all history and generates:
    1. Statistics per dimension (league, market, odds, team, day, side)
    2. Insights (human-readable lessons)
    3. Correction factors for future predictions
    
    Should be called after results are updated.
    """
    history = _load_history()
    state = _load_state()
    
    if not history:
        print("[LEARN] 📚 Sem histórico para estudar")
        return state
    
    # Reset counters
    state["global_stats"] = {"total": 0, "won": 0, "lost": 0, "void": 0, "pending": 0, "accuracy": 0.0, "roi": 0.0}
    state["by_league"] = {}
    state["by_market"] = {}
    state["by_odds_range"] = {
        "ultra_safe": {"range": [1.01, 1.30], "won": 0, "lost": 0, "total": 0},
        "safe": {"range": [1.30, 1.60], "won": 0, "lost": 0, "total": 0},
        "value": {"range": [1.60, 2.00], "won": 0, "lost": 0, "total": 0},
        "risky": {"range": [2.00, 3.00], "won": 0, "lost": 0, "total": 0},
        "longshot": {"range": [3.00, 99.0], "won": 0, "lost": 0, "total": 0},
    }
    state["by_team"] = {}
    state["by_day"] = {}
    state["by_side"] = {"home": {"won": 0, "lost": 0, "total": 0}, "away": {"won": 0, "lost": 0, "total": 0}}
    
    total_profit = 0.0
    total_staked = 0
    current_streak = 0
    best_streak = 0
    worst_streak = 0
    
    # ── PASS 1: COLLECT STATISTICS ──
    for entry in history:
        status = entry.get("status", "PENDING")
        # ARCHIVE_WON = WON arquivado (mesmo resultado para aprendizado)
        if status == "ARCHIVE_WON":
            status = "WON"
        if status == "PENDING":
            state["global_stats"]["pending"] += 1
            continue
        if status == "VOID":
            state["global_stats"]["void"] += 1
            continue
        
        is_win = status == "WON"
        league = entry.get("league", "Unknown")
        odd = float(entry.get("odd", 1.5))
        selection = entry.get("selection", "")
        home = entry.get("home", "")
        away = entry.get("away", "")
        date_str = entry.get("date", "")
        
        # Global
        state["global_stats"]["total"] += 1
        if is_win:
            state["global_stats"]["won"] += 1
        else:
            state["global_stats"]["lost"] += 1
        
        # ROI tracking
        total_staked += 1
        if is_win:
            total_profit += (odd - 1)
        else:
            total_profit -= 1
        
        # Streak tracking
        if is_win:
            if current_streak >= 0:
                current_streak += 1
            else:
                current_streak = 1
            best_streak = max(best_streak, current_streak)
        else:
            if current_streak <= 0:
                current_streak -= 1
            else:
                current_streak = -1
            worst_streak = min(worst_streak, current_streak)
        
        # By League
        if league not in state["by_league"]:
            state["by_league"][league] = {"won": 0, "lost": 0, "total": 0, "profit": 0.0}
        state["by_league"][league]["total"] += 1
        state["by_league"][league]["won" if is_win else "lost"] += 1
        state["by_league"][league]["profit"] += (odd - 1) if is_win else -1
        
        # By Market
        market = _classify_market(selection)
        if market not in state["by_market"]:
            state["by_market"][market] = {"won": 0, "lost": 0, "total": 0, "profit": 0.0}
        state["by_market"][market]["total"] += 1
        state["by_market"][market]["won" if is_win else "lost"] += 1
        state["by_market"][market]["profit"] += (odd - 1) if is_win else -1
        
        # By Odds Range
        odds_bucket = _classify_odds_range(odd)
        state["by_odds_range"][odds_bucket]["total"] += 1
        state["by_odds_range"][odds_bucket]["won" if is_win else "lost"] += 1
        
        # By Team (both teams get tracked)
        for team in [home, away]:
            if not team:
                continue
            team_key = team.lower().strip()
            if team_key not in state["by_team"]:
                state["by_team"][team_key] = {"won": 0, "lost": 0, "total": 0, "as_pick": 0, "as_opponent": 0}
            state["by_team"][team_key]["total"] += 1
            state["by_team"][team_key]["won" if is_win else "lost"] += 1
            
            # Track if this team was picked or opposed
            if any(word in selection.lower() for word in team.lower().split() if len(word) > 3):
                state["by_team"][team_key]["as_pick"] += 1
            else:
                state["by_team"][team_key]["as_opponent"] += 1
        
        # By Day of Week
        try:
            # date format: "dd/mm" - assume current year
            day, month = date_str.split("/")
            year = datetime.datetime.now().year
            dt = datetime.datetime(year, int(month), int(day))
            day_name = dt.strftime("%A")
            day_map = {
                "Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
                "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo"
            }
            day_pt = day_map.get(day_name, day_name)
        except:
            day_pt = "Unknown"
        
        if day_pt not in state["by_day"]:
            state["by_day"][day_pt] = {"won": 0, "lost": 0, "total": 0}
        state["by_day"][day_pt]["total"] += 1
        state["by_day"][day_pt]["won" if is_win else "lost"] += 1
        
        # By Side (home/away)
        side = "home" if _is_home_pick(entry) else "away"
        state["by_side"][side]["total"] += 1
        state["by_side"][side]["won" if is_win else "lost"] += 1
    
    # Compute global accuracy & ROI
    total = state["global_stats"]["total"]
    if total > 0:
        state["global_stats"]["accuracy"] = round((state["global_stats"]["won"] / total) * 100, 1)
        state["global_stats"]["roi"] = round((total_profit / total_staked) * 100, 1) if total_staked > 0 else 0.0
    
    state["current_streak"] = current_streak
    state["best_streak"] = best_streak
    state["worst_streak"] = worst_streak
    
    # ── PASS 2: GENERATE INSIGHTS & CORRECTIONS ──
    insights = []
    corrections = {"by_league": {}, "by_market": {}, "by_odds_range": {}, "by_team": {}}
    
    # League insights
    for league, data in state["by_league"].items():
        if data["total"] < MIN_SAMPLES:
            continue
        acc = (data["won"] / data["total"]) * 100
        roi = (data["profit"] / data["total"]) * 100
        
        if acc < 45:
            correction = -min(MAX_CORRECTION, int((50 - acc)))
            corrections["by_league"][league] = correction
            insights.append(f"🔴 {league}: Acerto baixo ({acc:.0f}%, {data['won']}/{data['total']}). Correção: {correction:+d}%")
        elif acc < 60:
            correction = -min(8, int((60 - acc) * 0.5))
            corrections["by_league"][league] = correction
            insights.append(f"🟡 {league}: Acerto médio ({acc:.0f}%, {data['won']}/{data['total']}). Correção: {correction:+d}%")
        elif acc >= 75:
            correction = min(5, int((acc - 70) * 0.3))
            corrections["by_league"][league] = correction
            insights.append(f"🟢 {league}: Excelente! ({acc:.0f}%, {data['won']}/{data['total']}). Boost: +{correction}%")
        
        if roi < -20:
            insights.append(f"💸 {league}: ROI negativo ({roi:.1f}%). Evitar odd agressiva nessa liga.")
    
    # Market insights
    for market, data in state["by_market"].items():
        if data["total"] < MIN_SAMPLES:
            continue
        acc = (data["won"] / data["total"]) * 100
        
        market_labels = {"ML": "Moneyline", "DC": "Dupla Chance", "OVER": "Over", "UNDER": "Under", "BTTS": "BTTS"}
        label = market_labels.get(market, market)
        
        if acc < 45:
            correction = -min(MAX_CORRECTION, int((50 - acc)))
            corrections["by_market"][market] = correction
            insights.append(f"🔴 Mercado {label}: Apenas {acc:.0f}% acerto ({data['won']}/{data['total']}). Correção: {correction:+d}%")
        elif acc >= 75:
            correction = min(5, int((acc - 70) * 0.3))
            corrections["by_market"][market] = correction
            insights.append(f"🟢 Mercado {label}: {acc:.0f}% acerto! Somos bons nisso.")
    
    # Odds range insights
    expected_accuracy = {"ultra_safe": 85, "safe": 70, "value": 58, "risky": 48, "longshot": 35}
    range_labels = {"ultra_safe": "Ultra Safe (1.01-1.30)", "safe": "Safe (1.30-1.60)", 
                    "value": "Value (1.60-2.00)", "risky": "Risky (2.00-3.00)", "longshot": "Longshot (3.00+)"}
    
    for bucket, data in state["by_odds_range"].items():
        if data["total"] < MIN_SAMPLES:
            continue
        acc = (data["won"] / data["total"]) * 100
        expected = expected_accuracy.get(bucket, 60)
        
        if acc < expected - 15:
            correction = -min(MAX_CORRECTION, int(expected - acc) // 2)
            corrections["by_odds_range"][bucket] = correction
            insights.append(f"⚠️ Faixa {range_labels[bucket]}: {acc:.0f}% vs {expected}% esperado. Superconfiante! Correção: {correction:+d}%")
        elif acc > expected + 10:
            correction = min(5, int((acc - expected) * 0.2))
            corrections["by_odds_range"][bucket] = correction
            insights.append(f"✅ Faixa {range_labels[bucket]}: {acc:.0f}% (acima dos {expected}% esperados). Boost: +{correction}%")
    
    # Team insights (problematic teams)
    for team, data in state["by_team"].items():
        if data["total"] < MIN_SAMPLES_TEAM:
            continue
        acc = (data["won"] / data["total"]) * 100
        
        if acc < 30 and data["total"] >= 3:
            correction = -min(12, int((40 - acc)))
            corrections["by_team"][team] = correction
            insights.append(f"🚫 {team.title()}: {data['won']}/{data['total']} ({acc:.0f}%). Time TÓXICO. Correção: {correction:+d}%")
        elif acc >= 85 and data["total"] >= 3:
            correction = min(5, int((acc - 80) * 0.3))
            corrections["by_team"][team] = correction
            insights.append(f"💎 {team.title()}: {data['won']}/{data['total']} ({acc:.0f}%). Time CONFIÁVEL. Boost: +{correction}%")
    
    # Side insights (home vs away)
    for side, data in state["by_side"].items():
        if data["total"] < MIN_SAMPLES:
            continue
        acc = (data["won"] / data["total"]) * 100
        side_label = "Casa" if side == "home" else "Fora"
        if acc < 45:
            insights.append(f"⚠️ Picks {side_label}: {acc:.0f}% acerto. Somos fracos em picks de {side_label.lower()}.")
        elif acc >= 75:
            insights.append(f"✅ Picks {side_label}: {acc:.0f}% acerto! Forte em {side_label.lower()}.")
    
    # Streak insight
    if current_streak >= 5:
        insights.append(f"🔥 Sequência de {current_streak} GREENS! Momento excelente.")
    elif current_streak <= -4:
        insights.append(f"❄️ Sequência de {abs(current_streak)} REDS. Reduzindo agressividade e elevando barreira de entrada.")
    
    # ── PASS 3: CALCULATE DYNAMIC THRESHOLDS ──
    # If accuracy < 75%, we raise the sniper/banker bar to be more selective
    base_sniper = 72
    base_banker = 82
    
    acc_gap = max(0, 78 - state["global_stats"]["accuracy"])
    streak_penalty = max(0, abs(min(0, current_streak)) * 2)
    
    state["thresholds"] = {
        "sniper": int(base_sniper + (acc_gap * 0.5) + streak_penalty),
        "banker": int(base_banker + (acc_gap * 0.4) + (streak_penalty * 0.5)),
        "minimum": int(60 + (acc_gap * 0.3))
    }
    
    state["thresholds"]["sniper"] = min(85, state["thresholds"]["sniper"])
    state["thresholds"]["banker"] = min(92, state["thresholds"]["banker"])
    
    insights.append(f"🎯 META 80%: Threshold Sniper ajustado para {state['thresholds']['sniper']}% (Rigidez: +{int(acc_gap + streak_penalty)})")
    
    state["insights"] = insights
    
    # ── PASS 4: DEEP MARKET & TOXICITY ANALYSIS ──
    # Identify leagues that are "Blacklisted" (ROI < -20% and 5+ games)
    blacklisted = []
    top_leagues = []
    for league, stats in state["by_league"].items():
        total = stats["total"]
        if total >= 5:
            win_rate = (stats["won"] / total) * 100
            # Calculate simple ROI if we don't have it tracked perfectly
            # Assuming avg odd 1.50
            est_roi = (stats["won"] * 0.5 - stats["lost"]) / total * 100
            
            if est_roi < -20 or win_rate < 40:
                blacklisted.append(league)
            elif est_roi > 10 or win_rate >= 75:
                top_leagues.append(league)
                
    state["blacklisted_leagues"] = blacklisted
    state["top_leagues"] = top_leagues
    
    # Identify Toxic Teams (Losses >= 3 and 0 wins)
    toxic = {}
    for team, stats in state["by_team"].items():
        if stats["total"] >= 3 and stats["won"] == 0:
            toxic[team] = "🔥 TOXIC (0% WR)"
        elif stats.get("lost", 0) > stats.get("won", 0) + 2:
            toxic[team] = "⚠️ UNRELIABLE"
            
    state["toxic_teams"] = toxic
    
    # Market Efficiency (which market is winning)
    efficiency = {}
    for mkt, stats in state["by_market"].items():
        if stats["total"] >= 10:
            efficiency[mkt] = round((stats["won"] / stats["total"]) * 100, 1)
            
    state["market_efficiency"] = efficiency
    
    state["corrections"] = corrections
    state["last_study"] = datetime.datetime.now().isoformat()
    state["total_studied"] = total
    
    _save_state(state)
    
    print(f"\n[LEARN] 🧠 AUTOCONHECIMENTO ATUALIZADO")
    print(f"[LEARN] 📊 {total} jogos estudados | Acerto: {state['global_stats']['accuracy']}% | ROI: {state['global_stats']['roi']}%")
    print(f"[LEARN] 🔥 Melhor sequência: +{best_streak} | Pior: {worst_streak}")
    print(f"[LEARN] 📝 {len(insights)} lições aprendidas:")
    for insight in insights[:10]:
        print(f"   {insight}")
    if len(insights) > 10:
        print(f"   ... e mais {len(insights) - 10} insights")
    
    return state


# ═══════════════════════════════════════
# APPLY CORRECTIONS TO NEW PREDICTIONS
# ═══════════════════════════════════════
def apply_learning_correction(prob, odd, league, selection, home_team, away_team):
    """
    Applies learned corrections to a probability estimate.
    Called during the prediction pipeline for each game.
    
    Args:
        prob: raw probability estimate (0-100)
        odd: decimal odds
        league: league name
        selection: pick text
        home_team: home team name
        away_team: away team name
    
    Returns:
        (corrected_prob, correction_notes)
    """
    state = _load_state()
    corrections = state.get("corrections", {})
    notes = []
    total_adj = 0
    
    # 1. League correction
    league_adj = corrections.get("by_league", {}).get(league, 0)
    if league_adj != 0:
        total_adj += league_adj
        notes.append(f"🧠 Liga {league}: {league_adj:+d}%")
    
    # 2. Market correction
    market = _classify_market(selection)
    market_adj = corrections.get("by_market", {}).get(market, 0)
    if market_adj != 0:
        total_adj += market_adj
        notes.append(f"🧠 Mercado {market}: {market_adj:+d}%")
    
    # 3. Odds range correction
    odds_bucket = _classify_odds_range(odd)
    odds_adj = corrections.get("by_odds_range", {}).get(odds_bucket, 0)
    if odds_adj != 0:
        total_adj += odds_adj
        notes.append(f"🧠 Faixa odds: {odds_adj:+d}%")
    
    # 4. Team correction (check both teams)
    team_corrections = corrections.get("by_team", {})
    for team in [home_team, away_team]:
        team_key = team.lower().strip()
        team_adj = team_corrections.get(team_key, 0)
        if team_adj != 0:
            # If pick is FOR this team, apply directly
            # If pick is AGAINST this team, invert
            is_picked = any(word in selection.lower() for word in team.lower().split() if len(word) > 3)
            if is_picked:
                total_adj += team_adj
                notes.append(f"🧠 {team}: {team_adj:+d}% (como pick)")
            else:
                total_adj -= team_adj
                notes.append(f"🧠 vs {team}: {-team_adj:+d}%")
    
    # 5. Cold streak protection
    if state.get("current_streak", 0) <= -4:
        # In a losing streak, be more conservative (reduce confidence)
        streak_adj = -3
        total_adj += streak_adj
        notes.append(f"❄️ Streak negativo ({state['current_streak']}): {streak_adj:+d}%")
    
    # Cap total adjustment
    total_adj = max(-MAX_CORRECTION, min(MAX_CORRECTION, total_adj))
    
    corrected = max(30, min(95, prob + total_adj))
    
    return corrected, notes


# ═══════════════════════════════════════
# GET LEARNING SUMMARY (for dashboard)
# ═══════════════════════════════════════
def get_learning_summary():
    """Returns a summary of the learning state for display."""
    state = _load_state()
    
    # Sort leagues by accuracy (worst first)
    league_rankings = []
    for league, data in state.get("by_league", {}).items():
        if data["total"] >= MIN_SAMPLES:
            acc = (data["won"] / data["total"]) * 100
            league_rankings.append({
                "league": league,
                "accuracy": round(acc, 1),
                "total": data["total"],
                "won": data["won"],
                "lost": data["lost"],
                "profit": round(data.get("profit", 0), 2),
                "status": "🟢" if acc >= 65 else ("🟡" if acc >= 50 else "🔴")
            })
    league_rankings.sort(key=lambda x: x["accuracy"])
    
    # Top/Bottom teams
    team_rankings = []
    for team, data in state.get("by_team", {}).items():
        if data["total"] >= MIN_SAMPLES_TEAM:
            acc = (data["won"] / data["total"]) * 100
            team_rankings.append({
                "team": team.title(),
                "accuracy": round(acc, 1),
                "total": data["total"],
                "won": data["won"],
            })
    team_rankings.sort(key=lambda x: x["accuracy"])
    
    return {
        "global": state.get("global_stats", {}),
        "insights": state.get("insights", []),
        "league_rankings": league_rankings,
        "team_rankings": team_rankings,
        "corrections_active": sum(
            len(v) for v in state.get("corrections", {}).values() if isinstance(v, dict)
        ),
        "streak": state.get("current_streak", 0),
        "best_streak": state.get("best_streak", 0),
        "worst_streak": state.get("worst_streak", 0),
        "last_study": state.get("last_study", "Nunca"),
        "by_market": state.get("by_market", {}),
        "by_odds_range": state.get("by_odds_range", {}),
        "by_side": state.get("by_side", {}),
        "by_day": state.get("by_day", {}),
    }


def get_active_thresholds():
    """Returns the current learned thresholds for sniper/banker."""
    state = _load_state()
    return state.get("thresholds", DEFAULT_STATE["thresholds"])


# ═══════════════════════════════════════
# CLEANUP OLD HISTORY (keep last N days)
# ═══════════════════════════════════════
def cleanup_old_history(keep_days=30):
    """
    Removes history entries older than keep_days.
    Data older than this should already be in Supabase cloud.
    Returns count of entries removed.
    """
    history = _load_history()
    if not history:
        return 0
    
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=keep_days)
    year = now.year
    
    kept = []
    removed = 0
    
    for entry in history:
        try:
            date_str = entry.get("date", "")
            day, month = date_str.split("/")
            entry_date = datetime.datetime(year, int(month), int(day))
            
            # Handle year boundary (December entries in January)
            if entry_date > now:
                entry_date = datetime.datetime(year - 1, int(month), int(day))
            
            if entry_date >= cutoff:
                kept.append(entry)
            else:
                removed += 1
        except:
            kept.append(entry)  # Keep if date is unparseable
    
    if removed > 0:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(kept, f, indent=4, ensure_ascii=False)
        print(f"[LEARN] 🧹 Limpeza: {removed} entradas antigas removidas (>{keep_days} dias). {len(kept)} mantidas.")
    
    return removed


# ═══════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 SISTEMA DE AUTOCONHECIMENTO — BOT PROBABILITY")
    print("=" * 60)
    
    # Study results
    state = study_results()
    
    # Show detailed report
    summary = get_learning_summary()
    
    print(f"\n{'='*60}")
    print("📊 RELATÓRIO DETALHADO")
    print(f"{'='*60}")
    
    print(f"\n🌐 GLOBAL:")
    g = summary["global"]
    print(f"   Total: {g.get('total', 0)} jogos | ✅ {g.get('won', 0)} | ❌ {g.get('lost', 0)}")
    print(f"   Acerto: {g.get('accuracy', 0)}% | ROI: {g.get('roi', 0)}%")
    print(f"   Streak atual: {summary['streak']} | Melhor: +{summary['best_streak']} | Pior: {summary['worst_streak']}")
    
    if summary["league_rankings"]:
        print(f"\n🏆 RANKING POR LIGA:")
        for lr in summary["league_rankings"]:
            print(f"   {lr['status']} {lr['league']}: {lr['accuracy']}% ({lr['won']}/{lr['total']})")
    
    if summary.get("by_market"):
        print(f"\n📈 POR MERCADO:")
        for market, data in summary["by_market"].items():
            if data["total"] > 0:
                acc = (data["won"] / data["total"]) * 100
                print(f"   {market}: {acc:.0f}% ({data['won']}/{data['total']})")
    
    print(f"\n🔧 Correções ativas: {summary['corrections_active']}")
    print(f"📅 Último estudo: {summary['last_study']}")

def get_learning_state():
    """
    Exposes the full current learning state for other modules.
    """
    try:
        if os.path.exists(LEARNING_STATE_FILE):
            with open(LEARNING_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return DEFAULT_STATE.copy()
