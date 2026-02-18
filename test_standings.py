
from espn_api import fetch_standings_from_espn
from data_fetcher import get_table_analysis
import json

def test_nba_standings():
    print("\n--- Testing NBA Standings ---")
    standings = fetch_standings_from_espn("basketball")
    # Print first 2 entries
    count = 0
    for k, v in standings.items():
        print(f"{k}: {v}")
        count += 1
        if count >= 3: break
        
def test_epl_standings():
    print("\n--- Testing EPL Standings ---")
    standings = fetch_standings_from_espn("soccer", "eng.1")
    # Print first 2 entries
    count = 0
    for k, v in standings.items():
        print(f"{k}: {v}")
        count += 1
        if count >= 3: break

def test_analysis():
    print("\n--- Testing Table Analysis (NBA) ---")
    # Using teams likely to be in the NBA standings
    print(get_table_analysis("Celtics", "Lakers", "basketball"))
    
    print("\n--- Testing Table Analysis (EPL) ---")
    print(get_table_analysis("Man City", "Arsenal", "football"))


if __name__ == "__main__":
    test_nba_standings()
    test_epl_standings()
    test_analysis()
