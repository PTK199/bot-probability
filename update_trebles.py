# -*- coding: utf-8 -*-
"""
update_trebles.py — Atualiza o status das trincas (history_trebles.json)
cruzando cada componente com os resultados reais da ESPN API.
Chamado automaticamente pelo auto_updater.py.
"""
import json, requests, sys, os, logging
from datetime import datetime, timedelta, date

sys.stdout = sys.stdout if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding == 'utf-8' else \
    __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TREBLE_PATH = os.path.join(BASE_DIR, 'history_trebles.json')

log = logging.getLogger('update_trebles')

# Aliases para fuzzy match de times
ALIASES = {
    'wolves': ['wolverhampton', 'wolverhampton wanderers'],
    'man city': ['manchester city'],
    'man utd': ['manchester united'],
    'atletico': ['atletico madrid', 'atletico-mg', 'atletico mineiro'],
    'aston villa': ['villa'],
    'palmeiras': ['verdao'],
    'flamengo': ['fla'],
    'thunder': ['oklahoma city thunder', 'oklahoma city'],
    'spurs': ['san antonio spurs', 'san antonio'],
    'celtics': ['boston celtics'],
    'bucks': ['milwaukee bucks'],
    'heat': ['miami heat'],
    'magic': ['orlando magic'],
    'rockets': ['houston rockets'],
    'pistons': ['detroit pistons'],
    'cavaliers': ['cleveland cavaliers'],
    'knicks': ['new york knicks'],
}

ESPN_LEAGUES = [
    'basketball/nba',
    'soccer/eng.1', 'soccer/esp.1', 'soccer/ita.1',
    'soccer/ger.1', 'soccer/fra.1', 'soccer/bra.1',
    'soccer/UEFA.CHAMPIONS', 'soccer/UEFA.EUROPA',
    'soccer/eng.fa',
]

def fuzzy(a, b):
    a, b = a.lower().strip(), b.lower().strip()
    if a in b or b in a: return True
    for key, vals in ALIASES.items():
        names = [key] + vals
        if any(n in a or a in n for n in names) and any(n in b or b in n for n in names):
            return True
    return False


def fetch_results(date_obj):
    """Busca todos os jogos finalizados de uma data."""
    date_str = date_obj.strftime('%Y%m%d')
    results = {}
    for league in ESPN_LEAGUES:
        url = f'https://site.api.espn.com/apis/site/v2/sports/{league}/scoreboard?dates={date_str}'
        try:
            r = requests.get(url, timeout=10)
            for ev in r.json().get('events', []):
                status = ev.get('status', {}).get('type', {})
                if not status.get('completed', False):
                    continue
                teams = ev.get('competitions', [{}])[0].get('competitors', [])
                if len(teams) < 2: continue
                h = next((t for t in teams if t.get('homeAway') == 'home'), teams[0])
                a = next((t for t in teams if t.get('homeAway') == 'away'), teams[1])
                hs = int(h.get('score', 0)) if str(h.get('score', '0')).isdigit() else 0
                as_ = int(a.get('score', 0)) if str(a.get('score', '0')).isdigit() else 0
                game = {
                    'home': h['team']['displayName'],
                    'away': a['team']['displayName'],
                    'hs': hs, 'as': as_,
                }
                results[h['team']['displayName']] = game
                results[a['team']['displayName']] = game
        except: continue
    return results


