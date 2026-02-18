
import os
import requests
import sys
import json
import datetime

# Force output encoding (safe)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Fallback to requests if supabase SDK fails
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

class SupabaseClient:
    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

    def table(self, table_name):
        return SupabaseQueryBuilder(self.url, table_name, self.headers)

class SupabaseQueryBuilder:
    def __init__(self, base_url, table_name, headers):
        self.endpoint = f"{base_url}/rest/v1/{table_name}"
        self.headers = headers

    def insert(self, data):
        try:
            response = requests.post(self.endpoint, headers=self.headers, json=data)
            if response.status_code >= 400:
                 print(f"❌ Insert Error {response.status_code}: {response.text}")
            return response
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return None

    def upsert(self, data, on_conflict="key"):
        headers = self.headers.copy()
        headers["Prefer"] = f"resolution=merge-duplicates"
        final_url = f"{self.endpoint}?on_conflict={on_conflict}"
        
        try:
            response = requests.post(final_url, headers=headers, json=data)
            if response.status_code >= 400:
                 print(f"❌ Upsert Error {response.status_code}: {response.text}")
            return response
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return None

    def select(self, columns="*", eq_field=None, eq_value=None):
        try:
            query = f"?select={columns}"
            if eq_field and eq_value:
                query += f"&{eq_field}=eq.{eq_value}"
            
            response = requests.get(
                f"{self.endpoint}{query}",
                headers=self.headers
            )
            if response.status_code < 300:
                return response.json()
        except:
            pass
        return []

def get_supabase():
    if not url or not key:
        return None
    return SupabaseClient(url, key)

def upload_teams(knowledge_base):
    client = get_supabase()
    if not client: 
        print("⚠️ Supabase Credentials Missing.")
        return

    print(f"📡 Connecting to Supabase via Raw HTTP: {client.url}")
    
    count = 0
    for team_key, data in knowledge_base.items():
        try:
            team_payload = {
                "key": team_key,
                "name": data.get("name", team_key.title()),
                "sport": data.get("sport", "Unknown"),
                "phase": data.get("phase", "Neutral"),
                "coach": data.get("coach", "Unknown"),
                "details": data.get("details", "")
            }
            res = client.table("teams").upsert(team_payload)
            
            if res and res.status_code < 300:
                print(f"✅ Uploaded Team: {team_key}")
                count += 1
                
                if "key_players" in data:
                     for p_name in data["key_players"]:
                         p_payload = {
                             "team_key": team_key,
                             "name": p_name,
                             "is_key_player": True
                         }
                         client.table("players").insert(p_payload)
            else:
                print(f"⚠️ Skipping players for {team_key} due to team error.")

        except Exception as e:
            print(f"❌ Critical Error uploading {team_key}: {e}")
            
    print(f"\n🎉 Total Teams Uploaded: {count}")

def sync_trebles_to_cloud():
    """Syncs local trebles history to Supabase."""
    client = get_supabase()
    if not client: return {"status": "error", "message": "No credentials"}
    
    import data_fetcher
    try:
        trebles = data_fetcher.get_history_trebles()
    except:
        return {"status": "error", "message": "Failed to get trebles"}
    
    count = 0
    for t in trebles:
        try:
            # Check for duplicates (Simple check by date and name)
            existing = client.table("trebles").select("*", eq_field="name", eq_value=t["name"])
            is_dup = False
            if existing:
                for e in existing:
                    if e.get('date') == t['date']:
                        is_dup = True
                        break
            
            if is_dup:
                print(f"⚠️ Treble already exists: {t['name']}")
                continue
                
            payload = {
                "date": t["date"],
                "name": t["name"],
                "odd": float(t["odd"]),
                "status": t["status"],
                "profit": t["profit"],
                "selections": t["selections"],
                "synced_at": datetime.datetime.now().isoformat()
            }
            
            res = client.table("trebles").insert(payload)
            if res and res.status_code < 300:
                count += 1
                print(f"✅ Treble Synced: {t['name']}")
        except Exception as e:
            print(f"❌ Error syncing treble: {e}")
            
    return {"status": "success", "synced": count}

def log_match_prediction(home_team, away_team, prediction_json, match_id=None):
    """
    Logs the AI's final prediction to the cloud database for future audit/learning.
    """
    client = get_supabase()
    if not client: return

    import uuid
    if not match_id:
        match_id = str(uuid.uuid4())
    
    payload = {
        "match_id": match_id,
        "home_team": home_team,
        "away_team": away_team, 
        "prediction_data": prediction_json,
        "outcome": "PENDING"
    }
    
    try:
        res = client.table("predictions").insert(payload)
        if res and res.status_code < 300:
            print(f"📝 Previsão salva na nuvem: {home_team} vs {away_team}")
        else:
            print(f"⚠️ Erro ao salvar log na nuvem: {res.text if res else 'None'}")
    except Exception as e:
        print(f"❌ Erro de conexão ao salvar log: {e}")


def sync_history_to_cloud():
    """
    Syncs local history.json to Supabase cloud for backup and analytics.
    """
    client = get_supabase()
    if not client:
        return {"status": "error", "message": "Supabase not configured"}
    
    history_file = 'history.json'
    if not os.path.exists(history_file):
        return {"status": "error", "message": "No history.json found"}
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        return {"status": "error", "message": "Failed to read history.json"}
    
    synced = 0
    for entry in history:
        match_key = f"{entry.get('date','')}-{entry.get('home','')}-{entry.get('away','')}"
        payload = {
            "key": match_key,
            "date": entry.get("date", ""),
            "home_team": entry.get("home", ""),
            "away_team": entry.get("away", ""),
            "league": entry.get("league", ""),
            "selection": entry.get("selection", ""),
            "odd": float(entry.get("odd", 0)),
            "prob": int(entry.get("prob", 0)),
            "status": entry.get("status", "PENDING"),
            "score": entry.get("score", ""),
            "profit": entry.get("profit", ""),
            "synced_at": datetime.datetime.now().isoformat()
        }
        
        try:
            res = client.table("history").upsert(payload, on_conflict="key")
            if res and res.status_code < 300:
                synced += 1
        except:
            continue
    
    return {"status": "success", "synced": synced, "total": len(history)}
