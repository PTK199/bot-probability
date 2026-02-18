
import os

file_path = 'd:/BOT PROBABILITY/data_fetcher.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False

for line in lines:
    if '# Fallback to hardcoded database if no real games found or date is old' in line:
        skip = True
    
    if skip and '# --- SCHEDULE FOR WEDNESDAY (11/02) ---' in line:
        skip = False
        new_lines.append("        pass # Hardcoded fallbacks removed. System relies on API.\n")
        continue

    if not skip:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully final hardcoded schedule blocks.")
