# -*- coding: utf-8 -*-
"""
Analisa historico de trincas e mostra green rate atual.
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('history_trebles.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

trebles = data if isinstance(data, list) else data.get('trebles', [])
print(f"Total de trincas: {len(trebles)}")

won = lost = pending = void = 0
for t in trebles:
    st = str(t.get('status', 'PENDING')).upper()
    name = t.get('name', t.get('type', '?'))
    date = t.get('date', '?')
    odd = t.get('total_odd', t.get('odd', '?'))
    sels = t.get('selections', [])
    print(f"  [{st:7}] {date} | {name} | @{odd} | {len(sels)} pernas")
    if st in ('WON', 'GREEN'):   won += 1
    elif st in ('LOST', 'RED'):  lost += 1
    elif st == 'VOID':           void += 1
    else:                        pending += 1

total = won + lost
rate = won/total*100 if total > 0 else 0
print(f"\nGREEN RATE TRINCAS: {rate:.1f}% | WON:{won} LOST:{lost} PEND:{pending} VOID:{void}")
print(f"\nEstrutura do primeiro registro:")
if trebles:
    print(json.dumps(trebles[0], ensure_ascii=False, indent=2)[:800])
