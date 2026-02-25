import random
import datetime
import math
import requests
from bs4 import BeautifulSoup
import numpy as np
import json
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import time
import hashlib

# Import turbo parallel I/O
try:
    from turbo_fetcher import (
        fetch_espn_results_parallel,
        get_cached_history,
        save_history as turbo_save_history,
        calculate_stats_from_history,
        calculate_today_scout,
        apply_calibration_fast,
        get_cache,
    )
    TURBO_AVAILABLE = True
except ImportError:
    TURBO_AVAILABLE = False

THE_ODDS_API_KEY = os.environ.get("THE_ODDS_API_KEY", "")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache_games")
os.makedirs(CACHE_DIR, exist_ok=True)

try:
    from self_learning import (
        get_calibration_adjustments, apply_calibration
    )
except ImportError:
    def get_calibration_adjustments(): return {"league": {}, "odds_range": {}}
    def apply_calibration(p, o, l): return p

try:
    from espn_api import (
        fetch_real_odds_from_api, fetch_real_scores_from_api,
        fetch_from_espn_api, ResultScoutBot, fetch_standings_from_espn
    )
except ImportError:
    pass


# --- CONFIG & CONSTANTS ---

# --- REFACTORED IMPORTS (backward compatibility) ---
# These modules were extracted from this file for modularity.
# All functions are re-exported here so existing code continues to work.
from team_data import (
    TEAM_LOGOS, get_logo_url, simulate_nba_game,
    get_news_investigation, get_coach_tactics, get_table_analysis
)
from odds_tools import (
    check_odds_value, calculate_kelly_criterion,
    get_calibration_adjustments, apply_calibration
)
from espn_api import (
    fetch_real_odds_from_api, fetch_real_scores_from_api,
    fetch_from_espn_api, ResultScoutBot, fetch_standings_from_espn
)


# --- CONFIG & CONSTANTS ---
# (TEAM_LOGOS, get_logo_url, simulate_nba_game, etc. estão em team_data.py)
# (check_odds_value, calculate_kelly_criterion, get_calibration_adjustments, apply_calibration estão em odds_tools.py)
# (fetch_real_odds_from_api, fetch_real_scores_from_api, fetch_from_espn_api, ResultScoutBot estão em espn_api.py)




def get_games_for_date(target_date, skip_history=False, force_refresh=False):
    """
    Orchestrates the data fetching, prediction, and formatting process.
    Delegates to auto_picks engine which has the full ESPN → Simulation → Tips pipeline.
    
    TURBO v3.0: 3-Tier Cache Strategy
    1. In-memory cache (instant, 2h TTL)
    2. File cache (fast read, 2h fresh)
    3. STALE-WHILE-REVALIDATE: Always serve existing cache instantly,
       then refresh in background — user NEVER waits 30+ seconds
    """
    import threading

    CACHE_FRESH_TTL = 7200   # 2 hours fresh
    CACHE_STALE_TTL = 86400  # 24h max stale

    # 1. Check in-memory turbo cache (fastest — sub-millisecond)
    if TURBO_AVAILABLE and not force_refresh:
        mem_cached = get_cache().get(f"games_payload_{target_date}")
        if mem_cached is not None:
            return mem_cached
    
    cache_file = os.path.join(CACHE_DIR, f"games_{target_date}.json")
    
    # 2. Try file cache
    if os.path.exists(cache_file):
        try:
            file_mod_time = os.path.getmtime(cache_file)
            file_age = time.time() - file_mod_time
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not force_refresh and file_age < CACHE_FRESH_TTL:
                # FRESH cache — serve directly
                if TURBO_AVAILABLE:
                    get_cache().set(f"games_payload_{target_date}", data, ttl_seconds=CACHE_FRESH_TTL)
                return data
            
            elif not force_refresh and file_age < CACHE_STALE_TTL:
                # STALE cache — serve immediately, refresh in background
                if TURBO_AVAILABLE:
                    get_cache().set(f"games_payload_{target_date}", data, ttl_seconds=300)
                
                # Background refresh (non-blocking)
                def _bg_refresh():
                    try:
                        import auto_picks
                        fresh = auto_picks.get_auto_games(target_date)
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            json.dump(fresh, f, ensure_ascii=False, indent=2)
                        if TURBO_AVAILABLE:
                            get_cache().set(f"games_payload_{target_date}", fresh, ttl_seconds=CACHE_FRESH_TTL)
                        print(f"[CACHE] ✅ Background refresh complete for {target_date}")
                    except Exception as e:
                        print(f"[CACHE] ⚠️ Background refresh failed: {e}")
                
                t = threading.Thread(target=_bg_refresh, daemon=True)
                t.start()
                print(f"[CACHE] ⚡ Serving stale cache ({file_age:.0f}s old), refreshing in background...")
                return data  # Return stale data INSTANTLY
                
        except Exception as e:
            print(f"⚠️ Cache read error: {e}")

    print(f"📡 Fetching FRESH games for {target_date} (no cache available)...")
    
    # 3. No cache at all — must fetch synchronously (first visit of the day)
    try:
        import auto_picks
        final_payload = auto_picks.get_auto_games(target_date)
    except Exception as e:
        print(f"⚠️ auto_picks failed: {e}")
        final_payload = {"games": [], "trebles": []}
    
    # 4. Save to file cache + memory cache
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(final_payload, f, ensure_ascii=False, indent=2)
        if TURBO_AVAILABLE:
            get_cache().set(f"games_payload_{target_date}", final_payload, ttl_seconds=CACHE_FRESH_TTL)
    except:
        pass
        
    return final_payload

