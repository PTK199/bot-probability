"""
Correcao final: remove picks NBA invalidos de 19/02 e busca resultados de 25/02
"""
import json
import requests

with open('history.json', 'r', encoding='utf-8') as f:
    h = json.load(f)

# 1. Remove picks de 19/02 que nao existem na ESPN (Timberwolves, Pelicans, Grizzlies nao jogaram nesse dia)
invalid_19 = {
    ('19/02', 'Timberwolves', 'Mavericks'),
    ('19/02', 'Pelicans', 'Bucks'),
    ('19/02', 'Grizzlies', 'Jazz'),
}

before = len(h)
h = [e for e in h if (e.get('date'), e.get('home'), e.get('away')) not in invalid_19]
removed = before - len(h)
print(f"[LIMPEZA] Removidos {removed} picks NBA invalidos de 19/02")

# 2. Busca resultados de hoje (25/02) da ESPN para atualizar jogos europeus e NBA que ja terminaram
print("\n[ESPN] Buscando resultados de 25/02...")

team_overrides = {
    "Boston Celtics": "Celtics", "New York Knicks": "Knicks", "Cleveland Cavaliers": "Cavaliers",
    "Oklahoma City Thunder": "Thunder", "Houston Rockets": "Rockets", "Golden State Warriors": "Warriors",
    "Denver Nuggets": "Nuggets", "LA Clippers": "Clippers", "Los Angeles Clippers": "Clippers",
    "Milwaukee Bucks": "Bucks", "Miami Heat": "Heat", "Phoenix Suns": "Suns",
    "Dallas Mavericks": "Mavericks", "Minnesota Timberwolves": "Timberwolves", "Sacramento Kings": "Kings",
    "Memphis Grizzlies": "Grizzlies", "Los Angeles Lakers": "Lakers", "Atlanta Hawks": "Hawks",
    "Charlotte Hornets": "Hornets", "San Antonio Spurs": "Spurs", "Chicago Bulls": "Bulls",
    "New Orleans Pelicans": "Pelicans", "Utah Jazz": "Jazz", "Portland Trail Blazers": "Trail Blazers",
    "Brooklyn Nets": "Nets", "Indiana Pacers": "Pacers", "Washington Wizards": "Wizards",
    "Orlando Magic": "Magic", "Philadelphia 76ers": "Sixers", "Detroit Pistons": "Pistons",
    "Toronto Raptors": "Raptors",
    "Wolverhampton Wanderers": "Wolverhampton Wanderers",
    "Aston Villa FC": "Aston Villa",
    "Wolverhampton Wanderers FC": "Wolverhampton Wanderers",
}

leagues_today = {
    "nba": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates=20260225",
    "eng.1": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates=20260225",
    "esp.1": "https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard?dates=20260225",
    "ita.1": "https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/scoreboard?dates=20260225",
    "ger.1": "https://site.api.espn.com/apis/site/v2/sports/soccer/ger.1/scoreboard?dates=20260225",
    "fra.1": "https://site.api.espn.com/apis/site/v2/sports/soccer/fra.1/scoreboard?dates=20260225",
    "bra.1": "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard?dates=20260225",
    "eng.fa": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.fa/scoreboard?dates=20260225",
    "conmebol.libertadores": "https://site.api.espn.com/apis/site/v2/sports/soccer/conmebol.libertadores/scoreboard?dates=20260225",
}

# Coleta todos os resultados finais de 25/02
results_25 = {}

