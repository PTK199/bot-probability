"""
turbo_fetcher.py — MOTOR TURBO DE BUSCA PARALELA ⚡
====================================================
Centraliza TODAS as chamadas HTTP externas em threads paralelas.
Elimina o gargalo #1 (chamadas sequenciais) do sistema.

Componentes acelerados:
  1. ESPN Schedule Fetch (10 ligas → paralelo)
  2. 365Scores Intelligence (N jogos → paralelo)  
  3. Google News Agent (N times → paralelo)
  4. ESPN Results (10 ligas → paralelo)
  5. In-memory cache com TTL (evita re-fetch)

Performance: ~80s sequencial → ~8-12s paralelo (8-10x speedup)
"""

import time
import datetime
import requests
import threading
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import json

# Fix Windows terminal encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ═══════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════

MAX_WORKERS_ESPN = 10      # All 10 leagues in parallel
MAX_WORKERS_365 = 6        # Up to 6 game details in parallel
MAX_WORKERS_NEWS = 5       # Up to 5 news searches in parallel
MAX_WORKERS_RESULTS = 10   # All result endpoints in parallel
HTTP_TIMEOUT = 6           # Seconds per request (reduced from 8)

ESPN_BASE = "http://site.api.espn.com/apis/site/v2/sports/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ═══════════════════════════════════════════════════
# IN-MEMORY CACHE (Thread-Safe, TTL-based)
# ═══════════════════════════════════════════════════

class TurboCache:
    """Thread-safe in-memory cache with TTL."""
    
    def __init__(self):
        self._store = {}   # key -> (data, expiry_timestamp)
        self._lock = threading.Lock()
        self._stats = {"hits": 0, "misses": 0}
    
    def get(self, key):
        with self._lock:
            if key in self._store:
                data, expiry = self._store[key]
                if time.time() < expiry:
                    self._stats["hits"] += 1
                    return data
                else:
                    del self._store[key]
            self._stats["misses"] += 1
            return None
    
    def set(self, key, data, ttl_seconds=900):
        with self._lock:
            self._store[key] = (data, time.time() + ttl_seconds)
    
    def invalidate(self, pattern=""):
        """Remove all keys matching pattern."""
        with self._lock:
            if not pattern:
                self._store.clear()
            else:
                keys_to_remove = [k for k in self._store if pattern in k]
                for k in keys_to_remove:
                    del self._store[k]
    
    def stats(self):
        return {**self._stats, "entries": len(self._store)}


# Global cache instance
_cache = TurboCache()


def get_cache():
    return _cache


# ═══════════════════════════════════════════════════
# 1. PARALLEL ESPN SCHEDULE FETCH (10x faster)
# ═══════════════════════════════════════════════════

LEAGUES = [
    {"name": "NBA", "endpoint": "basketball/nba/scoreboard", "sport": "basketball"},
    {"name": "Premier League", "endpoint": "soccer/eng.1/scoreboard", "sport": "football"},
    {"name": "La Liga", "endpoint": "soccer/esp.1/scoreboard", "sport": "football"},
    {"name": "Serie A", "endpoint": "soccer/ita.1/scoreboard", "sport": "football"},
    {"name": "Bundesliga", "endpoint": "soccer/ger.1/scoreboard", "sport": "football"},
    {"name": "Ligue 1", "endpoint": "soccer/fra.1/scoreboard", "sport": "football"},
    {"name": "Champions League", "endpoint": "soccer/uefa.champions/scoreboard", "sport": "football"},
    {"name": "Libertadores", "endpoint": "soccer/conmebol.libertadores/scoreboard", "sport": "football"},
    {"name": "Brasileirão", "endpoint": "soccer/bra.1/scoreboard", "sport": "football"},
    {"name": "FA Cup", "endpoint": "soccer/eng.fa/scoreboard", "sport": "football"},
]


