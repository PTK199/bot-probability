"""
🏀 NBA Stats Module
Uses nba_api to fetch player averages (PPG, RPG, APG).
Caches data locally to ensure "bullet train" speed.
"""

import os
import json
import datetime
import time

try:
    from nba_api.stats.endpoints import leaguedashplayerstats
    NBA_API_AVAILABLE = True
except ImportError:
    NBA_API_AVAILABLE = False

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
STATS_CACHE_FILE = os.path.join(CACHE_DIR, "nba_season_stats.json")

def fetch_and_cache_nba_stats(season="2025-26"):
    """
    Fetches all player stats for the season and saves to local JSON.
    """
    if not NBA_API_AVAILABLE:
        print("[NBA-STATS] ⚠️ nba_api not installed.")
        return {}

    print(f"[NBA-STATS] [FETCHING] Global NBA statistics for {season}...")
    try:
        # Fetching per-game stats for all players
        stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season=season,
            per_mode_detailed='PerGame'
        )
        data = stats.get_dict()
        
        result_set = data.get('resultSets', [{}])[0]
        headers = result_set.get('headers', [])
        rows = result_set.get('rowSet', [])
        
        if not rows:
            print("[NBA-STATS] ⚠️ No rows returned from NBA API.")
            return {}

        # Map interesting columns
        try:
            name_idx = headers.index('PLAYER_NAME')
            pts_idx = headers.index('PTS')
            reb_idx = headers.index('REB')
            ast_idx = headers.index('AST')
            team_idx = headers.index('TEAM_ABBREVIATION')
        except ValueError as e:
            print(f"[NBA-STATS] ⚠️ Missing headers in API response: {e}")
            return {}

        import unicodedata
        def normalize_name(name):
            return "".join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn').lower()

        stats_map = {}
        for row in rows:
            name = row[name_idx]
            clean_name = normalize_name(name)
            stats_map[clean_name] = {
                "name": name,
                "team": row[team_idx],
                "avg_pts": float(row[pts_idx]),
                "avg_reb": float(row[reb_idx]),
                "avg_ast": float(row[ast_idx]),
                "last_updated": datetime.datetime.now().isoformat()
            }
        
        with open(STATS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(stats_map, f, ensure_ascii=False, indent=2)
            
        print(f"[NBA-STATS] [DONE] Cached {len(stats_map)} players.")
        return stats_map

    except Exception as e:
        print(f"[NBA-STATS] ⚠️ Error fetching stats: {e}")
        return {}

def get_nba_player_stats(player_name):
    """
    Returns stats for a specific player, uses cache if < 24h old.
    """
    import unicodedata
    def normalize_name(name):
        return "".join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn').lower()

    search_name = normalize_name(player_name)
    stats_map = {}
    
    # Load cache
    if os.path.exists(STATS_CACHE_FILE):
        mtime = os.path.getmtime(STATS_CACHE_FILE)
        # If cache is fresh (< 24h)
        if (time.time() - mtime) < 86400:
            try:
                with open(STATS_CACHE_FILE, "r", encoding="utf-8") as f:
                    stats_map = json.load(f)
            except:
                pass
    
    # If cache empty or old, refresh
    if not stats_map:
        stats_map = fetch_and_cache_nba_stats()
        
    return stats_map.get(search_name)

if __name__ == "__main__":
    # Test
    p = "LeBron James"
    s = get_nba_player_stats(p)
    if s:
        print(f"Stats for {p}: {s}")
    else:
        print(f"Player {p} not found.")
