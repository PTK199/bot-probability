import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
}

# common endpoint for Betano BR
urls = [
    'https://br.betano.com/api/sport/basquete/competitions/17106/',
    'https://br.betano.com/api/sport/basquete/ligas/17106/',
    'https://br.betano.com/api/sport/basketball/matches/'
]

for url in urls:
    try:
        print(f"Testing {url}")
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print("SUCCESS!")
            # Save a sample to inspect
            with open('betano_sample.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            break
        else:
            print(f"Status: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")
