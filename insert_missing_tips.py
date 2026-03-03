# -*- coding: utf-8 -*-
import json
import os

history_file = 'history.json'
with open(history_file, 'r', encoding='utf-8') as f:
    history = json.load(f)

history_keys = set([f"{h.get('date', '')}|{h.get('home', '')}".strip() for h in history])
inserted = 0

for file in sorted(os.listdir('cache_games')):
    if file.startswith('games_'):
        date_str = file.replace('games_', '').replace('.json', '')
        parts = date_str.split('-')
        if len(parts) == 3:
            dd_mm = f"{parts[2]}/{parts[1]}"
            with open(os.path.join('cache_games', file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                games = data.get('games', []) if isinstance(data, dict) else data
                for g in games:
                    best_tip = g.get('best_tip')
                    if best_tip and best_tip.get('selection'):
                        home = g.get('home', g.get('home_team', ''))
                        away = g.get('away', g.get('away_team', ''))
                        k = f"{dd_mm}|{home}".strip()
                        if k not in history_keys:
                            new_entry = {
                                'date': dd_mm,
                                'time': g.get('time', '00:00'),
                                'home': home,
                                'away': away,
                                'home_logo': g.get('home_logo', ''),
                                'away_logo': g.get('away_logo', ''),
                                'league': g.get('league', ''),
                                'selection': best_tip.get('selection'),
                                'odd': best_tip.get('odd', g.get('odd', 1.0)),
                                'prob': best_tip.get('prob', g.get('prob', 0)),
                                'status': 'PENDING',
                                'score': '0-0',
                                'profit': '0%',
                                'badge': best_tip.get('badge', g.get('badge', '🤖 AI PICK'))
                            }
                            history.insert(0, new_entry)
                            history_keys.add(k)
                            inserted += 1

with open(history_file, 'w', encoding='utf-8') as f:
    json.dump(history, f, indent=4, ensure_ascii=False)

print(f'Inserted {inserted} tips to history.json.')
