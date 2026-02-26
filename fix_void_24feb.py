# -*- coding: utf-8 -*-
"""
Busca resultados NBA do dia 24/02/2026 e atualiza os picks VOID para WON/LOST.
"""
import json, requests, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
picks = data if isinstance(data, list) else data.get('picks', data.get('history', []))

# Pegar picks que estao como VOID (eram NBA do dia 24/02)
void_picks = [p for p in picks if str(p.get('status', '')).upper() == 'VOID']
print(f"Picks VOID encontrados: {len(void_picks)}")
for p in void_picks:
    print(f"  {p.get('home')} vs {p.get('away')} | {p.get('selection')}")

# Buscar ESPN NBA do dia 24/02/2026
url = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates=20260224'
r = requests.get(url, timeout=10)
events = r.json().get('events', [])
print(f"\nJogos NBA encontrados em 24/02: {len(events)}")

# Mapear resultados
results = []
for ev in events:
    state = ev.get('status', {}).get('type', {}).get('state', '')
    comps = ev.get('competitions', [{}])[0]
    teams = comps.get('competitors', [])
    if len(teams) < 2:
        continue
    h = next((t for t in teams if t.get('homeAway') == 'home'), teams[0])
    a = next((t for t in teams if t.get('homeAway') == 'away'), teams[1])
    hs = int(h.get('score', 0)) if str(h.get('score', '0')).isdigit() else 0
    as_ = int(a.get('score', 0)) if str(a.get('score', '0')).isdigit() else 0
    results.append({
        'home': h['team']['displayName'],
        'away': a['team']['displayName'],
        'hs': hs, 'as': as_, 'state': state
    })
    print(f"  [{state}] {h['team']['displayName']} {hs} x {as_} {a['team']['displayName']}")

def fuzzy(n1, n2):
    a, b = n1.lower().strip(), n2.lower().strip()
    return a in b or b in a

# Cruzar e atualizar
print("\n=== CRUZAMENTO ===")
updated = 0
for p in void_picks:
    ph = p.get('home', '')
    pa = p.get('away', '')
    game = None
    inverted = False
    for g in results:
        if fuzzy(ph, g['home']) and fuzzy(pa, g['away']):
            game = g; inverted = False; break
        if fuzzy(ph, g['away']) and fuzzy(pa, g['home']):
            game = g; inverted = True; break

    if not game:
        print(f"  [NAO ENCONTRADO] {ph} vs {pa}")
        continue

    hs = game['as'] if inverted else game['hs']
    as_ = game['hs'] if inverted else game['as']

    sel = p.get('selection', '').upper()
    sel_clean = sel.replace('VENCE', '').strip()

    # Identificar time selecionado
    if fuzzy(sel_clean, ph):
        result = 'WON' if hs > as_ else 'LOST'
    elif fuzzy(sel_clean, pa):
        result = 'WON' if as_ > hs else 'LOST'
    else:
        result = 'PENDING'

    tag = '[WON ]' if result == 'WON' else '[LOST]'
    print(f"  {tag} {ph} {hs}x{as_} {pa} | {p.get('selection')}")

    if result in ('WON', 'LOST'):
        p['status'] = result
        p['score'] = f'{hs}-{as_}'
        p.pop('note', None)  # remove a nota de VOID
        updated += 1

print(f"\nAtualizados: {updated}")

with open('history.json', 'w', encoding='utf-8') as f:
    json.dump(picks if isinstance(data, list) else data, f, ensure_ascii=False, indent=2)

all_won  = sum(1 for x in picks if str(x.get('status','')).upper() in ['WON','GREEN','WIN'])
all_lost = sum(1 for x in picks if str(x.get('status','')).upper() in ['LOST','RED','LOSS'])
all_pend = sum(1 for x in picks if str(x.get('status','')).upper() in ['PENDING','','NONE'] or not x.get('status'))
all_void = sum(1 for x in picks if str(x.get('status','')).upper() == 'VOID')
rate = all_won/(all_won+all_lost)*100 if (all_won+all_lost) > 0 else 0
print(f"\nGREEN RATE: {rate:.1f}% | WON:{all_won} LOST:{all_lost} PEND:{all_pend} VOID:{all_void}")
