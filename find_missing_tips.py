# -*- coding: utf-8 -*-
import json
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

history_file = 'history.json'
with open(history_file, 'r', encoding='utf-8') as f:
    history = json.load(f)

history_keys = set([f"{h.get('date', '')}|{h.get('home', '')}".strip() for h in history])

cache_dir = 'cache_games'
missing = 0

print("🔍 Buscando tips geradas que não entraram no histórico...")

for file in sorted(os.listdir(cache_dir)):
    if file.startswith('games_'):
        date_str = file.replace('games_', '').replace('.json', '')
        parts = date_str.split('-')
        if len(parts) == 3:
            dd_mm = f"{parts[2]}/{parts[1]}"
            with open(os.path.join(cache_dir, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                games = data.get('games', []) if isinstance(data, dict) else data
                for g in games:
                    best_tip = g.get('best_tip')
                    if best_tip and best_tip.get('selection'):
                        home = g.get('home', g.get('home_team', ''))
                        k = f"{dd_mm}|{home}".strip()
                        if k not in history_keys:
                            print(f"[{dd_mm}] Missing: {home} | {best_tip.get('selection')}")
                            missing += 1

print(f"\nTotal missing tips from cache_games: {missing}")
