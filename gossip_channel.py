
import news_radar
import sys
import time

# Encoding & Style
try:
    sys.stdout.reconfigure(encoding='utf-8')
except: pass

print("\n🚨 [GOSSIP CHANNEL] SCANNER EM TEMPO REAL ATIVADO")
print("📡 Buscando informações privilegiadas na rede...")
print("==================================================")

# Jogos da Imagem (12/02 e 13/02)
# Nota: Odds invertidas? Warriors 3.30 em casa? Spurs 1.38?
# Isso sugere que o GSW está com MUITOS desfalques ou a imagem é de pré-season/G-League?
# Ou Spurs com Wembanyama e Warriors sem Curry/Draymond?
# O Radar vai nos dizer a verdade.
games = [
    {"team1": "Golden State Warriors", "team2": "San Antonio Spurs", "odd1": 3.30, "odd2": 1.38},
    {"team1": "Oklahoma City Thunder", "team2": "Milwaukee Bucks", "odd1": 1.15, "odd2": 4.90}, 
    {"team1": "Utah Jazz", "team2": "Portland Trail Blazers", "odd1": 2.50, "odd2": 1.50},
    {"team1": "Los Angeles Lakers", "team2": "Dallas Mavericks", "odd1": 1.35, "odd2": 3.05}
]

for g in games:
    t1, t2 = g['team1'], g['team2']
    
    print(f"\n🏀 MATCHUP: {t1} x {t2}")
    
    # 1. Busca Notícias (News Radar v2 com Fonte)
    s1, news1 = news_radar.get_team_sentiment(t1, "basketball")
    s2, news2 = news_radar.get_team_sentiment(t2, "basketball")
    
    # 2. Formata Estilo Twitter/X
    # Team 1 Report
    if news1:
        for n in news1:
            print(f"   @{t1.replace(' ','')}: {n}")
    else:
        print(f"   @{t1.replace(' ','')}: 🤫 Silêncio no vestiário (Sem desfalques graves listados hoje).")
        
    # Team 2 Report
    if news2:
        for n in news2:
            print(f"   @{t2.replace(' ','')}: {n}")
    else:
        print(f"   @{t2.replace(' ','')}: 🤫 Nada declarado.")

    # 3. Análise de "Armadilha" (Trap) baseada na Odd vs Notícia
    # Ex: Odd alta (3.30) mas notícias boas? -> VALOR
    # Ex: Odd baixa (1.38) mas notícias ruins? -> ARMADILHA
    
    # Simplificação
    print(f"   💡 INSIGHT:")
    if s1 < -2 and g['odd1'] < 1.50:
         print(f"   ⚠️ CUIDADO com {t1}! Odd baixa ({g['odd1']}) mas elenco baleado.")
    elif s1 > 1 and g['odd1'] > 2.00:
         print(f"   💎 VALOR ESCONDIDO em {t1}! Odd alta ({g['odd1']}) e time com reforços.")
    
    if s2 < -2 and g['odd2'] < 1.50:
         print(f"   ⚠️ CUIDADO com {t2}! Odd baixa ({g['odd2']}) mas elenco baleado.")
    
    # Veredito Final
    score_diff = s1 - s2
    if score_diff > 2:
        print(f"   🔥 TENDÊNCIA: {t1} está mais inteiro fisicamente.")
    elif score_diff < -2:
         print(f"   🔥 TENDÊNCIA: {t2} chega com vantagem física.")
    else:
         print(f"   ⚖️ TENDÊNCIA: Confronto equilibrado nos bastidores.")

    print("   " + "-"*30)
    time.sleep(1) # Efeito dramático

print("\n📡 FIM DA TRANSMISSÃO.")
