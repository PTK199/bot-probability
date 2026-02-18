import json

def final_sync():
    with open('history.json', 'r', encoding='utf-8') as f:
        h = json.load(f)

    for e in h:
        if e.get('date') == '11/02':
            home = e.get('home', '')
            score = e.get('score', '')
            sel = e.get('selection', '').lower()
            
            # Man City (3-0)
            if 'City' in home and '3-0' in score:
                e['status'] = 'WON'
                e['profit'] = '+39%'
            
            # Aston Villa (1-0)
            if 'Villa' in home and '1-0' in score:
                e['status'] = 'WON'
                e['profit'] = '+102%'
            
            # Crystal Palace (2-3)
            if 'Palace' in home and '2-3' in score:
                e['status'] = 'LOST'
                e['profit'] = '-100%'
                
            # Sunderland (0-1) -> Liverpool won
            if 'Sunderland' in home and '0-1' in score:
                e['status'] = 'WON'
                e['profit'] = '+78%'
            
            # Nottingham (0-0)
            if 'Nottingham' in home and '0-0' in score:
                e['status'] = 'LOST'
                e['profit'] = '-100%'

    with open('history.json', 'w', encoding='utf-8') as f:
        json.dump(h, f, indent=4, ensure_ascii=False)
    print("MANDATORY FIX APPLIED.")

if __name__ == "__main__":
    final_sync()
