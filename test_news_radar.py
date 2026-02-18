import news_radar

print(" --- TESTANDO RADAR DE NOTÍCIAS PT-BR (SAFE PRINT) ---")

teams = ["Golden State Warriors", "Lakers"]

for team in teams:
    print(f"\nBusca por: {team}")
    try:
        score, news = news_radar.get_team_sentiment(team)
        print(f"Score: {score}")
        print(f"Notícias ({len(news)}):")
        for n in news:
            # Remove emojis para evitar erro de encoding no terminal Windows
            safe_n = n.encode('ascii', 'ignore').decode('ascii')
            # Se a string ficar vazia, tenta imprimir normal com tratamento de erro
            if not safe_n:
                 safe_n = n.encode('utf-8', 'ignore')
            print(f" - {safe_n}")
            
    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

print("\n--- FIM DO TESTE ---")
