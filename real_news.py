import requests
import xml.etree.ElementTree as ET
import urllib.parse
import re

# ---------------------------------------------------------
# TRADUTOR TÁTICO (INGLÊS -> PORTUGUÊS)
# ---------------------------------------------------------
def translate_sports_term(text):
    """
    Traduz manchetes esportivas do inglês para português focado em apostas.
    """
    text = text.lower()
    replacements = {
        "out": "FORA", "injury": "lesão", "injured": "lesionado",
        "doubtful": "DÚVIDA", "questionable": "questionável", "probable": "provável",
        "return": "retorno", "returns": "retorna", "miss": "perde",
        "game": "jogo", "vs": "contra", "ankle": "tornozelo", "knee": "joelho", 
        "hamstring": "coxa", "back": "costas", "soreness": "dores", 
        "surgery": "cirurgia", "trade": "troca", "rumors": "rumores", 
        "sources": "fontes", "coach": "técnico", "win": "vitória", 
        "loss": "derrota", "preview": "prévia", "recap": "resumo", 
        "report": "relatório", "lineup": "escalação", "roster": "elenco",
        "suspension": "suspensão", "suspended": "suspenso",
        "breaking": "URGENTE"
    }
    
    for en, pt in replacements.items():
        # Substitui palavra inteira
        text = re.sub(r'\b' + re.escape(en) + r'\b', pt, text)
        
    # Capitaliza a primeira letra
    return text.capitalize()

# ---------------------------------------------------------
# BUSCADOR GOOGLE NEWS (BR + US)
# ---------------------------------------------------------
def fetch_google_news(query, lang="pt"):
    """
    Busca no RSS do Google News.
    lang='pt' -> Google News BR (Português)
    lang='en' -> Google News US (Inglês) -> Traduzido
    """
    try:
        hl = "pt-BR" if lang == "pt" else "en-US"
        gl = "BR" if lang == "pt" else "US"
        ceid = f"{gl}:{hl}"
        
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl={hl}&gl={gl}&ceid={ceid}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        resp = requests.get(url, headers=headers, timeout=5)
        news_items = []
        
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            for item in root.findall('./channel/item')[:3]:
                title = item.find('title').text
                
                # Limpeza de Fonte
                if " - " in title:
                    title = title.rsplit(" - ", 1)[0].strip()
                    
                # Tradução se for EN
                if lang == "en":
                    title = f"[U$] {translate_sports_term(title)}"
                else:
                    title = f"[BR] {title}"
                    
                news_items.append(title)
                
        return news_items
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar news para '{query}': {e}")
        return []

# ---------------------------------------------------------
# FUNÇÃO PRINCIPAL (INVESTIGAÇÃO)
# ---------------------------------------------------------
def search_team_news(team_name, sport="basketball"):
    """
    Realiza a varredura tática em duas etapas:
    1. Busca BR (Prioridade)
    2. Busca US (Se for NBA/Basquete)
    Retorna uma string resumida.
    """
    print(f"🕵️ Real News: Investigando '{team_name}'...")
    
    # 1. Busca Brasil (Sempre)
    news_br = fetch_google_news(f'"{team_name}"', lang="pt")
    
    # 2. Busca USA (Se for NBA ou time internacional relevante)
    # Detecta se é NBA por keywords comuns ou parametro sport
    is_nba = "basketball" in sport.lower() or any(x in team_name.lower() for x in ["warriors", "lakers", "celtics", "bulls", "heat", "suns", "mavs", "knicks", "nets", "spurs"])
    
    news_us = []
    if is_nba:
        news_us = fetch_google_news(f'"{team_name}" NBA', lang="en")
    
    # Combina resultados (US tem prioridade na NBA por ser mais rápido)
    if is_nba:
        all_news = news_us + news_br
    else:
        all_news = news_br
        
    # Deduplica e limita
    unique_news = []
    seen = set()
    for n in all_news:
        if n not in seen:
            unique_news.append(n)
            seen.add(n)
            
    if not unique_news:
        return "Nenhuma notícia relevante de última hora encontrada nas redes."
        
    # Retorna as 2 mais recentes formatadas
    return " | ".join(unique_news[:2])
