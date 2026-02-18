
"""
SPECIALIZED AI MODULES - THE SPECIALISTS 🕵️‍♂️
These modules perform deep-dive analysis on specific markets.
Imported by ai_engine.py to power the Neural Cortex Omega.
"""

try:
    from knowledge_base import SPORTS_KNOWLEDGE
except ImportError:
    SPORTS_KNOWLEDGE = {}

# --- MODULE 1: PARLAY ARCHITECT (ARQUITETO DE MÚLTIPLAS) ---
def architect_parlays(available_games):
    """
    Generates 3 distinct parlay tickets based on strict criteria:
    1. ELITE (Safe, ~3.00)
    2. VALUE (Leverage, ~6.00-10.00)
    3. OVERDRIVE (NBA Points, ~4.00)
    """
    tickets = {
        "elite": {"name": "🛡️ TRIPLA ELITE (Segurança Máxima)", "selections": [], "total_odd": 1.0},
        "value": {"name": "💰 TRIPLA DE VALOR (Risco Calculado)", "selections": [], "total_odd": 1.0},
        "overdrive": {"name": "🏀 TRIPLA OVERDRIVE (NBA Pace)", "selections": [], "total_odd": 1.0}
    }

    # Helper to find team in knowledge base
    def get_team_info(name):
        return SPORTS_KNOWLEDGE.get(name.lower(), {})

    # --- LOGIC FOR ELITE ---
    # Filter: Favorites playing Home with Dominance + Win Rate > 70%
    candidates_elite = []
    for g in available_games:
        home_team = get_team_info(g['home'])
        # Simulating Win Rate check via 'phase'
        phase = home_team.get('phase', '').lower()
        if "dominância" in phase or "máquina" in phase or "campeão" in phase or "império" in phase:
            if g.get('odd_home', 1.5) < 1.60: # Strong favorite
                candidates_elite.append({
                    "match": f"{g['home']} vs {g['away']}",
                    "pick": f"{g['home']} Vence (ou HT)",
                    "odd": float(g.get('odds', {}).get('home', 1.40)),
                    "reason": "Favorito absoluto em casa. Win Rate > 70%. Dominância tática."
                })
    
    # Select Top 3 for Elite
    for pick in candidates_elite[:3]:
        tickets['elite']['selections'].append(pick)
        tickets['elite']['total_odd'] *= pick['odd']

    # --- LOGIC FOR VALUE ---
    # Filter: Handicaps Esticados (NBA) or Zebras
    candidates_value = []
    for g in available_games:
        sport = g.get('sport', '').lower()
        if "nba" in sport:
            # Simulated check for 'Handicap Esticado' - looking for teams on winning streak
            home_info = get_team_info(g['home'])
            if "w" in home_info.get('last_matches', [])[-3:]:
                candidates_value.append({
                    "match": f"{g['home']} vs {g['away']}",
                    "pick": f"{g['away']} +12.5 (Handicap)",
                    "odd": 1.90,
                    "reason": "Handicap esticado. Favorito vem de 3 vitórias por +15."
                })
        elif "zebra" in g.get('details', '').lower() or "crise" in get_team_info(g['home']).get('phase', '').lower():
             candidates_value.append({
                "match": f"{g['home']} vs {g['away']}",
                "pick": f"{g['away']} ou Empate",
                "odd": 2.20,
                "reason": "Zebra jogando contra time desfalcado/em crise."
            })
            
    # Select Top 3 for Value
    for pick in candidates_value[:3]:
        tickets['value']['selections'].append(pick)
        tickets['value']['total_odd'] *= pick['odd']

    # --- LOGIC FOR OVERDRIVE ---
    # Filter: High Pace NBA
    candidates_over = []
    for g in available_games:
        if "nba" in g.get('sport', '').lower():
            # Mock Pace check (assuming high pace teams)
            if "pace" in get_team_info(g['home']).get('coach_style', '').lower() or "pace" in get_team_info(g['away']).get('coach_style', '').lower():
                candidates_over.append({
                    "match": f"{g['home']} vs {g['away']}",
                    "pick": "Over 230.5 Pontos",
                    "odd": 1.90,
                    "reason": "Pace Combinado > 200. Defesas frágeis e transição rápida."
                })
    
    # Select Top 3 for Overdrive
    for pick in candidates_over[:3]:
        tickets['overdrive']['selections'].append(pick)
        tickets['overdrive']['total_odd'] *= pick['odd']

    # Round Odds
    for k in tickets:
        tickets[k]['total_odd'] = round(tickets[k]['total_odd'], 2)

    return tickets

