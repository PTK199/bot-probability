from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import json

def get_betano_nba_props():
    print("[SCRAPER] Iniciando Betano Headless Scraper...")
    
    # Configurar Chrome Options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # Run invisible
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")
    # Simulate a real user agent to bypass basic blocks
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    # Iniciar o driver silenciosamente
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://br.betano.com/sport/basquete/competitions/eua/17106/"
        print(f"[SCRAPER] Navegando para: {url}")
        driver.get(url)
        
        # Wait for Cloudflare/Datadome
        print("[SCRAPER] Aguardando renderizacao principal (10s)...")
        time.sleep(10)
        
        # Extrair estado inicial
        raw_html = driver.page_source
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        match_urls = []
        
        # Encontrar links dos jogos varrendo os elementos <a>
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Betano match URLs typically look like: /odds/nome-do-time-a-nome-do-time-b/12345/
            if '/odds/' in href and href not in match_urls:
                match_urls.append("https://br.betano.com" + href)
                        
        print(f"[SCRAPER] Encontrados {len(match_urls)} jogos via HTML. Raspando Props...")
        
        results = {}
        for m_url in match_urls[:3]: # Limit to first 3 for test safety
            print(f" -> Raspando Jogo: {m_url}")
            driver.get(m_url)
            time.sleep(5) # Let initial rendering finish
            
            # Tentar clicar na aba "Jogadores" usando JavaScript para forçar o lazy-loading
            try:
                # Betano usually has tabs with class 'tab' or role 'tab' containing 'Jogadores'
                script = """
                let tabs = document.querySelectorAll('div[role="tab"], button[role="tab"], a');
                for (let t of tabs) {
                    if (t.innerText && t.innerText.includes('Jogadores')) {
                        t.click();
                        return true;
                    }
                }
                return false;
                """
                clicked = driver.execute_script(script)
                if clicked:
                    print("   [+] Aba 'Jogadores' clicada. Aguardando Props...")
                    time.sleep(4) # Wait for network request
            except Exception as e:
                print(f"   [-] Erro ao clicar na aba: {e}")

            m_soup = BeautifulSoup(driver.page_source, 'html.parser')
            m_state = {}
            for s in m_soup.find_all('script'):
                if s.string and 'window["initial_state"]=' in s.string:
                    raw = s.string.strip().replace('window["initial_state"]=', '', 1)
                    if raw.endswith(';'): raw = raw[:-1]
                    try: m_state = json.loads(raw)
                    except: pass
                    break
                    
            # Look for markets: Pontos do Jogador
            props_found_in_game = 0
            if 'data' in m_state and 'event' in m_state['data']:
                event_data = m_state['data']['event']
                for market in event_data.get('markets', []):
                    # In some Betano versions it's "Mais/Menos Pontos - <Player Name>" or similar
                    target_market = False
                    name = market.get('name', '')
                    if 'Pontos' in name and ('Jogador' in name or '-' in name): target_market = True
                    
                    if target_market:
                        for selection in market.get('selections', []):
                            p_name = selection.get('name', '')
                            odd = selection.get('price', 1.0)
                            line = market.get('handicap', 0.0) 
                            
                            if "Mais" in p_name or "Over" in p_name:
                                clean_name = p_name.replace("Mais de ", "").replace("Over ", "")
                                if clean_name not in results:
                                    results[clean_name] = {"lines": {"betano": {}}}
                                results[clean_name]["lines"]["betano"]["Over"] = {"val": line, "odd": odd}
                                props_found_in_game += 1
                                print(f"   [+] Prop Found: {clean_name} Over {line} @ {odd}")
            
            # Fallback text search if initial_state fails
            if props_found_in_game == 0:
                 # Check if the properties are just rendered in HTML spans
                 print("   [-] Props JSON failed. Tentando parse html bruto...")
                 # (Not implemented yet to save complexity)
                                
        print(f"[SCRAPER] Extraidos props de {len(results)} jogadores.")
        
        with open("cache_odds/nba_player_points_betano.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        return results
        
    except Exception as e:
        print(f"[SCRAPER] Erro Critico: {e}")
        return {}
    finally:
        driver.quit()

if __name__ == "__main__":
    get_betano_nba_props()