def evaluate_component(comp, results):
    """
    Avalia um componente da trinca.
    Retorna 'WON', 'LOST', ou 'PENDING'.
    """
    match = comp.get('match', '')  # ex: "Aston Villa @ Wolverhampton Wanderers"
    pick  = comp.get('pick', '')   # ex: "Aston Villa ou Empate (@1.49)"

    # Extrai os times do match
    parts = match.replace(' @ ', ' vs ').split(' vs ')
    if len(parts) < 2: return 'PENDING'
    away_team = parts[0].strip()  # No formato "Away @ Home"
    home_team = parts[1].strip()

    # Encontra jogo nos resultados
    game = None
    for team_name, g in results.items():
        if fuzzy(home_team, g['home']) or fuzzy(away_team, g['away']) or \
           fuzzy(home_team, g['away']) or fuzzy(away_team, g['home']):
            game = g
            break

    if not game: return 'PENDING'

    hs, as_ = game['hs'], game['as']
    # Corrige orientação se necessário
    if fuzzy(home_team, game['away']):
        hs, as_ = as_, hs

    pick_low = pick.lower()
    sel_low  = pick_low.split('(')[0].strip()  # Remove odd do final

    # Dupla Chance / ou Empate
    if 'ou empate' in sel_low:
        fav = sel_low.replace('ou empate', '').strip()
        if fuzzy(fav, home_team):
            return 'WON' if hs >= as_ else 'LOST'
        elif fuzzy(fav, away_team):
            return 'WON' if as_ >= hs else 'LOST'

    # Vencedor / ML
    elif 'vence' in sel_low:
        team = sel_low.replace('vence', '').strip()
        if fuzzy(team, home_team):
            return 'WON' if hs > as_ else 'LOST'
        elif fuzzy(team, away_team):
            return 'WON' if as_ > hs else 'LOST'

    # Over / Under pontos ou gols
    elif 'over' in sel_low or 'mais de' in sel_low:
        import re
        nums = re.findall(r'\d+\.?\d*', sel_low)
        if nums:
            line = float(nums[0])
            total = hs + as_
            return 'WON' if total > line else 'LOST'

    return 'PENDING'


def run():
    if not os.path.exists(TREBLE_PATH):
        print('history_trebles.json nao encontrado.')
        return 0

    with open(TREBLE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    trebles = data if isinstance(data, list) else data.get('trebles', [])

    pending = [t for t in trebles if str(t.get('status', 'PENDING')).upper() in ('PENDING', '', 'NONE')]
    print(f'[TREBLES] Pendentes: {len(pending)} de {len(trebles)} total')

    if not pending:
        print('[TREBLES] Nenhuma trinca pendente.')
        return 0

    # Busca resultados dos últimos 14 dias
    today = date.today()
    all_results = {}
    for delta in range(14):
        d = today - timedelta(days=delta)
        res = fetch_results(d)
        all_results.update(res)
    print(f'[TREBLES] Jogos buscados na ESPN: {len(all_results)}')

    updated = won = lost = 0
    for treble in pending:
        components = treble.get('components', [])
        if not components:
            continue

        comp_results = []
        for comp in components:
            r = evaluate_component(comp, all_results)
            comp['status'] = r
            comp_results.append(r)

        if any(r == 'LOST' for r in comp_results):
            treble['status'] = 'LOST'
            treble['profit'] = '-100%'
            lost += 1; updated += 1
        elif all(r == 'WON' for r in comp_results):
            odd = float(treble.get('total_odd', treble.get('odd', 1.0)))
            profit = int((odd - 1) * 100)
            treble['status'] = 'WON'
            treble['profit'] = f'+{profit}%'
            won += 1; updated += 1
        # else: ainda pendente (algum jogo ainda nao acabou)

        name = treble.get('name', '?')
        date_t = treble.get('date', '?')
        st = treble.get('status', 'PENDING')
        print(f'  [{st:7}] {date_t} | {name} | componentes: {comp_results}')

    # Salva
    with open(TREBLE_PATH, 'w', encoding='utf-8') as f:
        json.dump(trebles if isinstance(data, list) else data, f, ensure_ascii=False, indent=2)

    # Stats finais
    all_won  = sum(1 for t in trebles if str(t.get('status','')).upper() in ('WON','GREEN'))
    all_lost = sum(1 for t in trebles if str(t.get('status','')).upper() in ('LOST','RED'))
    all_pend = sum(1 for t in trebles if str(t.get('status','')).upper() in ('PENDING','','NONE') or not t.get('status'))
    rate = all_won/(all_won+all_lost)*100 if (all_won+all_lost) > 0 else 0
    print(f'\n[TREBLES] GREEN RATE: {rate:.1f}% | WON:{all_won} LOST:{all_lost} PEND:{all_pend}')
    print(f'[TREBLES] Atualizadas agora: {updated} (WON:{won} LOST:{lost})')
    return updated


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