def _fetch_single_league(league, espn_date):
    """Fetch games from a single ESPN league endpoint."""
    games = []
    try:
        url = f"{ESPN_BASE}{league['endpoint']}?date={espn_date}"
        r = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT)
        if r.status_code != 200:
            return games
        data = r.json()

        for event in data.get("events", []):
            try:
                status = event.get("status", {}).get("type", {})
                if status.get("completed", False):
                    continue

                comps = event.get("competitions", [])
                if not comps:
                    continue
                comp = comps[0]
                competitors = comp.get("competitors", [])
                home_c = next((c for c in competitors if c["homeAway"] == "home"), None)
                away_c = next((c for c in competitors if c["homeAway"] == "away"), None)
                if not home_c or not away_c:
                    continue

                h_name = home_c["team"].get("name", home_c["team"]["displayName"])
                a_name = away_c["team"].get("name", away_c["team"]["displayName"])

                # Parse time UTC -> BRT (UTC-3)
                game_time = "TBD"
                try:
                    raw = event.get("date", "")
                    dt = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
                    brt = dt - datetime.timedelta(hours=3)
                    game_time = brt.strftime("%H:%M")
                except:
                    pass

                espn_odds = {}
                odds_data = comp.get("odds", [])
                if odds_data:
                    espn_odds["spread"] = odds_data[0].get("details", "")
                    espn_odds["over_under"] = odds_data[0].get("overUnder", 0)

                h_record, a_record = "", ""
                for c in competitors:
                    recs = c.get("records", [])
                    if recs:
                        rec = recs[0].get("summary", "")
                        if c["homeAway"] == "home":
                            h_record = rec
                        else:
                            a_record = rec

                games.append({
                    "home": h_name, "away": a_name,
                    "league": league["name"], "sport": league["sport"],
                    "time": game_time, "espn_odds": espn_odds,
                    "home_record": h_record, "away_record": a_record,
                })
            except:
                continue
    except Exception as e:
        print(f"[TURBO] ESPN error {league['name']}: {e}")
    return games


def fetch_espn_schedule_parallel(target_date):
    """
    Fetch ALL ESPN leagues in PARALLEL.
    Old: ~80s (sequential). New: ~8s (parallel).
    """
    cache_key = f"espn_schedule_{target_date}"
    cached = _cache.get(cache_key)
    if cached is not None:
        print(f"[TURBO] ⚡ ESPN Schedule HIT cache ({len(cached)} games)")
        return cached

    espn_date = target_date.replace("-", "")
    all_games = []
    
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_ESPN) as executor:
        futures = {executor.submit(_fetch_single_league, lg, espn_date): lg for lg in LEAGUES}
        for future in as_completed(futures):
            try:
                games = future.result()
                all_games.extend(games)
            except Exception as e:
                print(f"[TURBO] League thread failed: {e}")
    
    elapsed = time.time() - t0
    print(f"[TURBO] ⚡ ESPN Schedule: {len(all_games)} games in {elapsed:.1f}s (parallel)")
    
    _cache.set(cache_key, all_games, ttl_seconds=600)  # 10 min cache
    return all_games


# ═══════════════════════════════════════════════════
# 2. PARALLEL 365SCORES INTELLIGENCE
# ═══════════════════════════════════════════════════

def _fetch_single_intel(home, away, target_date, sport_365, get_lineup_func):
    """Fetch lineup intelligence for a single game."""
    try:
        intel = get_lineup_func(home, away, target_date, sport=sport_365)
        return (home, intel)
    except Exception as e:
        print(f"[TURBO] 365S error for {home}: {e}")
        return (home, None)