# --- MODULE 2: CORNERS SPECIALIST (ESPEC. ESCANTEIOS) ---
def specialist_corners(match_live_data):
    """
    Analisa Dinâmica de Pressão para Sinais de Cantos.
    Inputs: Blocked Shots, Pressure Index, Scenario.
    """
    sinal = {"market": "N/A", "prob": 0, "reason": ""}
    
    stats = match_live_data.get('stats', {})
    score_h = match_live_data.get('score_h', 0)
    score_a = match_live_data.get('score_a', 0)
    time_str = match_live_data.get('time', "0")
    try:
        time = int(time_str.replace("'", ""))
    except:
        time = 0
    
    # 1. Pressure Index Calculation (Simulated)
    # attacks_dangerous = stats.get('dangerous_attacks', 0)
    # pressure_index = attacks_dangerous / time if time > 0 else 0
    pressure_index = 1.8 # Mock for simulation based on description
    
    # Cenário: Favorito Perdendo em Casa
    odd_home_pre = float(match_live_data.get('odd_home_pre', 2.0))
    is_home_favorito = odd_home_pre < 1.60
    is_losing_or_draw = score_h <= score_a
    
    if is_home_favorito and is_losing_or_draw and time > 70:
        blocked_shots = 8 # Simulated high number for this scenario
        if pressure_index > 1.5 and blocked_shots > 5:
            sinal = {
                "market": "RACE TO CORNERS / OVER LIMIT",
                "prob": 88,
                "reason": f"PRESSÃO EXTREMA: Favorito perdendo aos {time}min. Pressure Index {pressure_index}. Chuva de cruzamentos iminente."
            }
    
    # Cenário: Jogo Travado no Meio
    elif pressure_index < 0.5 and time > 30:
        sinal = {
            "market": "UNDER CANTOS",
            "prob": 75,
            "reason": "Jogo concentrado no círculo central. Baixa incidência de jogadas de linha de fundo."
        }
        
    return sinal

# --- MODULE 3: GOALS PROBABILITY SPECIALIST ---
def specialist_goals(team_a_data, team_b_data):
    """
    Analisa xG e BTTS para prever Over/Under.
    """
    # Simulated Stats (replace with real data hook if available)
    # Assume data comes via SPORTS_KNOWLEDGE details/phase
    
    xg_a = 1.9 # innovative simulation
    xga_b = 1.6
    
    # Adjust variables based on text analysis of team data
    if "ataque devastador" in team_a_data.get('details', '').lower(): xg_a = 2.5
    if "defesa exposta" in team_b_data.get('details', '').lower(): xga_b = 2.0
    if "retranca" in team_b_data.get('coach_dna', '').lower(): xga_b = 0.8
    if "retranca" in team_a_data.get('coach_dna', '').lower(): xg_a = 0.9

    sinal = "No Bet"
    odd_justa = 0.0
    reason = ""
    
    # Logic 1: Over 2.5
    if xg_a > 1.8 and xga_b > 1.5:
        sinal = "OVER 2.5 GOLS"
        odd_justa = 1.70
        reason = "Ataque produtivo (xG > 1.8) vs Defesa vazada (xGA > 1.5)."
    
    # Logic 2: Under 2.5
    elif xg_a < 1.0 and "retranca" in team_b_data.get('coach_dna', '').lower():
        sinal = "UNDER 2.5 GOLS"
        odd_justa = 1.65
        reason = "Ataque ineficiente contra Defesa de bloco baixo."
        
    # Logic 3: Over 0.5 HT (Simulated)
    # if odd_over_ht > 1.60 and history_ht_goals > 70%: ...
    
    return {"sinal": sinal, "odd_justa": odd_justa, "reason": reason}

