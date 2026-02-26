# -*- coding: utf-8 -*-
"""
Correção dos picks de 25/02:
- 8 picks NBA com matchups que não ocorreram no dia 25 — marcar como pick fictício/erro de geração
- 6 picks europeus agendados para dia 27/02 e 03/03 — corrigir a data no sistema
"""
import json

with open('history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

picks = data if isinstance(data, list) else data.get('picks', data.get('history', []))

# Picks NBA do dia 25 que NAO ocorreram (matchups fictícios gerados pelo auto_picks)
# Verificado via ESPN: Suns, Pelicans, Bulls, Hawks, Nets não jogaram em 25/02 nesses matchups
NBA_FICTICIOS = [
    ('Suns',      'Celtics'),
    ('Pelicans',  'Warriors'),
    ('Bucks',     'Heat'),
    ('Bulls',     'Hornets'),
    ('Cavaliers', 'Knicks'),
    ('Raptors',   'Thunder'),
    ('Nets',      'Mavericks'),
    ('Hawks',     'Wizards'),
]

# Jogos europeus que são do dia 27/02 e 03/03, não do dia 25
# Vamos corrigir a data deles para refletir a data real
EURO_REMAP = {
    ('Levante',                    'Alavés'):                '27/02',
    ('Wolverhampton Wanderers',    'Aston Villa'):           '27/02',
    ('Strasbourg',                 'Lens'):                  '27/02',
    ('Parma',                      'Cagliari'):              '27/02',
    ('FC Augsburg',                'FC Cologne'):            '27/02',
    ('Port Vale',                  'Bristol City'):          '03/03',
}

def fuzzy(n1, n2):
    return n1.lower() in n2.lower() or n2.lower() in n1.lower()

nba_voided = 0
euro_fixed = 0

for p in picks:
    if str(p.get('status', '')).upper() not in ['PENDING', '', 'NONE'] and p.get('status'):
        continue

    ph = p.get('home', p.get('team1', ''))
    pa = p.get('away', p.get('team2', ''))

    # Verificar se é NBA fictício
    for (h, a) in NBA_FICTICIOS:
        if fuzzy(ph, h) and fuzzy(pa, a):
            # Marcar como VOID (jogo não aconteceu com essa matchup nessa data)
            p['status'] = 'VOID'
            p['note'] = 'Matchup nao ocorreu em 25/02/2026 - pick gerado incorretamente'
            nba_voided += 1
            print(f"  [VOID] {ph} vs {pa}")
            break

    # Verificar se é jogo europeu com data errada
    for (h, a), new_date in EURO_REMAP.items():
        if fuzzy(ph, h) and fuzzy(pa, a):
            old_date = p.get('date', '?')
            p['date'] = new_date
            euro_fixed += 1
            print(f"  [DATE FIX] {ph} vs {pa}: {old_date} -> {new_date}")
            break

print(f"\nNBA fictícios marcados como VOID: {nba_voided}")
print(f"Datas europeias corrigidas: {euro_fixed}")

with open('history.json', 'w', encoding='utf-8') as f:
    json.dump(picks if isinstance(data, list) else data, f, ensure_ascii=False, indent=2)

all_won  = sum(1 for x in picks if str(x.get('status', '')).upper() in ['WON', 'GREEN', 'WIN'])
all_lost = sum(1 for x in picks if str(x.get('status', '')).upper() in ['LOST', 'RED', 'LOSS'])
all_pend = sum(1 for x in picks if str(x.get('status', '')).upper() in ['PENDING', '', 'NONE'] or not x.get('status'))
all_void = sum(1 for x in picks if str(x.get('status', '')).upper() == 'VOID')
rate = all_won / (all_won + all_lost) * 100 if (all_won + all_lost) > 0 else 0

print(f"\n=== GREEN RATE FINAL: {rate:.1f}% ===")
print(f"    WON:{all_won}  LOST:{all_lost}  PENDENTE:{all_pend}  VOID:{all_void}")
print(f"    (Jogos europeus do dia 27/02 e 03/03 ficam PENDING ate acontecerem)")