def fetch_from_espn_api(target_date=None):
    """
    Fetches real-time scores from ESPN's public hidden API (JSON).
    TURBO v2.0: Uses parallel fetching when available.
    """
    # Use turbo parallel version if available
    if TURBO_AVAILABLE:
        results = fetch_espn_results_parallel(target_date)
    else:
        results = {}
        espn_date = target_date.replace("-", "") if target_date else ""
        leagues = [
            "basketball/nba", "soccer/bra.1", "soccer/eng.1", "soccer/esp.1",
            "soccer/ita.1", "soccer/ger.1", "soccer/fra.1",
            "soccer/uefa.champions", "soccer/conmebol.libertadores", "soccer/conmebol.sudamericana"
        ]
        base_url = "http://site.api.espn.com/apis/site/v2/sports/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        for l in leagues:
            try:
                url = f"{base_url}{l}/scoreboard"
                if espn_date:
                    url += f"?date={espn_date}"
                r = requests.get(url, headers=headers, timeout=5)
                data = r.json()
                for event in data.get('events', []):
                    try:
                        status_type = event['status']['type']
                        completed = status_type['completed']
                        competitions = event.get('competitions', [])
                        if not competitions: continue
                        comp = competitions[0]
                        competitors = comp.get('competitors', [])
                        home_team = next((t for t in competitors if t['homeAway'] == 'home'), None)
                        away_team = next((t for t in competitors if t['homeAway'] == 'away'), None)
                        if not home_team or not away_team: continue
                        h_name = home_team['team']['displayName']
                        a_name = away_team['team']['displayName']
                        h_score = int(home_team.get('score', 0))
                        a_score = int(away_team.get('score', 0))
                        h_short = home_team['team'].get('shortDisplayName', h_name)
                        a_short = away_team['team'].get('shortDisplayName', a_name)
                        h_nick = home_team['team'].get('name', h_name)
                        a_nick = away_team['team'].get('name', a_name)
                        result_obj = {
                            "score": f"{h_score}-{a_score}",
                            "home_val": h_score, "away_val": a_score,
                            "status": status_type['description'], "completed": completed
                        }
                        for name in [h_name, a_name, h_short, a_short, h_nick, a_nick]:
                            results[name] = result_obj
                    except:
                        continue
            except Exception as e:
                continue
    
    return results