# --- MODULE 4: NBA TOTALS ANALYST ---
def analyst_nba_totals(team_a_data, team_b_data, current_line=220):
    """
    Analisa PACE e Fatigue para Over/Under na NBA.
    """
    # Mock Data based on coach style
    pace_a = 100
    pace_b = 100
    
    if "posse" in team_a_data.get('coach_dna', '').lower(): pace_a = 96 # Slower
    if "pressão" in team_a_data.get('coach_dna', '').lower(): pace_a = 104 # Faster
    
    combined_pace = pace_a + pace_b
    
    sinal = "No Bet"
    reason = ""
    
    # Logic 1: Valor no Over
    if combined_pace > 205 and current_line < 230:
        sinal = "VALOR NO OVER"
        reason = f"Pace Combinado ({combined_pace}) projeta placar alto. Linha de {current_line} está desajustada."
        
    # Logic 2: Under (Defesa Top 5 vs Slow Pace)
    is_top_defense = "defesa" in team_a_data.get('details', '').lower() or "muralha" in team_a_data.get('phase', '').lower()
    if is_top_defense and pace_b < 98:
        sinal = "UNDER"
        reason = "Defesa de Elite contra time de ritmo lento."
        
    return {"sinal": sinal, "reason": reason}

# --- MODULE 5: THROW-INS SPECIALIST (LATERAIS) ---
def specialist_throwins(match_data):
    """
    Analisa largura do campo e estilo de jogo para LATERAIS.
    """
    width = match_data.get('field_width', 'standard') # narrow, standard, wide
    style = match_data.get('style', 'mixed') # wing_play, midfield
    weather = match_data.get('weather', 'clear')
    
    if style == 'wing_play' or weather == 'rain':
        return {
            "market": "OVER LATERAIS",
            "prob": 80,
            "reason": "Jogo pelas pontas + Clima adverso (erros de domínio)."
        }
    elif style == 'midfield' and width == 'wide':
        return {
            "market": "UNDER LATERAIS",
            "prob": 70,
            "reason": "Campo largo com disputa centralizada. Bola sai pouco."
        }
        
    return {"market": "No Bet", "prob": 50, "reason": "Sem padrão claro."}

# --- MODULE 6: PLAYER PROPS ANALYST (ASSISTS) ---
def analyst_player_props(player_name, sport='football'):
    """
    Analisa probabilidade de Assistência.
    """
    # Database of key passers (mock)
    props = {
        "De Bruyne": {"key_passer": True, "set_pieces": True, "prob_assist": 45},
        "Bruno Fernandes": {"key_passer": True, "set_pieces": True, "prob_assist": 40},
        "Trent Alexander-Arnold": {"key_passer": True, "set_pieces": True, "prob_assist": 38},
        "Vinicius Jr": {"key_passer": False, "set_pieces": False, "prob_assist": 25}, # Winger/Finisher
        "Jokic": {"potential_assists": 15, "usage": 30, "prob_assist_over": 85},
        "Haliburton": {"potential_assists": 18, "usage": 25, "prob_assist_over": 90}, 
        "Trae Young": {"potential_assists": 16, "usage": 32, "prob_assist_over": 88}
    }
    
    p = props.get(player_name)
    if not p: return {"market": "N/A", "reason": f"Sem dados para {player_name}", "min_odd": 0}
    
    if sport == 'football':
        if p.get('key_passer') and p.get('set_pieces'):
            return {"market": "Anytime Assist", "min_odd": 2.50, "reason": "Batedor oficial de bolas paradas e principal criador."}
            
    elif "nba" in sport.lower() or sport == 'basketball':
        if p.get('potential_assists', 0) > 12:
            return {"market": "Over Assists", "reason": f"Gera {p['potential_assists']} chances de arremesso por jogo (Potential Assists)."}
            
    return {"market": "N/A", "reason": "Dados insuficientes para gerar prop.", "min_odd": 0}