for league, url in leagues_today.items():
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code != 200:
            continue
        data = resp.json()
        for ev in data.get('events', []):
            comps = ev.get('competitions', [{}])[0]
            competitors = comps.get('competitors', [])
            if len(competitors) < 2:
                continue
            home_c = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
            away_c = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])
            h_raw = home_c.get('team', {}).get('displayName', '')
            a_raw = away_c.get('team', {}).get('displayName', '')
            h_name = team_overrides.get(h_raw, h_raw)
            a_name = team_overrides.get(a_raw, a_raw)
            h_score = home_c.get('score', '0') or '0'
            a_score = away_c.get('score', '0') or '0'
            status_type = ev.get('status', {}).get('type', {})
            is_done = status_type.get('completed', False)
            state = status_type.get('name', '').lower()

            if is_done or 'final' in state or 'post' in state:
                try:
                    hv = int(float(h_score))
                    av = int(float(a_score))
                except:
                    hv, av = 0, 0
                results_25[h_name.lower()] = {
                    'hv': hv, 'av': av,
                    'home': h_name, 'away': a_name
                }
                results_25[a_name.lower()] = {
                    'hv': hv, 'av': av,
                    'home': h_name, 'away': a_name,
                    'is_away': True
                }
                print(f"  DONE: {h_name} {hv}-{av} {a_name}")
    except Exception as e:
        pass

print(f"\n[ESPN] {len(results_25)//2} jogos finalizados em 25/02")

def find_res(home, away, rmap):
    h_l = home.lower().strip()
    a_l = away.lower().strip()
    if h_l in rmap:
        return rmap[h_l]
    if a_l in rmap:
        return rmap[a_l]
    for k, v in rmap.items():
        if h_l in k or k in h_l:
            return v
        if a_l in k or k in a_l:
            return v
    return None

def evaluate(selection, our_h, our_a, home, away, odd):
    sel = selection.lower()
    def team_in(t):
        t_l = t.lower()
        if t_l in sel:
            return True
        for p in t_l.split():
            if len(p) > 3 and p in sel:
                return True
        return False

    if 'vence' in sel:
        won = (our_h > our_a) if team_in(home) else (our_a > our_h) if team_in(away) else None
    elif 'ou empate' in sel:
        won = (our_h >= our_a) if team_in(home) else (our_a >= our_h) if team_in(away) else None
    elif 'over' in sel:
        try:
            line = float(sel.split('over')[1].replace('pontos','').replace('gols','').strip().split()[0])
            won = (our_h + our_a) > line
        except:
            won = None
    elif 'under' in sel:
        try:
            line = float(sel.split('under')[1].replace('pontos','').replace('gols','').strip().split()[0])
            won = (our_h + our_a) < line
        except:
            won = None
    else:
        won = None

    if won is None:
        return None, None, None
    if won:
        return 'WON', f'+{int((odd-1)*100)}%', '✅ GREEN'
    else:
        return 'LOST', '-100%', '❌ RED'

# 3. Atualiza jogos de 25/02 que ja terminaram
updated = 0
print("\n[UPDATE] Atualizando picks do dia 25/02...")
for i, entry in enumerate(h):
    if entry.get('status') != 'PENDING' or entry.get('date') != '25/02':
        continue
    home = entry.get('home', '')
    away = entry.get('away', '')
    sel = entry.get('selection', '')
    odd = float(entry.get('odd', 1.5))

    res = find_res(home, away, results_25)
    if res is None:
        continue

    # Determina perspectiva
    res_home_lower = res.get('home', '').lower()
    home_lower = home.lower()
    if home_lower == res_home_lower or home_lower in res_home_lower or res_home_lower in home_lower:
        our_h = res['hv']
        our_a = res['av']
    else:
        our_h = res['av'] if res.get('is_away') else res['hv']
        our_a = res['hv'] if res.get('is_away') else res['av']

    status, profit, badge = evaluate(sel, our_h, our_a, home, away, odd)
    if status is None:
        print(f"  ?? {home} vs {away} | {sel} | {our_h}-{our_a}")
        continue

    h[i]['status'] = status
    h[i]['score'] = f"{our_h}-{our_a}"
    h[i]['profit'] = profit
    h[i]['badge'] = badge
    updated += 1
    icon = "G" if status == "WON" else "R"
    print(f"  [{icon}] {home} vs {away} | {sel} -> {status} ({our_h}-{our_a})")

with open('history.json', 'w', encoding='utf-8') as f:
    json.dump(h, f, indent=4, ensure_ascii=False)

print(f"\nTotal atualizado hoje: {updated}")
print("Salvo!")
