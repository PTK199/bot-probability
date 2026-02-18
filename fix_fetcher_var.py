
import os
import sys

file_path = 'd:/BOT PROBABILITY/data_fetcher.py'

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Ensure processed_games is initialized before dynamic loop
    if "resolved_games = set()" in line:
        new_lines.append(line)
        new_lines.append("    processed_games = [] # Ensure initialized before loop\n")
        continue

    new_lines.append(line)

# Handle potential indentation errors if block was removed poorly
# Just simple pass for safety

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed processed_games initialization.")