def fetch_365_intelligence_parallel(games, target_date, get_lineup_func):
    """
    Fetch 365Scores intelligence for ALL games in parallel.
    Old: N × 2s = ~20s. New: ~3s.
    """
    cache_key = f"365intel_{target_date}"
    cached = _cache.get(cache_key)
    # Temporary bypass memory cache for debugging NBA EV Player Props:
    # if cached is not None:
    #     print(f"[TURBO] ⚡ 365Scores Intel HIT cache ({len(cached)} entries)")
    #     return cached

    intel_map = {}
    t0 = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_365) as executor:
        futures = []
        for game in games:
            sport_365 = "basketball" if game.get("sport") == "basketball" else "football"
            futures.append(
                executor.submit(_fetch_single_intel, game["home"], game["away"], target_date, sport_365, get_lineup_func)
            )
        for future in as_completed(futures):
            try:
                home, intel = future.result()
                if intel:
                    intel_map[home] = intel
            except:
                continue
    
    elapsed = time.time() - t0
    print(f"[TURBO] ⚡ 365Scores Intel: {len(intel_map)} entries in {elapsed:.1f}s (parallel)")
    
    _cache.set(cache_key, intel_map, ttl_seconds=600)
    return intel_map


# ═══════════════════════════════════════════════════
# 3. PARALLEL NEWS AGENT
# ═══════════════════════════════════════════════════

def _fetch_single_news(team_name, sport, search_func):
    """Fetch news for a single team."""
    try:
        news = search_func(team_name, sport)
        return (team_name, news)
    except Exception as e:
        return (team_name, "")


def fetch_news_parallel(teams_with_sport, search_func):
    """
    Fetch news for ALL teams in parallel.
    Old: N × 2 requests × 5s = ~50s. New: ~5s.
    
    teams_with_sport: list of (team_name, sport_str)
    """
    cache_key = f"news_{hash(frozenset(t[0] for t in teams_with_sport))}"
    cached = _cache.get(cache_key)
    if cached is not None:
        print(f"[TURBO] ⚡ News Agent HIT cache")
        return cached

    news_map = {}
    t0 = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_NEWS) as executor:
        futures = []
        for team_name, sport in teams_with_sport:
            futures.append(
                executor.submit(_fetch_single_news, team_name, sport, search_func)
            )
        for future in as_completed(futures):
            try:
                team, news = future.result()
                news_map[team] = news
            except:
                continue
    
    elapsed = time.time() - t0
    print(f"[TURBO] ⚡ News Agent: {len(news_map)} teams in {elapsed:.1f}s (parallel)")
    
    _cache.set(cache_key, news_map, ttl_seconds=900)  # 15 min for news
    return news_map


# ═══════════════════════════════════════════════════
# 4. PARALLEL ESPN RESULTS FETCH
# ═══════════════════════════════════════════════════

RESULT_LEAGUES = [
    "basketball/nba",
    "soccer/bra.1",
    "soccer/eng.1",
    "soccer/esp.1",
    "soccer/ita.1",
    "soccer/ger.1",
    "soccer/fra.1",
    "soccer/uefa.champions",
    "soccer/conmebol.libertadores",
    "soccer/conmebol.sudamericana",
]


def _fetch_single_result_league(league_path, espn_date):
    """Fetch results from a single ESPN league."""
    results = {}
    try:
        url = f"{ESPN_BASE}{league_path}/scoreboard"
        if espn_date:
            url += f"?date={espn_date}"
        r = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT)
        data = r.json()
        
        for event in data.get('events', []):
            try:
                status_type = event['status']['type']
                completed = status_type['completed']
                competitions = event.get('competitions', [])
                if not competitions:
                    continue
                comp = competitions[0]
                competitors = comp.get('competitors', [])
                
                home_team = next((t for t in competitors if t['homeAway'] == 'home'), None)
                away_team = next((t for t in competitors if t['homeAway'] == 'away'), None)
                if not home_team or not away_team:
                    continue
                
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
                    "home_val": h_score,
                    "away_val": a_score,
                    "status": status_type['description'],
                    "completed": completed
                }
                
                for name in [h_name, a_name, h_short, a_short, h_nick, a_nick]:
                    results[name] = result_obj
            except:
                continue
    except Exception as e:
        print(f"[TURBO] Results error {league_path}: {e}")
    return results