# --- MODULE 7: ASIAN HANDICAP SNIPER ---
def sniper_handicaps(team_name, market_line, last_result_context):
    """
    Identifica valor em Handicaps baseado em 'Spots' e reação exagerada do mercado.
    """
    # Logic: Overreaction to last result (Spot Betting)
    
    # Scenario: Favorite just won big (Goleada)
    if "win" in last_result_context.lower() and "goleada" in last_result_context.lower():
        # Market inflates line. E.g. Real Madrid won 5-0, now line is -2.5 (Too high)
        return {
            "sinal": "APOSTAS NO AZARÃO (Underdog)",
            "reason": "Mercado superestimou o favorito após goleada recente. Valor no Handicap Positivo."
        }
        
    # Scenario: Favorite lost unfairly
    if "loss" in last_result_context.lower() and "injusta" in last_result_context.lower():
        # Market drops line. Value on Favorite.
        return {
            "sinal": "VALOR NO FAVORITO",
            "reason": "Favorito subestimado após tropeço. Linha desajustada para baixo."
        }
        
    return {"sinal": "LINHA JUSTA (No Bet)", "reason": "Mercado alinhado com Power Ranking."}

# --- MODULE 8: SHARP MONEY TRACKER (RASTREIO DE DINHEIRO INTELIGENTE) ---
def tracker_sharp_money(team_name, public_pct, line_movement):
    """
    Identifica Reverse Line Movement (RLM).
    Se o público (>70%) está em um lado, mas a linha moveu contra eles,
    o dinheiro Sharpe está no outro lado.
    
    Args:
        team_name (str): Nome do time analisado.
        public_pct (int): Porcentagem de tickets/apostas no time (0-100).
        line_movement (str): 'up' (Odd subiu), 'down' (Odd caiu), 'stable'.
    """
    sinal = {"market": "N/A", "action": "NO BET", "strength": 0, "reason": ""}
    
    # Logic 1: Classic RLM (Public High, Line Moves Against)
    # Ex: 80% apostas no Flamengo, mas Odd subiu de 1.80 para 1.95 (Casas querem mais ação no Fla)
    if public_pct > 75 and line_movement == 'up':
        sinal = {
            "market": f"CONTRA {team_name} (FADE PUBLIC)",
            "action": "SHARP ALERT 🚨",
            "strength": 95,
            "reason": f"80% do público em {team_name}, mas a Odd subiu. As casas estão convidando o público. O dinheiro pesado está no adversário."
        }
        
    # Logic 2: Steam Move (Sharp & Public together)
    # Ex: 80% apostas e Odd despencou (Todo mundo sabe algo)
    elif public_pct > 80 and line_movement == 'down':
        sinal = {
            "market": f"FAVOR DE {team_name} (STEAM)",
            "action": "FOLLOW STEAM 🚂",
            "strength": 80,
            "reason": "Fluxo massivo de dinheiro. Público e Sharps concordam. Linha derretendo."
        }
        
    # Logic 3: Contrarian Value
    # Ex: Ninguém quer o time (20% apostas), linha estável.
    elif public_pct < 25 and line_movement == 'stable':
        sinal = {
            "market": f"FAVOR DE {team_name} (CONTRARIAN)",
            "action": "VALUE BET 💎",
            "strength": 70,
            "reason": f"Apenas {public_pct}% no time. Valor intrínseco pela impopularidade."
        }
        
    return sinal

# --- MODULE 9: NARRATIVE OVERRIDE (LEI DO EX & MOTIVAÇÃO) ---
def narrative_override(player_data, match_context):
    """
    Detecta Fator Humano não estatístico: Lei do Ex, Despedidas, Must Win.
    A 'fome' às vezes vence a matemática.
    """
    sinal = {"trigger": False, "factor": "", "boost": 0}
    
    # Ensure match_context is a string
    ctx = str(match_context).lower() if not isinstance(match_context, str) else match_context.lower()
    
    # 1. Lei do Ex (Revenge Game)
    if player_data.get("ex_club") and player_data["ex_club"].lower() in ctx:
        sinal = {
            "trigger": True,
            "factor": "LEI DO EX ⚖️",
            "boost": 15, # Boost de 15% na probabilidade de gol/ponto
            "reason": f"Jogador enfrentando ex-clube ({player_data['ex_club']}). Motivação extra confirmada."
        }
        
    # 2. Desespero (Relegation Battle)
    elif "rebaixamento" in ctx or "must win" in ctx:
        sinal = {
            "trigger": True,
            "factor": "DESESPERO (Z4) 🆘",
            "boost": 10,
            "reason": "Time jogando a vida. Probabilidade de cartões e escanteios aumentada."
        }
        
    # 3. Aniversário / Recorde
    elif "recorde" in ctx:
        sinal = {
            "trigger": True,
            "factor": "MILESTONE HUNT 🎯",
            "boost": 20,
            "reason": "Jogador buscando recorde histórico na partida. Volume de jogo será forçado nele."
        }

    return sinal


