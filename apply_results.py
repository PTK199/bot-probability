# -*- coding: utf-8 -*-
"""
Aplica resultados confirmados do dia 25/02/2026 no history.json
NBA: 8 jogos finais confirmados via ESPN/browser
"""
import json

with open('history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

picks = data if isinstance(data, list) else data.get('picks', data.get('history', []))

# Resultados CONFIRMADOS do dia 25/02/2026
NBA_RESULTS = [
    # (home_keywords, away_keywords, home_score, away_score)
    (['Pistons', 'Detroit'],        ['Thunder', 'Oklahoma'],       124, 116),
    (['Raptors', 'Toronto'],        ['Spurs', 'San Antonio'],      107, 110),
    (['Grizzlies', 'Memphis'],      ['Warriors', 'Golden State'],  112, 133),
    (['Bucks', 'Milwaukee'],        ['Cavaliers', 'Cleveland'],    118, 116),
    (['Nuggets', 'Denver'],         ['Celtics', 'Boston'],         103,  84),
    (['Trail Blazers', 'Portland'], ['Timberwolves', 'Minnesota'], 121, 124),
    (['Lakers', 'Los Angeles'],     ['Magic', 'Orlando'],          109, 110),
    (['Rockets', 'Houston'],        ['Kings', 'Sacramento'],       128,  97),
]

# Red Bull Bragantino ja foi atualizado, mas garantindo
FUTEBOL_RESULTS = [
    (['Red Bull Bragantino', 'Bragantino'], ['Athletico', 'Athletico Paranaense', 'Atletico-PR'], 1, 1),
]

ALL_RESULTS = NBA_RESULTS + FUTEBOL_RESULTS

def fuzzy(name, keywords):
    n = name.lower()
    return any(k.lower() in n or n in k.lower() for k in keywords)

def evaluate(pick, hs, as_):
    market = pick.get('market', '').upper()
    sel = pick.get('selection', '').upper()
    ph_kw = [pick.get('home', pick.get('team1', ''))]
    pa_kw = [pick.get('away', pick.get('team2', ''))]

    if 'VENCEDOR' in market or 'ML' in market:
        sel_clean = sel.replace('VENCE', '').strip()
        # Descobrir qual time é o "home" no pick vs no resultado real
        # Tenta identificar se o pick home bate com keywords do resultado
        # O importante é: quem ganhou?
        if any(k.lower() in sel_clean.lower() or sel_clean.lower() in k.lower() for k in ph_kw):
            # Selecionou o time da casa (do pick)
            # Mas precisamos saber se o time da casa do pick ganhou de fato
            # Vou usar a lógica: se o pick home ganhou => hs > as_
            return 'WON' if hs > as_ else 'LOST'
        elif any(k.lower() in sel_clean.lower() or sel_clean.lower() in k.lower() for k in pa_kw):
            return 'WON' if as_ > hs else 'LOST'
        else:
            # tenta match direto pelo nome no sel_clean
            return None

    elif 'DUPLA CHANCE' in market:
        parts = sel.split(' OU ')
        team_part = parts[0].strip() if parts else ''
        is_draw = (hs == as_)
        home_winning = any(k.lower() in team_part.lower() or team_part.lower() in k.lower() for k in ph_kw) and hs > as_
        away_winning = any(k.lower() in team_part.lower() or team_part.lower() in k.lower() for k in pa_kw) and as_ > hs
        if 'EMPATE' in sel:
            return 'WON' if (is_draw or home_winning or away_winning) else 'LOST'
        else:
            return 'WON' if (home_winning or away_winning) else 'LOST'

    elif 'OVER' in sel:
        try:
            line = float(sel.split('OVER')[1].split('PONTOS')[0].strip())
            return 'WON' if (hs + as_) > line else 'LOST'
        except Exception:
            return None

    elif 'UNDER' in sel:
        try:
            line = float(sel.split('UNDER')[1].split('PONTOS')[0].strip())
            return 'WON' if (hs + as_) < line else 'LOST'
        except Exception:
            return None

    return None

updated = 0
details = []

for p in picks:
    if str(p.get('status', '')).upper() not in ['PENDING', '', 'NONE'] and p.get('status'):
        continue

    ph = p.get('home', p.get('team1', ''))
    pa = p.get('away', p.get('team2', ''))

    for (h_kw, a_kw, hs, as_) in ALL_RESULTS:
        home_match = fuzzy(ph, h_kw) or fuzzy(ph, a_kw)  # tenta dos dois lados
        away_match = fuzzy(pa, a_kw) or fuzzy(pa, h_kw)

        # Match normal (pick home = resultado home)
        if fuzzy(ph, h_kw) and fuzzy(pa, a_kw):
            result = evaluate(p, hs, as_)
            if result:
                p['status'] = result
                p['score'] = f'{hs}-{as_}'
                updated += 1
                details.append((result, ph, pa, hs, as_, p.get('market', '?'), p.get('selection', '?')))
            break

        # Match invertido (pick home = resultado away)
        if fuzzy(ph, a_kw) and fuzzy(pa, h_kw):
            result = evaluate(p, as_, hs)  # invertido
            if result:
                p['status'] = result
                p['score'] = f'{as_}-{hs}'
                updated += 1
                details.append((result, ph, pa, as_, hs, p.get('market', '?'), p.get('selection', '?')))
            break

print(f"Picks atualizados: {updated}")
print("-" * 70)
for (res, h, a, hs, as_, mkt, sel) in details:
    tag = '[WON ]' if res == 'WON' else '[LOST]'
    print(f"  {tag} {h:25} {hs} x {as_} {a:25} | {mkt}: {sel}")

with open('history.json', 'w', encoding='utf-8') as f:
    json.dump(picks if isinstance(data, list) else data, f, ensure_ascii=False, indent=2)

all_won  = sum(1 for x in picks if str(x.get('status', '')).upper() in ['WON', 'GREEN', 'WIN'])
all_lost = sum(1 for x in picks if str(x.get('status', '')).upper() in ['LOST', 'RED', 'LOSS'])
all_pend = sum(1 for x in picks if str(x.get('status', '')).upper() in ['PENDING', '', 'NONE'] or not x.get('status'))
rate = all_won / (all_won + all_lost) * 100 if (all_won + all_lost) > 0 else 0

print(f"\n=== GREEN RATE NOVO: {rate:.1f}% ===")
print(f"    WON:{all_won}  LOST:{all_lost}  PENDENTE:{all_pend}")

# Mostrar o que ainda esta pendente
pend_list = [x for x in picks if str(x.get('status', '')).upper() in ['PENDING', '', 'NONE'] or not x.get('status')]
if pend_list:
    print(f"\nAinda pendentes ({len(pend_list)}):")
    for p in pend_list:
        print(f"  {p.get('date','?')} | {p.get('home','?')} vs {p.get('away','?')} | {p.get('league','?')}")