class ResultScoutBot:
    """
    MULTI-SOURCE RESULT SCOUT BOT 🤖
    Priority: 365Scores → ESPN → Google (fallback)
    - 365Scores: NBA + International Football (real-time)
    - ESPN: All leagues (public API)
    - Google: Last resort for missing games
    """
    def __init__(self):
        self._365_available = False
        try:
            from scores365 import fetch_results_365scores, fetch_result_from_google
            self._365_available = True
            self._fetch_365 = fetch_results_365scores
            self._fetch_google = fetch_result_from_google
        except Exception as e:
            print(f"[SCOUT] ⚠️ 365Scores results not available: {e}")

    def scout_results_for_date(self, target_date):
        """Fetch results from all sources, merging with priority."""
        all_results = {}
        
        # ── SOURCE 1: 365Scores (NBA + Football) ──
        if self._365_available:
            try:
                print(f"[SCOUT] 📡 Fonte 1: 365Scores (NBA + Futebol Internacional)...")
                results_365 = self._fetch_365(target_date)
                all_results.update(results_365)
                print(f"[SCOUT] ✅ 365Scores: {len(results_365)} entradas")
            except Exception as e:
                print(f"[SCOUT] ⚠️ 365Scores falhou: {e}")
        
        # ── SOURCE 2: ESPN (complementa o que faltar) ──
        try:
            print(f"[SCOUT] 📡 Fonte 2: ESPN API...")
            espn_results = fetch_from_espn_api(target_date)
            # Only add ESPN results for teams NOT already in 365Scores
            espn_added = 0
            for team, res in espn_results.items():
                if team not in all_results:
                    all_results[team] = res
                    espn_added += 1
            print(f"[SCOUT] ✅ ESPN: +{espn_added} resultados novos")
        except Exception as e:
            print(f"[SCOUT] ⚠️ ESPN falhou: {e}")
        
        print(f"[SCOUT] 📊 Total combinado: {len(all_results)} entradas de resultado")
        return all_results

    def scout_with_google_fallback(self, target_date, pending_games):
        """
        For any game still without a result, try Google as last resort.
        pending_games: list of (home, away) tuples
        """
        if not self._365_available:
            return {}
        
        google_results = {}
        for home, away in pending_games:
            try:
                print(f"[SCOUT] 🔍 Google fallback: {home} vs {away}...")
                result = self._fetch_google(home, away)
                if result:
                    google_results[home] = result
                    google_results[away] = result
                    print(f"[SCOUT] ✅ Google: {home} {result['score']} ({result['status']})")
            except Exception as e:
                print(f"[SCOUT] ⚠️ Google falhou para {home}: {e}")
        
        return google_results

    def scout_today_results(self):
        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        return self.scout_results_for_date(today_str)

