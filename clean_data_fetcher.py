
import os

file_path = 'd:/BOT PROBABILITY/data_fetcher.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
skip_trebles_1 = False
skip_trebles_2 = False

for i, line in enumerate(lines):
    # 1. Remove Hardcoded Match Analysis (FEB 5th - 10th)
    if '# --- FEB 5TH ANALYSIS (Existing) ---' in line:
        skip = True
    
    if skip and '# Fallback Logic' in line:
        skip = False
        # Insert a comment to indicate dynamic logic takes over
        new_lines.append("        # --- DYNAMIC LOGIC ENGAGED (Hardcoded Dates Removed) ---\n")

    # 2. Remove Hardcoded Trebles Part 1
    if 'if target_date == "2026-02-09":' in line and 'trebles =' in lines[i-1]:
        skip_trebles_1 = True
    
    if skip_trebles_1 and '# --- RISK FACTOR SYSTEM' in line:
        skip_trebles_1 = False
        # Insert Dynamic Treble Logic here
        dynamic_trebles = """    # --- DYNAMIC TREBLE GENERATOR (V2.0) ---
    trebles = []
    
    # 1. Sort games by Safety (Prob) and Value (Odd)
    safe_candidates = sorted(
        [g for g in processed_games if g.get('best_tip', {}).get('prob', 0) >= 80], 
        key=lambda x: x['best_tip']['prob'], 
        reverse=True
    )
    
    value_candidates = sorted(
        [g for g in processed_games if 1.70 <= float(g.get('best_tip', {}).get('odd', 0)) <= 2.50], 
        key=lambda x: float(x['best_tip']['odd']), 
        reverse=True
    )

    # 2. Build Returns
    # A) TRIPLA BLINDADA (Safety)
    if len(safe_candidates) >= 3:
        selection = safe_candidates[:3]
        total_odd = 1.0
        pick_list = []
        for s in selection:
            odd = float(s['best_tip']['odd'])
            total_odd *= odd
            pick_list.append(f"- {s['home_team']} vs {s['away_team']}: {s['best_tip']['selection']} (@{odd:.2f})")
            
        trebles.append({
            "name": "🛡️ TRIPLA BLINDADA (IA)",
            "total_odd": f"{total_odd:.2f}",
            "probability": "85%",
            "selections": [{"match": f"{s['home_team']}", "pick": f"{s['best_tip']['selection']} (@{s['best_tip']['odd']})" } for s in selection],
            "copy_text": "🛡️ TRIPLA BLINDADA:\\n" + "\\n".join(pick_list) + f"\\nOdd Total: {total_odd:.2f}"
        })

    # B) TRIPLA VALOR (Value)
    if len(value_candidates) >= 3:
        selection = value_candidates[:3]
        total_odd = 1.0
        pick_list = []
        for s in selection:
            odd = float(s['best_tip']['odd'])
            total_odd *= odd
            pick_list.append(f"- {s['home_team']} vs {s['away_team']}: {s['best_tip']['selection']} (@{odd:.2f})")

        trebles.append({
            "name": "🔥 TRIPLA VALOR (IA)",
            "total_odd": f"{total_odd:.2f}",
            "probability": "65%",
            "selections": [{"match": f"{s['home_team']}", "pick": f"{s['best_tip']['selection']} (@{s['best_tip']['odd']})" } for s in selection],
            "copy_text": "🔥 TRIPLA VALOR:\\n" + "\\n".join(pick_list) + f"\\nOdd Total: {total_odd:.2f}"
        })
    elif len(value_candidates) >= 2 and len(safe_candidates) >= 1:
        # Fallback Mix
        selection = value_candidates[:2] + safe_candidates[:1]
        total_odd = 1.0
        pick_list = []
        for s in selection:
            odd = float(s['best_tip']['odd'])
            total_odd *= odd
            pick_list.append(f"- {s['home_team']} vs {s['away_team']}: {s['best_tip']['selection']} (@{odd:.2f})")

        trebles.append({
            "name": "⚖️ TRIPLA MISTA (IA)",
            "total_odd": f"{total_odd:.2f}",
            "probability": "75%",
            "selections": [{"match": f"{s['home_team']}", "pick": f"{s['best_tip']['selection']} (@{s['best_tip']['odd']})" } for s in selection],
            "copy_text": "⚖️ TRIPLA MISTA:\\n" + "\\n".join(pick_list) + f"\\nOdd Total: {total_odd:.2f}"
        })

"""
        new_lines.append(dynamic_trebles)

    # 3. Remove Hardcoded Trebles Part 2 (Feb 11th)
    if 'if target_date == "2026-02-11":' in line:
        skip_trebles_2 = True
    
    if skip_trebles_2 and 'return {"games": processed_games' in line:
        skip_trebles_2 = False

    if not skip and not skip_trebles_1 and not skip_trebles_2:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully successfully removed hardcoded logic and injected dynamic generators.")