# --- MODULE 10: REFEREE STRICTNESS PROFILE (PERFIL DO ÁRBITRO) ---
def referee_profile_strictness(referee_name, avg_cards, team_fouls_avg):
    """
    Cruza rigor do árbitro com agressividade dos times.
    Alvo: Over Cartões e Expulsões.
    """
    risk_level = "LOW"
    action = "NO BET"
    reason = ""
    
    # Database Simulations (In production, fetch from real DB)
    strict_refs = ["Wilton Pereira Sampaio", "Claus", "Lahoz (Aposentado)", "Oliver"]
    lenient_refs = ["Daronco (Deixa jogar)", "Marciniak"]
    
    is_strict = referee_name in strict_refs or avg_cards > 5.5
    is_aggressive_match = team_fouls_avg > 28 # Combined fouls avg
    
    if is_strict and is_aggressive_match:
        risk_level = "EXTREME 🟥"
        action = "OVER CARTÕES / EXPULSÃO"
        reason = f"Árbitro Rigoroso ({avg_cards} cartões/jogo) + Jogo Pegado ({team_fouls_avg} faltas). Combustível para vermelho."
        
    elif not is_strict and is_aggressive_match:
        risk_level = "MEDIUM"
        action = "OVER FALTAS (S/ CARTÃO)"
        reason = "Jogo pegado, mas árbitro 'deixa jogar'. Tende a muitas faltas, poucos cartões."
        
    elif is_strict and not is_aggressive_match:
        risk_level = "MEDIUM-HIGH"
        action = "OVER CARTÕES (TÉCNICO)"
        reason = "Árbitro gosta de aparecer. Qualquer reclamação vira cartão, mesmo em jogo limpo."

    return {"risk": risk_level, "action": action, "reason": reason}

# --- MODULE 11: LINEUP LEAKS SCRAPER (VARREDURA DE VAZAMENTOS) ---
def scraper_lineup_leaks(team_name, key_player):
    """
    Varre 'Twitter/X' e Fóruns por notícias de última hora (Vazamentos).
    Objetivo: Bloquear aposta se o craque sentiu no aquecimento.
    """
    import random
    
    # Simulation Logic (In production, replace with Selenium/API calls to Twitter)
    # Simulating a 5% chance of a major leak for key players
    leak_found = random.random() < 0.05 
    
    if leak_found:
        return {
            "status": "CRITICAL ALERT 🚨",
            "info": f"VAZAMENTO DETECTADO: {key_player} sentiu no aquecimento!",
            "source": "Twitter/X (Beat Writer)",
            "action": "ABORT BET / CASH OUT",
            "timestamp": "Agora (Pre-Game)"
        }
    
    return {
        "status": "CLEAN", 
        "info": "Nenhum vazamento recente detectado.",
        "action": "PROCEED"
    }

