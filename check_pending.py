# -*- coding: utf-8 -*-
import sys, io, json, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

picks = data if isinstance(data, list) else data.get('picks', data.get('history', []))
pending = [p for p in picks if str(p.get('status', '')).upper() in ['PENDING', '', 'NONE'] or not p.get('status')]

print(f"Picks pendentes total: {len(pending)}")

date_str = '20260225'
ESPN_URLS = {
    'NBA':        f'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_str}',
    'EPL':        f'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates={date_str}',
    'BRA':        f'https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard?dates={date_str}',
    'LA_LIGA':    f'https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard?dates={date_str}',
    'LIGUE1':     f'https://site.api.espn.com/apis/site/v2/sports/soccer/fra.1/scoreboard?dates={date_str}',
    'SERIE_A':    f'https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/scoreboard?dates={date_str}',
    'BUNDESLIGA': f'https://site.api.espn.com/apis/site/v2/sports/soccer/ger.1/scoreboard?dates={date_str}',
    'FA_CUP':     f'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.fa/scoreboard?dates={date_str}',
    'LA_LIGA2':   f'https://site.api.espn.com/apis/site/v2/sports/soccer/esp.2/scoreboard?dates={date_str}',
}

all_games = []
for league, url in ESPN_URLS.items():
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for ev in r.json().get('events', []):
                state = ev.get('status', {}).get('type', {}).get('state', '')
                comps = ev.get('competitions', [{}])[0]
                teams = comps.get('competitors', [])
                if len(teams) >= 2:
                    h = next((t for t in teams if t.get('homeAway') == 'home'), teams[0])
                    a = next((t for t in teams if t.get('homeAway') == 'away'), teams[1])
                    all_games.append({
                        'home': h['team']['displayName'],
                        'away': a['team']['displayName'],
                        'hs': h.get('score', '?'),
                        'as': a.get('score', '?'),
                        'state': state,
                        'league': league,
                    })
        else:
            print(f"WARN {league}: HTTP {r.status_code}")
    except Exception as e:
        print(f"ERR {league}: {e}")

post_games = [g for g in all_games if g['state'] == 'post']
print(f"\nJogos encontrados em 25/02: {len(all_games)} | Finalizados: {len(post_games)}")
print("-" * 70)
for g in post_games:
    print(f"  [{g['league']:10}] {g['home']:30} {g['hs']:>3} x {g['as']:<3} {g['away']}")

def fuzzy(n1, n2):
    a, b = n1.lower().strip(), n2.lower().strip()
    return a in b or b in a

# Cruzamento
print("\n" + "=" * 70)
print("CRUZAMENTO PICKS x RESULTADOS")
print("=" * 70)

won = 0; lost = 0; still_pend = 0; updated = 0

for p in pending:
    ph = p.get('home', p.get('team1', ''))
    pa = p.get('away', p.get('team2', ''))
    game = None

    for g in post_games:
        if (fuzzy(ph, g['home']) and fuzzy(pa, g['away'])) or \
           (fuzzy(ph, g['away']) and fuzzy(pa, g['home'])):
            game = g
            break

    if not game:
        still_pend += 1
        continue

    hs = int(game['hs']) if str(game['hs']).isdigit() else None
    as_ = int(game['as']) if str(game['as']).isdigit() else None
    market = p.get('market', '').upper()
    sel = p.get('selection', '').upper()
    result = 'PENDING'

    if hs is not None and as_ is not None:
        if 'VENCEDOR' in market or 'ML' in market:
            sel_clean = sel.replace('VENCE', '').strip()
            if fuzzy(sel_clean, game['home']):
                result = 'WON' if hs > as_ else 'LOST'
            elif fuzzy(sel_clean, game['away']):
                result = 'WON' if as_ > hs else 'LOST'

        elif 'DUPLA CHANCE' in market:
            parts = sel.split(' OU ')
            team_part = parts[0].strip() if parts else ''
            is_draw = (hs == as_)
            home_wins = fuzzy(team_part, game['home']) and hs > as_
            away_wins = fuzzy(team_part, game['away']) and as_ > hs
            if 'EMPATE' in sel:
                result = 'WON' if (is_draw or home_wins or away_wins) else 'LOST'
            else:
                result = 'WON' if (home_wins or away_wins) else 'LOST'

        elif 'OVER' in sel:
            try:
                line = float(sel.split('OVER')[1].split('PONTOS')[0].strip())
                result = 'WON' if (hs + as_) > line else 'LOST'
            except Exception:
                pass

        elif 'UNDER' in sel:
            try:
                line = float(sel.split('UNDER')[1].split('PONTOS')[0].strip())
                result = 'WON' if (hs + as_) < line else 'LOST'
            except Exception:
                pass

    tag = '[WON ]' if result == 'WON' else ('[LOST]' if result == 'LOST' else '[?   ]')
    print(f"  {tag} {game['home']:25} {game['hs']}x{game['as']} {game['away']:25} | {p.get('market','?')}: {p.get('selection','?')}")

    if result in ('WON', 'LOST'):
        p['status'] = result
        p['score'] = f"{game['hs']}-{game['as']}"
        updated += 1
        if result == 'WON':
            won += 1
        else:
            lost += 1
    else:
        still_pend += 1

print(f"\nWON: {won} | LOST: {lost} | Ainda pendente: {still_pend}")

if updated > 0:
    with open('history.json', 'w', encoding='utf-8') as f:
        json.dump(picks if isinstance(data, list) else data, f, ensure_ascii=False, indent=2)
    print(f"Salvos: {updated} picks atualizados no history.json")

all_won  = sum(1 for x in picks if str(x.get('status', '')).upper() in ['WON', 'GREEN', 'WIN'])
all_lost = sum(1 for x in picks if str(x.get('status', '')).upper() in ['LOST', 'RED', 'LOSS'])
all_pend = sum(1 for x in picks if str(x.get('status', '')).upper() in ['PENDING', '', 'NONE'] or not x.get('status'))
rate = all_won / (all_won + all_lost) * 100 if (all_won + all_lost) > 0 else 0

print(f"\n=== GREEN RATE FINAL: {rate:.1f}% ===")
print(f"    WON:{all_won}  LOST:{all_lost}  PENDENTE:{all_pend}")
