"""Test all API endpoints + verify new fields"""
import requests
import json
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

s = requests.Session()
BASE = "http://127.0.0.1:5000"

print("=== TESTANDO ENDPOINTS DO SERVIDOR ===\n")

# 1. Login
r = s.post(f"{BASE}/api/login", json={"email": "teste@bot.com", "password": "teste123"})
print(f"1. LOGIN: {r.status_code} - {r.json()}")

# 2. Games hoje
r = s.get(f"{BASE}/api/games?date=2026-02-11")
data = r.json()
ng = len(data.get("games", []))
nt = len(data.get("trebles", []))
print(f"2. GAMES 11/02: {ng} jogos, {nt} trebles")

# 3. Games amanha (auto engine)
r = s.get(f"{BASE}/api/games?date=2026-02-12")
data = r.json()
ng2 = len(data.get("games", []))
nt2 = len(data.get("trebles", []))
print(f"3. GAMES 12/02 (AUTO): {ng2} jogos, {nt2} trebles")

# 4. History
r = s.get(f"{BASE}/api/history")
print(f"4. HISTORY: {len(r.json())} entries")

# 5. History Stats (DETAILED CHECK)
r = s.get(f"{BASE}/api/history_stats")
stats = r.json()
print(f"5. STATS COMPLETOS:")
print(f"   greens={stats.get('greens')}, reds={stats.get('reds')}")
print(f"   win_rate={stats.get('win_rate')}")
print(f"   accuracy={stats.get('accuracy')}")
print(f"   streak={stats.get('streak')}")
print(f"   voids={stats.get('voids')}, pending={stats.get('pending')}")
print(f"   resolved={stats.get('resolved')}")
league_breakdown = stats.get('league_breakdown', [])
print(f"   league_breakdown: {len(league_breakdown)} ligas")
if league_breakdown:
    for lb in league_breakdown[:3]:
        print(f"     -> {lb['league']}: {lb['greens']}G/{lb['reds']}R = {lb['accuracy']}%")

# 6. Analyze
r = s.get(f"{BASE}/api/analyze?id=test123")
print(f"6. ANALYZE: {r.status_code} - {r.json().get('status')}")

# 7. Deep Analysis
r = s.post(f"{BASE}/api/analyze_deep", json={"text": "Flamengo vs Palmeiras 1.50 2.00"})
print(f"7. DEEP ANALYSIS: {r.status_code}")

# 8. Multiple Risk
r = s.post(f"{BASE}/api/analyze_multiple", json={"text": "Celtics 1.20 Pistons 3.50", "bankroll": 500})
print(f"8. MULTIPLE RISK: {r.status_code}")

# 9. Leverage (DETAILED CHECK)
r = s.get(f"{BASE}/api/leverage")
lev = r.json()
print(f"9. LEVERAGE PLAN:")
print(f"   current_day={lev.get('current_day')}")
print(f"   current_stake=R${lev.get('current_stake')}")
tip = lev.get('daily_tip', {})
print(f"   daily_tip: {tip.get('match')} | {tip.get('market')} @ {tip.get('odd')} ({tip.get('confidence')})")

# 10. Today Scout
r = s.get(f"{BASE}/api/today_scout")
print(f"10. TODAY SCOUT: {r.status_code}")

# 11. History Trebles
r = s.get(f"{BASE}/api/history_trebles")
print(f"11. HISTORY TREBLES: {r.status_code} - {len(r.json())} trebles")

# 12. Check Session
r = s.get(f"{BASE}/api/check_session")
print(f"12. CHECK SESSION: logged_in={r.json().get('logged_in')}")

# 13. Logout
r = s.get(f"{BASE}/api/logout")
print(f"13. LOGOUT: {r.json().get('status')}")

# Check new modules imported
print(f"\n=== VERIFICANDO NOVOS MODULOS ===")
try:
    import team_data
    print(f"  team_data.py: {len(team_data.TEAM_LOGOS)} logos")
except Exception as e:
    print(f"  FAIL team_data: {e}")

try:
    import odds_tools
    k = odds_tools.calculate_kelly_criterion(70, 1.50)
    print(f"  odds_tools.py: Kelly(70%, 1.50) = {k}%")
except Exception as e:
    print(f"  FAIL odds_tools: {e}")

try:
    import espn_api
    print(f"  espn_api.py: OK (ResultScoutBot ready)")
except Exception as e:
    print(f"  FAIL espn_api: {e}")

try:
    from supabase_client import sync_history_to_cloud
    print(f"  supabase sync: function loaded OK")
except Exception as e:
    print(f"  FAIL supabase sync: {e}")

print(f"\n=== TODOS OS 13 ENDPOINTS + 4 MODULOS TESTADOS! ===")
