from espn_api import fetch_from_espn_api

def debug_city():
    results = fetch_from_espn_api("2026-02-11")
    
    # Simulate the logic in update_history_v3
    home_team = "Manchester City"
    away_team = "Fulham"
    
    res = results.get(home_team) # Should be None
    if not res:
        res = results.get(away_team) # Should get Fulham object
        
    print(f"Res found via away? {res is not None}")
    if res:
        print(f"Res key example: {res.get('away')}") # Just to see
        print(f"Score raw: {res.get('score')}") # "0-3"
        
        s_parts = res['score'].split('-')
        val1 = int(s_parts[0])
        val2 = int(s_parts[1])
        
        home_direct = results.get(home_team)
        print(f"home_direct: {home_direct}")
        
        is_match = (res == home_direct)
        print(f"res == home_direct: {is_match}")
        
        if is_match:
            h_score = val1
            a_score = val2
            print("Logic Path: IF (Match)")
        else:
            h_score = val2
            a_score = val1
            print("Logic Path: ELSE (Swap)")
            
        print(f"Calculated: {home_team} {h_score} - {a_score} {away_team}")

if __name__ == "__main__":
    debug_city()