def fetch_espn_results_parallel(target_date=None):
    """
    Fetch results from ALL ESPN leagues in PARALLEL.
    Old: ~80s. New: ~6s.
    """
    cache_key = f"espn_results_{target_date or 'today'}"
    cached = _cache.get(cache_key)
    if cached is not None:
        print(f"[TURBO] ⚡ ESPN Results HIT cache ({len(cached)} entries)")
        return cached

    espn_date = target_date.replace("-", "") if target_date else ""
    all_results = {}
    
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_RESULTS) as executor:
        futures = {executor.submit(_fetch_single_result_league, lp, espn_date): lp for lp in RESULT_LEAGUES}
        for future in as_completed(futures):
            try:
                results = future.result()
                all_results.update(results)
            except:
                continue
    
    elapsed = time.time() - t0
    print(f"[TURBO] ⚡ ESPN Results: {len(all_results)} entries in {elapsed:.1f}s (parallel)")
    
    _cache.set(cache_key, all_results, ttl_seconds=300)  # 5 min cache for results
    return all_results


# ═══════════════════════════════════════════════════
# 5. HISTORY CACHE (Eliminates repeated file reads)
# ═══════════════════════════════════════════════════

_history_cache = {"data": None, "mtime": 0}
_history_lock = threading.Lock()


def get_cached_history():
    """
    Returns history.json with smart file-change detection.
    Only re-reads from disk if file was modified.
    """
    history_file = 'history.json'
    with _history_lock:
        if os.path.exists(history_file):
            current_mtime = os.path.getmtime(history_file)
            if _history_cache["data"] is not None and current_mtime <= _history_cache["mtime"]:
                return _history_cache["data"]
            
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            _history_cache["data"] = data
            _history_cache["mtime"] = current_mtime
            return data
        return []


def save_history(history):
    """Save history and update cache."""
    history_file = 'history.json'
    with _history_lock:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        _history_cache["data"] = history
        _history_cache["mtime"] = time.time()


# ═══════════════════════════════════════════════════
# 6. STATS CALCULATOR (No re-fetch)
# ═══════════════════════════════════════════════════

def calculate_stats_from_history(history):
    """
    Pure function: calculates stats from a pre-loaded history list.
    NO more re-calling get_history_games().
    """
    if not history:
        return {"accuracy": 0, "red_pct": 0, "total": 0, "greens": 0, "reds": 0, 
                "win_rate": "0%", "voids": 0, "pending": 0, "resolved": 0, 
                "streak": "0", "league_breakdown": []}

    total = len(history)
    greens = sum(1 for h in history if h['status'] == 'WON')
    reds = sum(1 for h in history if h['status'] == 'LOST')
    voids = sum(1 for h in history if h['status'] == 'VOID')
    pending = sum(1 for h in history if h['status'] == 'PENDING')
    
    resolved = greens + reds
    accuracy = round((greens / resolved) * 100, 1) if resolved > 0 else 0
    red_pct = round((reds / resolved) * 100, 1) if resolved > 0 else 0

    # Streak
    streak_val = 0
    for h in reversed(history):
        s = h.get('status', 'PENDING')
        if s in ('PENDING', 'VOID'):
            continue
        if s == 'WON':
            streak_val += 1
        else:
            break

    # League breakdown
    leagues = {}
    for h in history:
        if h['status'] not in ('WON', 'LOST'):
            continue
        lg = h.get('league', 'Desconhecida')
        if lg not in leagues:
            leagues[lg] = {"greens": 0, "reds": 0}
        if h['status'] == 'WON':
            leagues[lg]["greens"] += 1
        else:
            leagues[lg]["reds"] += 1

    league_stats = []
    for lg, data in leagues.items():
        lg_total = data["greens"] + data["reds"]
        lg_acc = round((data["greens"] / lg_total) * 100, 1) if lg_total > 0 else 0
        league_stats.append({"league": lg, "greens": data["greens"], "reds": data["reds"], "accuracy": lg_acc})
    league_stats.sort(key=lambda x: x["accuracy"], reverse=True)

    return {
        "accuracy": accuracy, "win_rate": f"{accuracy}%", "red_pct": red_pct,
        "total": total, "greens": greens, "reds": reds,
        "voids": voids, "pending": pending, "resolved": resolved,
        "streak": str(streak_val), "league_breakdown": league_stats[:10]
    }


