import json
import collections

with open('history.json', 'r', encoding='utf-8') as f:
    history = json.load(f)

stats = collections.Counter()
scores = collections.Counter()
badges = collections.Counter()
dates = collections.Counter()

import sys
import io

# Fix output encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for h in history:
    stats[h.get('status')] += 1
    scores[h.get('score')] += 1
    badges[h.get('badge')] += 1
    dates[h.get('date')] += 1

print(f"Total entries: {len(history)}")
print("\nStatuses:")
for k, v in stats.items():
    print(f"  {k}: {v}")

print("\nTop 10 Scores:")
for k, v in scores.most_common(10):
    print(f"  {k}: {v}")

print("\nBadges Breakdown:")
for k, v in badges.items():
    print(f"  {k}: {v}")

print("\nRecent Dates:")
for k, v in sorted(dates.items(), key=lambda x: x[0], reverse=True)[:10]:
    print(f"  {k}: {v}")

# Find suspected false greens
false_greens = [h for h in history if h.get('status') == 'WON' and h.get('score') in ['0-0', '2-2', '1-1']]
print(f"\nSuspected False/Weak Greens (0-0, 1-1, 2-2): {len(false_greens)}")

# Analyze 19/02 and 20/02
print("\nEntries for 19/02 and 20/02:")
for d in ['19/02', '20/02']:
    d_entries = [h for h in history if h.get('date') == d]
    print(f"  {d}: {len(d_entries)} entries ({len([x for x in d_entries if x.get('status') == 'WON'])} Green)")