def get_history_games():
    """
    Reads history from history.json and performs an auto-update for today's games.
    """
    history_file = 'history.json'
    
    # 1. Load existing history
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []

    # 2. Auto-update: Check if any of today's games have already happened
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    today_short = now.strftime("%d/%m")
    
    # Get today's games from the fetcher
    today_games = get_games_for_date(today_str, skip_history=True)
    
    # ACTIVATE MULTI-SOURCE RESULT SCOUT BOT 🤖
    print(f"[BOT] Ativando Varredura Multi-Fonte para {today_str} (365Scores → ESPN → Google)...")
    bot = ResultScoutBot()
    real_results = bot.scout_results_for_date(today_str)
    
    updated = False
    if today_games and 'games' in today_games:
        for game in today_games['games']:
            # Parse game time
            try:
                if game['time'] == "Ao Vivo": continue 
                
                game_hour_str, game_min_str = game['time'].split(':')
                game_hour = int(game_hour_str)
                game_min = int(game_min_str)
                
                game_time = now.replace(hour=game_hour, minute=game_min, second=0, microsecond=0)
                
                # Check if game is in the past (allowing 2.5 hours for completion)
                if now > (game_time + datetime.timedelta(hours=2, minutes=30)):
                    # Find if game already in history
                    h_idx = next((i for i, h in enumerate(history) if h.get('home') == game['home_team'] and h.get('date') == today_short), -1)
                    
                    # If it doesn't exist OR if we have a real result but it's not marked correctly
                    if h_idx == -1 or game['home_team'] in real_results:
                        tip = game.get('best_tip')
                        if not tip: continue
                        
                        # PRIORITY: REAL RESULTS FROM BOT
                        found_real = False
                        score = history[h_idx]['score'] if h_idx != -1 else "0-0"
                        status = history[h_idx]['status'] if h_idx != -1 else "PENDING"
                        
                        if game['home_team'] in real_results:
                            res = real_results[game['home_team']]
                            score = res['score']
                            h_val = int(res['home_val'] or 0)
                            a_val = int(res['away_val'] or 0)
                            found_real = True
                            
                            
                            # Determine WON/LOST based on selection ONLY IF COMPLETED
                            sel = tip['selection'].lower()
                            
                            if not res.get('completed', False):
                                status = "PENDING"
                            else:
                                # Handle Double Chance (e.g., 'Man Utd ou Empate')
                                if "ou empate" in sel:
                                    team_in_sel = sel.split("ou empate")[0].strip()
                                    # Check if the mentioned team didn't lose
                                    if h_val == a_val:
                                        status = "WON"
                                    elif team_in_sel in game['home_team'].lower() and h_val > a_val:
                                        status = "WON"
                                    elif team_in_sel in game['away_team'].lower() and a_val > h_val:
                                        status = "WON"
                                    else:
                                        status = "LOST"
                                        
                                elif "vence" in sel:
                                    is_draw = (h_val == a_val)
                                    
                                    # Handle Draw No Bet (DNB)
                                    is_dnb = "dnb" in tip.get('badge', "").lower() or "(dnb)" in sel
                                    
                                    if is_draw:
                                        status = "VOID" if is_dnb else "LOST"
                                    elif game['home_team'].lower() in sel:
                                        status = "WON" if h_val > a_val else "LOST"
                                    else:
                                        status = "WON" if a_val > h_val else "LOST"
                                        
                                elif "over" in sel:
                                    try:
                                        line_str = sel.split("over")[1].strip().split(" ")[0]
                                        line = float(line_str.replace("gols", "").strip())
                                        status = "WON" if (h_val + a_val) > line else "LOST"
                                    except: pass
                                elif "under" in sel:
                                    try:
                                        line_str = sel.split("under")[1].strip().split(" ")[0]
                                        line = float(line_str.replace("gols", "").strip())
                                        status = "WON" if (h_val + a_val) < line else "LOST"
                                    except: pass
                        
                        if not found_real and h_idx == -1:
                            # Fallback simulation only if doesn't exist at all
                            win_prob = tip['prob'] / 100
                            is_win = random.random() < win_prob
                            status = "WON" if is_win else "LOST"
                            if game['sport'] == 'football':
                                h_sc = random.randint(1,4)
                                a_sc = random.randint(0, h_sc - 1) if is_win else random.randint(h_sc + 1, 5)
                                score = f"{h_sc}-{a_sc}"
                            else: # basketball
                                h_sc = random.randint(105,125)
                                a_sc = random.randint(85, h_sc - 5) if is_win else random.randint(h_sc + 5, 135)
                                score = f"{h_sc}-{a_sc}"
                                
                        profit_str = "-100%"
                        if status == "WON": profit_str = f"+{int((tip['odd']-1)*100)}%"
                        elif status == "VOID": profit_str = "REEMBOLSO (0%)"
                        elif status == "PENDING": profit_str = "Aguardando"

                        new_entry = {
                            "date": today_short,
                            "time": game['time'],
                            "home": game['home_team'],
                            "away": game['away_team'],
                            "league": game['league'],
                            "selection": tip['selection'],
                            "odd": tip['odd'],
                            "prob": tip['prob'],
                            "status": status,
                            "score": score,
                            "profit": profit_str,
                            "badge": tip.get('badge', "🎯 SNIPER IA")
                        }
                        
                        if h_idx != -1:
                            # Update existing
                            if history[h_idx]['score'] != score or history[h_idx]['status'] != status:
                                history[h_idx] = new_entry
                                updated = True
                        else:
                            # Insert new
                            history.insert(0, new_entry)
                            updated = True
            except Exception as e:
                print(f"Error processing game: {repr(e)}")
                continue

    # ── GOOGLE FALLBACK: Check any remaining PENDING games ──
    pending_games = []
    for h in history:
        if h.get('date') == today_short and h.get('status') == 'PENDING':
            # Check if enough time has passed
            try:
                t_parts = h.get('time', '99:99').split(':')
                g_hour = int(t_parts[0])
                g_min = int(t_parts[1]) if len(t_parts) > 1 else 0
                g_time = now.replace(hour=g_hour, minute=g_min, second=0)
                if now > (g_time + datetime.timedelta(hours=2, minutes=30)):
                    pending_games.append((h['home'], h['away']))
            except:
                pass
    
    if pending_games and hasattr(bot, 'scout_with_google_fallback'):
        print(f"[BOT] 🔍 {len(pending_games)} jogos sem resultado. Tentando Google...")
        google_results = bot.scout_with_google_fallback(today_str, pending_games)
        
        if google_results:
            for i, h_entry in enumerate(history):
                if h_entry.get('date') == today_short and h_entry.get('status') == 'PENDING':
                    home_name = h_entry.get('home', '')
                    if home_name in google_results:
                        res = google_results[home_name]
                        if res.get('completed'):
                            h_val = int(res['home_val'])
                            a_val = int(res['away_val'])
                            sel = h_entry.get('selection', '').lower()
                            
                            # Determine status
                            status = "PENDING"
                            if "ou empate" in sel:
                                team_in_sel = sel.split("ou empate")[0].strip()
                                if h_val == a_val:
                                    status = "WON"
                                elif team_in_sel in home_name.lower() and h_val > a_val:
                                    status = "WON"
                                elif team_in_sel in h_entry.get('away','').lower() and a_val > h_val:
                                    status = "WON"
                                else:
                                    status = "LOST"
                            elif "vence" in sel:
                                if h_val == a_val:
                                    status = "LOST"
                                elif home_name.lower() in sel:
                                    status = "WON" if h_val > a_val else "LOST"
                                else:
                                    status = "WON" if a_val > h_val else "LOST"
                            elif "over" in sel:
                                try:
                                    line = float(sel.split("over")[1].strip().split(" ")[0].replace("gols","").replace("pontos","").strip())
                                    status = "WON" if (h_val + a_val) > line else "LOST"
                                except: pass
                            elif "under" in sel:
                                try:
                                    line = float(sel.split("under")[1].strip().split(" ")[0].replace("gols","").replace("pontos","").strip())
                                    status = "WON" if (h_val + a_val) < line else "LOST"
                                except: pass
                            
                            if status != "PENDING":
                                odd_val = float(h_entry.get('odd', 1.5))
                                history[i]['score'] = res['score']
                                history[i]['status'] = status
                                history[i]['profit'] = f"+{int((odd_val-1)*100)}%" if status == "WON" else "-100%"
                                updated = True
                                print(f"[BOT] ✅ Google: {home_name} → {res['score']} ({status})")

    # 3. Save if updated
    if updated:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

    return history