def calculate_today_scout(history, total_scheduled):
    """
    Pure function: today's scout from pre-loaded data.
    NO more circular calls.
    """
    now = datetime.datetime.now()
    target_short = now.strftime("%d/%m")
    
    today_results = [h for h in history if h.get('date') == target_short]
    greens = sum(1 for h in today_results if h.get('status') == 'WON')
    reds = sum(1 for h in today_results if h.get('status') == 'LOST')
    pends_hist = sum(1 for h in today_results if h.get('status') == 'PENDING')
    
    pending = pends_hist + max(0, total_scheduled - len(today_results))
    resolved = greens + reds
    daily_acc = round((greens / resolved) * 100, 1) if resolved > 0 else 0
    
    return {
        "total": total_scheduled,
        "greens": greens, "reds": reds,
        "pending": pending, "accuracy": daily_acc,
        "date": target_short
    }


# ═══════════════════════════════════════════════════
# 7. CALIBRATION CACHE (No more re-reading history.json)
# ═══════════════════════════════════════════════════

_calibration_cache = {"data": None, "computed_at": 0}


def get_calibration_adjustments_cached():
    """Cached version — recomputes max once per 10 minutes."""
    now = time.time()
    if _calibration_cache["data"] is not None and (now - _calibration_cache["computed_at"]) < 600:
        return _calibration_cache["data"]
    
    adjustments = {
        "league": {},
        "odds_range": {
            "ultra_safe": {"range": (1.10, 1.40), "hits": 0, "total": 0},
            "safe": {"range": (1.40, 1.70), "hits": 0, "total": 0},
            "value": {"range": (1.70, 2.00), "hits": 0, "total": 0},
            "aggressive": {"range": (2.00, 99.0), "hits": 0, "total": 0}
        }
    }
    
    try:
        history = get_cached_history()
        for entry in history:
            league = entry.get('league', 'Unknown')
            odd = float(entry.get('odd', 1.5))
            status = entry.get('status', 'PENDING')
            if status not in ['WON', 'LOST']:
                continue
            is_win = status == 'WON'
            
            if league not in adjustments['league']:
                adjustments['league'][league] = {'hits': 0, 'total': 0}
            adjustments['league'][league]['total'] += 1
            if is_win:
                adjustments['league'][league]['hits'] += 1
            
            for key, data in adjustments['odds_range'].items():
                low, high = data['range']
                if low <= odd < high:
                    data['total'] += 1
                    if is_win:
                        data['hits'] += 1
                    break
    except:
        pass
    
    _calibration_cache["data"] = adjustments
    _calibration_cache["computed_at"] = now
    return adjustments


def apply_calibration_fast(prob, odd, league):
    """Cached calibration — no more re-reading history.json per call."""
    cal = get_calibration_adjustments_cached()
    adjustment = 0
    
    if league in cal['league']:
        lg_data = cal['league'][league]
        if lg_data['total'] >= 3:
            real_accuracy = (lg_data['hits'] / lg_data['total']) * 100
            if real_accuracy < 60:
                adjustment -= 10
            elif real_accuracy < 70:
                adjustment -= 6
            elif real_accuracy < 75:
                adjustment -= 3
    
    for key, data in cal['odds_range'].items():
        low, high = data['range']
        if low <= odd < high and data['total'] >= 3:
            real_hit_rate = (data['hits'] / data['total']) * 100
            expected = {"ultra_safe": 85, "safe": 70, "value": 60, "aggressive": 50}.get(key, 65)
            if real_hit_rate < expected - 10:
                adjustment -= 6
            break
    
    return max(30, min(95, prob + adjustment))


# ═══════════════════════════════════════════════════
# PERFORMANCE MONITOR
# ═══════════════════════════════════════════════════

def performance_report():
    """Returns performance stats for debugging."""
    return {
        "cache": _cache.stats(),
        "history_cached": _history_cache["data"] is not None,
        "calibration_cached": _calibration_cache["data"] is not None,
    }
