# -*- coding: utf-8 -*-
import sys, io, json, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

picks = data if isinstance(data, list) else data.get('picks', data.get('history', []))
pending = [p for p in picks if str(p.get('status', '')).upper() in ['PENDING', '', 'NONE'] or not p.get('status')]

print(f"Picks pendentes total: {len(pending)}")

unique_dates = set([p.get('date') for p in pending if p.get('date')])
print(f"Datas com picks pendentes: {unique_dates}")

all_games = []

for dd_mm in unique_dates:
    parts = str(dd_mm).split('/')
    if len(parts) == 2:
        date_str = f"2026{parts[1]}{parts[0]}"
    else:
        continue
        
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
        'LIBERTADORES':f'https://site.api.espn.com/apis/site/v2/sports/soccer/conmebol.libertadores/scoreboard?dates={date_str}'
    }

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
                pass
        except Exception as e:
            pass

post_games = [g for g in all_games if g['state'] == 'post']
print(f"Jogos encontrados: {len(all_games)} | Finalizados: {len(post_games)}")
print("-" * 70)

def fuzzy(n1, n2):
    a, b = str(n1).lower().strip(), str(n2).lower().strip()
    return a in b or b in a or (len(a)>3 and len(b)>3 and (a[:4] in b or b[:4] in a))

print("\n" + "=" * 70)
print("CRUZAMENTO PICKS x RESULTADOS (DYNAMIC)")
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
    sel = str(p.get('selection', '')).upper()
    league = p.get('league', '').upper()
    result = 'PENDING'

    if hs is not None and as_ is not None:
        if 'VENCE' in sel or 'ML' in sel:
            sel_clean = sel.replace('VENCE', '').strip()
            if fuzzy(sel_clean, game['home']):
                result = 'WON' if hs > as_ else 'LOST'
            elif fuzzy(sel_clean, game['away']):
                result = 'WON' if as_ > hs else 'LOST'
        
        elif 'OU EMPATE' in sel:
            parts = sel.split(' OU ')
            team_part = parts[0].strip() if parts else ''
            is_draw = (hs == as_)
            home_wins = fuzzy(team_part, game['home']) and hs > as_
            away_wins = fuzzy(team_part, game['away']) and as_ > hs
            result = 'WON' if (is_draw or home_wins or away_wins) else 'LOST'

        elif 'OVER' in sel:
            try:
                line = float(sel.split('OVER')[1].split('PONTOS')[0].split('GOLS')[0].strip())
                result = 'WON' if (hs + as_) > line else 'LOST'
            except: pass
            
        elif 'UNDER' in sel:
            try:
                line = float(sel.split('UNDER')[1].split('PONTOS')[0].split('GOLS')[0].strip())
                result = 'WON' if (hs + as_) < line else 'LOST'
            except: pass

        elif 'DNB' in sel or 'DRAW NO BET' in sel:
            if hs == as_:
                result = 'VOID'
            else:
                sel_clean = sel.replace('DNB', '').strip()
                if fuzzy(sel_clean, game['home']):
                    result = 'WON' if hs > as_ else 'LOST'
                elif fuzzy(sel_clean, game['away']):
                    result = 'WON' if as_ > hs else 'LOST'

    tag = '[WON ]' if result == 'WON' else ('[LOST]' if result == 'LOST' else f'[{result:5}]')
    print(f"  {tag} {game['home']:25} {game['hs']}x{game['as']} {game['away']:25} | {p.get('selection','?')}")

    if result in ('WON', 'LOST', 'VOID'):
        p['status'] = result
        p['score'] = f"{game['hs']}-{game['as']}"
        if result == 'WON':
            odd = float(p.get('odd', 1.0))
            p['profit'] = f"+{int((odd - 1) * 100)}%"
            won += 1
        elif result == 'LOST':
            p['profit'] = "-100%"
            lost += 1
        elif result == 'VOID':
            p['profit'] = "0%"
        updated += 1
    else:
        still_pend += 1

print(f"\nWON: {won} | LOST: {lost} | Ainda pendente: {still_pend}")

if updated > 0:
    with open('history.json', 'w', encoding='utf-8') as f:
        json.dump(picks if isinstance(data, list) else data, f, ensure_ascii=False, indent=4)
    print(f"Salvos: {updated} picks atualizados no history.json")

all_won  = sum(1 for x in picks if str(x.get('status', '')).upper() in ['WON', 'GREEN', 'WIN'])
all_lost = sum(1 for x in picks if str(x.get('status', '')).upper() in ['LOST', 'RED', 'LOSS'])
all_pend = sum(1 for x in picks if str(x.get('status', '')).upper() in ['PENDING', '', 'NONE'] or not x.get('status'))
rate = all_won / (all_won + all_lost) * 100 if (all_won + all_lost) > 0 else 0

print(f"\n=== GREEN RATE FINAL: {rate:.1f}% ===")
print(f"    WON:{all_won}  LOST:{all_lost}  PENDENTE:{all_pend}")