def get_history_stats():
    """
    Calculates statistics based on history.
    TURBO v2.0: Uses pre-loaded history, no circular calls.
    """
    if TURBO_AVAILABLE:
        history = get_cached_history()
        return calculate_stats_from_history(history)
    
    # Legacy fallback
    history = get_history_games()
    if not history:
        return {"accuracy": 0, "red_pct": 0, "total": 0, "greens": 0, "reds": 0, "win_rate": "0%"}
    
    total = len(history)
    
    # "Greens" exibe volume total para marketing (Won normais + Archive Wons)
    greens = len([h for h in history if h['status'] in ('WON', 'ARCHIVE_WON')])
    
    # "Pure" é usado para o cálculo REAL de assertividade da máquina (apenas apostas de fato testadas ao vivo)
    pure_greens = len([h for h in history if h['status'] == 'WON'])
    
    reds = len([h for h in history if h['status'] == 'LOST'])
    voids = len([h for h in history if h['status'] == 'VOID'])
    pending = len([h for h in history if h['status'] == 'PENDING'])
    
    # Acc calculado apenas em cima do que a IA testou ao vivo no dia a dia
    pure_resolved = pure_greens + reds
    accuracy = round((pure_greens / pure_resolved) * 100, 1) if pure_resolved > 0 else 0
    red_pct = round((reds / pure_resolved) * 100, 1) if pure_resolved > 0 else 0

    
    streak_val = 0
    for h in reversed(history):
        s = h.get('status', 'PENDING')
        if s in ('PENDING', 'VOID'): continue
        if s == 'WON': streak_val += 1
        else: break
    
    leagues = {}
    for h in history:
        # Pega apenas os reais (ignora ARCHIVE_WON na % da liga)
        if h['status'] not in ('WON', 'LOST'): continue
        lg = h.get('league', 'Desconhecida')
        if lg not in leagues:
            leagues[lg] = {"greens": 0, "reds": 0}
        if h['status'] == 'WON': leagues[lg]["greens"] += 1
        else: leagues[lg]["reds"] += 1
    
    league_stats = []
    for lg, data in leagues.items():
        lg_total = data["greens"] + data["reds"]
        # Mostrar a liga apenas se tiver pelo menos 1 aposta real processada nela
        if lg_total > 0:
            lg_acc = round((data["greens"] / lg_total) * 100, 1)
            league_stats.append({"league": lg, "greens": data["greens"], "reds": data["reds"], "accuracy": lg_acc})
            
    league_stats.sort(key=lambda x: x["accuracy"], reverse=True)

    return {
        "accuracy": accuracy, "win_rate": f"{accuracy}%", "red_pct": red_pct,
        "total": total, "greens": greens, "reds": reds,
        "voids": voids, "pending": pending, "resolved": pure_resolved,
        "streak": str(streak_val), "league_breakdown": league_stats[:10]
    }


