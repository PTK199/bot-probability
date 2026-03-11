# -*- coding: utf-8 -*-
import json, sys, os, io
from collections import defaultdict

os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('history.json', 'r', encoding='utf-8') as f:
    picks = json.load(f)

pending = [p for p in picks if str(p.get('status', '')).upper() in ['PENDING', '', 'NONE'] or not p.get('status')]

# Group by date
by_date = defaultdict(list)
for p in pending:
    by_date[p.get('date', '?')].append(p)

print(f"Total pendentes: {len(pending)}")
for d in sorted(by_date.keys()):
    print(f"\n=== {d} ({len(by_date[d])} picks) ===")
    for p in by_date[d]:
        print(f"  {p.get('home','?'):20} vs {p.get('away','?'):20} | {p.get('league','?'):15} | {p.get('selection','?')}")