# --- MODULE 12: CHEMISTRY GAP (SINERGIA DE ELENCO) ---
def chemistry_gap_analysis(team_name, lineup_type='bench'):
    """
    Analisa a queda de rendimento (Net Rating) quando os titulares saem.
    Vital para apostas em 2º Quarto (NBA) ou 2º Tempo (Futebol).
    """
    
    # Database of known weak benches (Mock Data based on 2026 rosters)
    weak_benches = ["Lakers", "Suns", "Nuggets (Sem Westbrook)", "Bucks"]
    elite_benches = ["Celtics", "Thunder", "Knicks", "Pacers"]
    
    rating_drop = 0
    warning = "STABLE"
    
    if lineup_type == 'bench':
        if team_name in weak_benches:
            rating_drop = -15.5 # Net Rating despenca
            warning = "CRITICAL DROP 📉"
            reason = "Banco horrível. O time perde a vantagem rapidamente sem os titulares."
        elif team_name in elite_benches:
            rating_drop = -2.0 # Mantém o nível
            warning = "ELITE DEPTH 🛡️"
            reason = "Banco de luxo. Mantém ou amplia a vantagem."
        else:
            rating_drop = -6.5 # Média da liga
            warning = "NORMAL DROP"
            reason = "Queda padrão de rendimento."
            
    return {"net_rating_impact": rating_drop, "warning": warning, "reason": reason}

# --- MODULE 13: LIVE MOMENTUM SWING (LEITURA DE PRESSÃO AO VIVO) ---
def live_momentum_swing(recent_stats):
    """
    Detecta ONDAS DE PRESSÃO (Momentum) nos últimos 5-10 minutos.
    Se o Azarão está amassando, o bot ignora a odd pré-live.
    
    Args:
        recent_stats (dict): stats dos últimos 10min.
        Ex: {'corners': 3, 'dangerous_attacks': 8, 'shots_on_target': 2}
    """
    
    momentum_score = 0
    
    # Pesos para ações recentes
    momentum_score += recent_stats.get('corners', 0) * 1.5
    momentum_score += recent_stats.get('dangerous_attacks', 0) * 0.5
    momentum_score += recent_stats.get('shots_on_target', 0) * 2.0
    momentum_score += recent_stats.get('big_chance_missed', 0) * 3.0
    
    alert = "NEUTRAL"
    action = "WAIT"
    
    # Thresholds
    if momentum_score > 8.0:
        alert = "EXTREME PRESSURE 🔥"
        action = "BET NEXT GOAL (GOL IMINENTE)"
        reason = f"Momentum Score: {momentum_score}. O time está martelando (3+ cantos/chutes em 5min)."
    elif momentum_score > 5.0:
        alert = "HIGH PRESSURE"
        action = "BET CORNERS / OVER"
        reason = "Pressão crescente. Defesa adversária cedendo escanteios."
        
    return {"momentum_score": momentum_score, "alert": alert, "action": action, "reason": reason}

# --- MODULE 14: SELF-CORRECTION LOOP (O MÓDULO DE APRENDIZADO) ---
def self_correction_loop(history_log, current_weights):
    """
    SUPERVISOR DE IA: Analisa erros passados e reajusta pesos.
    Se o 'Sharp Money' falhou 3x seguidas, seu peso diminui.
    Se o 'Momentum Swing' acertou tudo, seu peso aumenta.
    
    Args:
        history_log (list): Lista de dicts [{'module': 'sharp_money', 'result': 'loss'}, ...]
        current_weights (dict): Pesos atuais dos módulos. Ex: {'sharp': 1.0, 'momentum': 1.0}
    """
    
    new_weights = current_weights.copy()
    
    print("--- 🧠 SELF-CORRECTION STARTED ---")
    
    for entry in history_log:
        mod = entry['module']
        res = entry['result']
        
        if mod not in new_weights: continue
        
        # Penaliza erro
        if res == 'loss':
            original = new_weights[mod]
            new_weights[mod] *= 0.95 # Reduz 5% a confiança
            print(f"📉 Penalizando {mod}: {original:.2f} -> {new_weights[mod]:.2f}")
            
        # Recompensa acerto
        elif res == 'win':
            original = new_weights[mod]
            new_weights[mod] *= 1.02 # Aumenta 2% (Crescimento orgânico)
            print(f"📈 Recompensando {mod}: {original:.2f} -> {new_weights[mod]:.2f}")

    # Normalização de segurança (Pesos não podem zerar ou explodir)
    for k, v in new_weights.items():
        if v < 0.5: new_weights[k] = 0.5
        if v > 2.0: new_weights[k] = 2.0

    return new_weights