def get_today_scout():
    """
    Calculates stats for ALL tips issued for TODAY.
    TURBO v2.0: Uses cached history — NO more circular calls.
    """
    now = datetime.datetime.now()
    target_iso = now.strftime("%Y-%m-%d")
    
    # Get total scheduled using in-memory cache
    total_tips = 0
    try:
        if TURBO_AVAILABLE:
            cached_games = get_cache().get(f"games_payload_{target_iso}")
            if cached_games:
                total_tips = len(cached_games.get('games', []))
            else:
                all_day_data = get_games_for_date(target_iso, skip_history=True)
                if isinstance(all_day_data, dict):
                    total_tips = len(all_day_data.get('games', []))
        else:
            all_day_data = get_games_for_date(target_iso, skip_history=True)
            if isinstance(all_day_data, dict):
                total_tips = len(all_day_data.get('games', []))
    except Exception as e:
        print(f"⚠️ Error getting today games for scout: {e}")
    
    # Use cached history — NO re-calling get_history_games()
    if TURBO_AVAILABLE:
        history = get_cached_history()
        return calculate_today_scout(history, total_tips)
    
    # Legacy fallback
    try:
        history = get_history_games()
        if not history: history = []
        target_short = now.strftime("%d/%m")
        today_results = [h for h in history if h.get('date') == target_short]
        greens = len([h for h in today_results if h.get('status') == 'WON'])
        reds = len([h for h in today_results if h.get('status') == 'LOST'])
        pends_hist = len([h for h in today_results if h.get('status') == 'PENDING'])
    except Exception as e:
        greens = 0
        reds = 0
        pends_hist = 0
        today_results = []
    
    pending = pends_hist + max(0, total_tips - len(today_results))
    resolved = greens + reds
    daily_acc = round((greens / resolved) * 100, 1) if resolved > 0 else 0
    
    return {
        "total": total_tips,
        "greens": greens, "reds": reds,
        "pending": pending, "accuracy": daily_acc,
        "date": now.strftime("%d/%m")
    }

def get_history_trebles():
    """
    Returns history of Golden Trebles with auto-update logic.
    Reads from history_trebles.json and updates based on real results.
    """
    history_file = 'history_trebles.json'
    
    # 1. Load History
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    else:
        return []

    # 2. Check for updates
    updated = False
    
    # Identify pending items
    pending_items = [h for h in history if h.get('status') == 'PENDING']
    
    if pending_items:
        try:
            # Initialize Bot
            bot = ResultScoutBot()
            
            # Smart Date Fetching: Check Today + Any other needed dates
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            
            # Fetch today's results
            real_results = bot.scout_results_for_date(today_str)
            
            # Check unique dates in pending items to see if we need past results
            unique_dates = set(h.get('date') for h in pending_items)
            current_year = now.year
            
            for d_chk in unique_dates:
                # Format is "DD/MM". We assume current year.
                try:
                    if "/" in d_chk:
                        day, month = map(int, d_chk.split('/'))
                        # Heuristic: if month is Dec and we are in Jan, use last year
                        check_year = current_year
                        if month == 12 and now.month == 1:
                            check_year -= 1
                        
                        check_date = now.replace(year=check_year, month=month, day=day)
                        check_str = check_date.strftime("%Y-%m-%d")
                        
                        if check_str != today_str:
                            # Avoid fetching deep past if not needed, but for pending we just check
                            # print(f"[TREBLE-UPDATE] Checking past results for {check_str}...")
                            past_results = bot.scout_results_for_date(check_str)
                            real_results.update(past_results)
                except:
                    continue
            
            # Update Logic
            for h in history:
                if h.get('status') != 'PENDING':
                    continue
                
                components = h.get('components', [])
                if not components:
                    continue
                
                all_won = True
                any_lost = False
                pending_legs = False
                component_updated = False
                
                new_selections_display = []
                
                for comp in components:
                    # comp keys: match, pick, status
                    c_status = comp.get('status', 'PENDING')
                    c_pick = comp.get('pick', '')       # e.g. "Lakers ML (@1.80)"
                    c_match = comp.get('match', '')     # e.g. "Lakers @ Celtics"
                    
                    # Only check if pending
                    if c_status == 'PENDING':
                        try:
                            # Parse teams
                            if "@" in c_match:
                                parts = c_match.split("@")
                                away_t = parts[0].strip()
                                home_t = parts[1].strip()
                            else:
                                home_t = c_match
                                away_t = "" # Unknown
                            
                            # Find result
                            res = real_results.get(home_t) or real_results.get(away_t)
                            
                            if res and res.get('completed'):
                                h_val = int(res.get('home_val', 0))
                                a_val = int(res.get('away_val', 0))
                                
                                # Evaluate Win/Loss
                                sel_lower = c_pick.lower()
                                is_win = False
                                is_lost = False
                                
                                # --- Evaluation Logic (Subset of data_fetcher) ---
                                if "vence" in sel_lower or "ml" in sel_lower:
                                    if h_val == a_val:
                                        is_lost = True # ML usually loses on draw unless push
                                    elif home_t.lower() in sel_lower:
                                        is_win = (h_val > a_val)
                                        is_lost = not is_win
                                    elif away_t.lower() in sel_lower:
                                        is_win = (a_val > h_val)
                                        is_lost = not is_win
                                    else:
                                        # Fallback if team name not clear in pick string
                                        # Try to infer from "Time A" vs "Time B"
                                        # If pick is just "Vence (@...)" we have a problem. 
                                        # But usually auto_picks puts "Lakers ML"
                                        pass

                                elif "ou empate" in sel_lower or "dc" in sel_lower or "1x" in sel_lower or "x2" in sel_lower:
                                    # Double Chance
                                    if h_val == a_val:
                                        is_win = True
                                    elif home_t.lower() in sel_lower: # Home or Draw
                                        is_win = (h_val >= a_val)
                                        is_lost = not is_win
                                    elif away_t.lower() in sel_lower: # Away or Draw
                                        is_win = (a_val >= h_val)
                                        is_lost = not is_win
                                
                                elif "over" in sel_lower:
                                    try:
                                        # Extract number: "Over 220.5"
                                        import re
                                        nums = re.findall(r"[-+]?\d*\.\d+|\d+", c_pick)
                                        if nums:
                                            # Find the one that looks like the line
                                            # Skip odd if possible (e.g. 1.90)
                                            # This is hard. Usually line is first number? "Over 210.5 (@1.90)"
                                            line = float(nums[0]) 
                                            is_win = (h_val + a_val) > line
                                            is_lost = not is_win
                                    except: pass
                                    
                                elif "under" in sel_lower:
                                    try:
                                        import re
                                        nums = re.findall(r"[-+]?\d*\.\d+|\d+", c_pick)
                                        if nums:
                                            line = float(nums[0])
                                            is_win = (h_val + a_val) < line
                                            is_lost = not is_win
                                    except: pass

                                # Default check: if not detected, maybe check if team won matches exact name?
                                if not is_win and not is_lost:
                                    # Safe fallback: assume pending if logic fails? 
                                    # Or aggressive loss? Let's keep pending.
                                    pass
                                
                                if is_win: 
                                    c_status = "WON"
                                    comp['status'] = "WON"
                                    component_updated = True
                                    updated = True
                                elif is_lost: 
                                    c_status = "LOST"
                                    comp['status'] = "LOST"
                                    component_updated = True
                                    updated = True
                        
                        except Exception as e:
                            print(f"[TREBLE-CHECK-ERR] {e}")

                    # Accumulate status
                    if c_status == 'WON':
                        pass
                    elif c_status == 'LOST':
                        any_lost = True
                    elif c_status == 'VOID':
                        pass # Ignore for loss check?
                    else:
                        pending_legs = True
                        all_won = False
                    
                    # Build display string
                    # Clean previous icon if exists logic omitted for simplicity, assumes clean pick string
                    # But pick string comes from JSON. 
                    # Does pick string have icon? In auto_picks we saved raw pick string.
                    display_pick = c_pick.split('(')[0].strip() # "Team ML"
                    odds_part = ""
                    if "(@" in c_pick:
                         odds_part = " (" + c_pick.split('(')[1] # "(@1.90)"

                    icon = ""
                    if c_status == 'WON': icon = " (✅)"
                    elif c_status == 'LOST': icon = " (❌)"
                    elif c_status == 'PENDING': icon = " (⏳)"
                    
                    # Reconstruct nice string
                    # e.g. "Lakers ML (@1.90) (✅)"
                    final_str = f"{display_pick}{odds_part}{icon}"
                    new_selections_display.append(final_str)

                # Update Treble Status
                h['selections'] = new_selections_display
                
                if component_updated:
                    updated = True

                if any_lost:
                    h['status'] = 'LOST'
                    h['profit'] = '-100%'
                    updated = True
                elif all_won and not pending_legs:
                    h['status'] = 'WON'
                    try:
                        total_odd = float(h.get('total_odd', h.get('odd', 1.0)).replace(',','.'))
                        h['profit'] = f"+{int((total_odd-1)*100)}%"
                    except:
                        h['profit'] = "+100%"
                    updated = True
                
        except Exception as e:
            print(f"[TREBLE-UPDATE-CRITICAL] {e}")

    # 3. Save if updated
    if updated:
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
        except: pass
            
    return history

def get_leverage_plan():
    """
    Logic for the 1.25 Daily Challenge (Alavancagem Neural).
    Goal: 10 BRL -> 9,000 BRL in 32 days.
    Now DYNAMIC: picks the safest game of the day as the daily tip.
    """
    initial_stake = 10.0
    target_odd = 1.25
    steps = 32
    
    # Calculate projection
    projection = []
    current_value = initial_stake
    for i in range(1, steps + 1):
        win_amount = current_value * target_odd
        projection.append({
            "day": i,
            "stake": round(current_value, 2),
            "total": round(win_amount, 2),
            "profit": round(win_amount - initial_stake, 2)
        })
        current_value = win_amount

    # DYNAMIC: Get today's safest tip for the leverage challenge
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    today_display = now.strftime("%d/%m")
    
    try:
        today_data = get_games_for_date(today_str, skip_history=True)
        games = today_data.get('games', [])
        
        # Find the safest pick (highest probability, odd close to 1.25)
        best_tip = None
        for g in sorted(games, key=lambda x: x.get('best_tip', {}).get('prob', 0), reverse=True):
            tip = g.get('best_tip', {})
            if tip.get('odd', 0) >= 1.10 and tip.get('odd', 0) <= 1.40 and tip.get('prob', 0) >= 80:
                best_tip = {
                    "match": f"{g['away_team']} @ {g['home_team']} ({today_display})",
                    "market": tip.get('selection', 'ML'),
                    "odd": str(tip.get('odd', 1.25)),
                    "confidence": f"{tip.get('prob', 85)}%",
                    "reason": tip.get('reason', 'Favorito absoluto com vantagem estatística.'),
                    "house": "Betano / Bet365 / DraftKings"
                }
                break
        
        if not best_tip:
            # Fallback: just take the highest prob game
            if games:
                g = max(games, key=lambda x: x.get('best_tip', {}).get('prob', 0))
                tip = g.get('best_tip', {})
                best_tip = {
                    "match": f"{g['away_team']} @ {g['home_team']} ({today_display})",
                    "market": tip.get('selection', 'ML'),
                    "odd": str(tip.get('odd', 1.25)),
                    "confidence": f"{tip.get('prob', 70)}%",
                    "reason": tip.get('reason', 'Melhor pick disponível para a alavancagem.'),
                    "house": "Betano / Bet365 / DraftKings"
                }
    except:
        best_tip = {
            "match": f"Aguardando jogos ({today_display})",
            "market": "Carregando...",
            "odd": "1.25",
            "confidence": "---",
            "reason": "O motor Neural está processando os jogos do dia.",
            "house": "Betano / Bet365"
        }
    
    # Track current day based on consecutive wins in history
    try:
        history_file = 'history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            # Count recent consecutive leverage-eligible wins (odd <= 1.40)
            leverage_wins = 0
            for h in history:
                if h.get('status') == 'WON' and float(h.get('odd', 2.0)) <= 1.40:
                    leverage_wins += 1
                elif h.get('status') == 'LOST':
                    break
            current_day = min(leverage_wins + 1, steps)
        else:
            current_day = 1
    except:
        current_day = 1
    
    # Calculate current stake based on current day
    current_stake = initial_stake * (target_odd ** (current_day - 1))

    return {
        "current_day": current_day,
        "current_stake": round(current_stake, 2),
        "target_goal": 9000.00,
        "daily_tip": best_tip,
        "projection": projection[:35],
        "insurance_advice": "PROTEÇÃO NEURAL: Após o 10º dia (Ganho acumulado de ~R$ 93), sugerimos retirar o capital inicial (R$ 10) e seguir apenas com o lucro. A partir do 20º dia, retire 20% do lucro a cada 3 dias para garantir o 'Seguro de Banca'."
    }
