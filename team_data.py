"""
🏟️ TEAM DATA & SCOUTING MODULE
Extracted from data_fetcher.py for modularity.
Contains: logos, simulations, news, tactics, table analysis.
"""

import numpy as np
import random

# --- TEAM LOGOS ---
TEAM_LOGOS = {
    # NBA
    "Lakers": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Los_Angeles_Lakers_logo.svg",
    "Warriors": "https://upload.wikimedia.org/wikipedia/en/thumb/0/01/Golden_State_Warriors_logo.svg/1200px-Golden_State_Warriors_logo.svg.png",
    "Nuggets": "https://upload.wikimedia.org/wikipedia/en/thumb/7/76/Denver_Nuggets.svg/1200px-Denver_Nuggets.svg.png",
    "Heat": "https://upload.wikimedia.org/wikipedia/en/thumb/f/fb/Miami_Heat_logo.svg/1200px-Miami_Heat_logo.svg.png",
    "Celtics": "https://upload.wikimedia.org/wikipedia/en/thumb/8/8f/Boston_Celtics.svg/1200px-Boston_Celtics_logo.svg.png",
    "Bucks": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4a/Milwaukee_Bucks_logo.svg/1200px-Milwaukee_Bucks_logo.svg.png",
    "Suns": "https://upload.wikimedia.org/wikipedia/en/thumb/d/dc/Phoenix_Suns_logo.svg/1200px-Phoenix_Suns_logo.svg.png",
    "Clippers": "https://upload.wikimedia.org/wikipedia/en/thumb/b/bb/Los_Angeles_Clippers_logo.svg/1200px-Los_Angeles_Clippers_logo.svg.png",
    "Mavericks": "https://upload.wikimedia.org/wikipedia/en/thumb/9/97/Dallas_Mavericks_logo.svg/1200px-Dallas_Mavericks_logo.svg.png",
    "Mavs": "https://upload.wikimedia.org/wikipedia/en/thumb/9/97/Dallas_Mavericks_logo.svg/1200px-Dallas_Mavericks_logo.svg.png",
    "Knicks": "https://upload.wikimedia.org/wikipedia/en/thumb/2/25/New_York_Knicks_logo.svg/1200px-New_York_Knicks_logo.svg.png",
    "Sixers": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0e/Philadelphia_76ers_logo.svg/1200px-Philadelphia_76ers_logo.svg.png",
    "Cavs": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4b/Cleveland_Cavaliers_logo.svg/1200px-Cleveland_Cavaliers_logo.svg.png",
    "Magic": "https://upload.wikimedia.org/wikipedia/en/thumb/1/10/Orlando_Magic_logo.svg/1200px-Orlando_Magic_logo.svg.png",
    "Thunder": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5d/Oklahoma_City_Thunder.svg/1200px-Oklahoma_City_Thunder.svg.png",
    "Wolves": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/Minnesota_Timberwolves_logo.svg/1200px-Minnesota_Timberwolves_logo.svg.png",
    "Timberwolves": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/Minnesota_Timberwolves_logo.svg/1200px-Minnesota_Timberwolves_logo.svg.png",
    "Grizzlies": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f1/Memphis_Grizzlies.svg/1200px-Memphis_Grizzlies.svg.png",
    "Pelicans": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0d/New_Orleans_Pelicans_logo.svg/1200px-New_Orleans_Pelicans_logo.svg.png",
    "Kings": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c7/SacramentoKings.svg/1200px-SacramentoKings.svg.png",
    "Jazz": "https://upload.wikimedia.org/wikipedia/en/thumb/0/04/Utah_Jazz_logo_%282016%29.svg/1200px-Utah_Jazz_logo_%282016%29.svg.png",
    "Blazers": "https://upload.wikimedia.org/wikipedia/en/thumb/2/21/Portland_Trail_Blazers_logo.svg/1200px-Portland_Trail_Blazers_logo.svg.png",
    "Hawks": "https://upload.wikimedia.org/wikipedia/en/thumb/2/24/Atlanta_Hawks_logo.svg/1200px-Atlanta_Hawks_logo.svg.png",
    "Hornets": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c4/Charlotte_Hornets_%282014%29.svg/1200px-Charlotte_Hornets_%282014%29.svg.png",
    "Pistons": "https://upload.wikimedia.org/wikipedia/commons/7/7c/Pistons_logo17.svg",
    "Pacers": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1b/Indiana_Pacers.svg/1200px-Indiana_Pacers.svg.png",
    "Wizards": "https://upload.wikimedia.org/wikipedia/en/thumb/0/02/Washington_Wizards_logo.svg/1200px-Washington_Wizards_logo.svg.png",
    "Rockets": "https://upload.wikimedia.org/wikipedia/en/thumb/2/28/Houston_Rockets.svg/1200px-Houston_Rockets_logo.svg.png",
    "Spurs": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/San_Antonio_Spurs.svg/1200px-San_Antonio_Spurs_logo.svg.png",
    "Nets": "https://upload.wikimedia.org/wikipedia/commons/4/44/Brooklyn_Nets_newlogo.svg",
    "Raptors": "https://upload.wikimedia.org/wikipedia/en/thumb/3/36/Toronto_Raptors_logo.svg/1200px-Toronto_Raptors_logo.svg.png",
    # Football
    "Flamengo": "https://logodownload.org/wp-content/uploads/2016/09/flamengo-logo-escudo-novo-2.png",
    "Vitória": "https://logodownload.org/wp-content/uploads/2017/02/esporte-clube-vitoria-logo-escudo-1.png",
    "Chelsea": "https://upload.wikimedia.org/wikipedia/en/thumb/c/cc/Chelsea_FC.svg/1200px-Chelsea_FC.svg.png",
    "West Ham": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/West_Ham_United_FC_logo.svg/1200px-West_Ham_United_FC_logo.svg.png",
    "Arsenal": "https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Arsenal_FC.svg/1200px-Arsenal_FC.svg.png",
    "Liverpool": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Liverpool_FC.svg/1200px-Liverpool_FC.svg.png",
    "Man City": "https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Manchester_City_FC_badge.svg/1200px-Manchester_City_FC_badge.svg.png",
    "Bayern": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/FC_Bayern_M%C3%BCnchen_logo_%282002%E2%80%932017%29.svg/1200px-FC_Bayern_M%C3%BCnchen_logo_%282002%E2%80%932017%29.svg.png",
    "Real Madrid": "https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Real_Madrid_CF.svg/1200px-Real_Madrid_CF.svg.png",
    "Barcelona": "https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_%28crest%29.svg/1200px-FC_Barcelona_%28crest%29.svg.png",
}


def get_logo_url(team_name, sport='unknown'):
    """Returns the logo URL for a team."""
    clean_name = team_name.replace(" FC", "").replace(" SC", "").strip()
    
    if clean_name in TEAM_LOGOS:
        return TEAM_LOGOS[clean_name]
        
    for key, url in TEAM_LOGOS.items():
        if key in clean_name or clean_name in key:
            return url
            
    if sport == 'basketball':
        return "https://cdn-icons-png.flaticon.com/512/3159/3159057.png"
    elif sport in ('football', 'soccer'):
        return "https://cdn-icons-png.flaticon.com/512/53/53283.png"
        
    return "https://cdn-icons-png.flaticon.com/512/10606/10606233.png"


def simulate_nba_game(home_team, away_team):
    """Simulates an NBA game 5,000 times using Monte Carlo logic."""
    power_ratings = {
        "Pistons": 98, "Celtics": 93, "Knicks": 92, "Cavaliers": 91, 
        "Thunder": 93, "Rockets": 90, "Raptors": 89, "Sixers": 87, 
        "Nuggets": 86, "Timberwolves": 85, "Magic": 84, "Clippers": 82,
        "Warriors": 81, "Suns": 80, "Mavericks": 78, "Heat": 79,
        "Kings": 78, "Grizzlies": 80, "Lakers": 77, "Hawks": 76,
        "Hornets": 75, "Spurs": 74, "Bulls": 74, "Pelicans": 72,
        "Bucks": 71, "Jazz": 69, "Blazers": 67, "Nets": 65, 
        "Pacers": 62, "Wizards": 61
    }
    
    h_power = power_ratings.get(home_team, 75)
    a_power = power_ratings.get(away_team, 75)
    h_power += 3  # Home court advantage
    
    iterations = 5000
    home_wins = 0
    total_h_score = 0
    total_a_score = 0
    
    for _ in range(iterations):
        base_score = 115
        h_score = int(np.random.normal(base_score + (h_power - 80), 12))
        a_score = int(np.random.normal(base_score + (a_power - 80), 12))
        
        if h_score > a_score:
            home_wins += 1
        total_h_score += h_score
        total_a_score += a_score
            
    avg_h = int(total_h_score / iterations)
    avg_a = int(total_a_score / iterations)
    prob_h = (home_wins / iterations) * 100
    
    return {
        "avg_score": f"{avg_h}-{avg_a}",
        "home_win_prob": round(prob_h, 1),
        "away_win_prob": round(100 - prob_h, 1),
        "total_avg": avg_h + avg_a
    }


def get_news_investigation(team_name, player=None):
    """Simulates a 'Detective' search for last minute news."""
    news_db = {
        "Bulls": "🚨 FOFOCA: Lavine discutiu com o técnico no treino e pode ter minutos reduzidos.",
        "Nuggets": "✅ CONFIRMADO: Murray treinou normalmente. Time titular completo.",
        "Lakers": "⚠️ ALERTA: LeBron postou '⏳' no Instagram. Risco de descanso.",
        "Warriors": "🚨 DESFALQUE: Curry está com gripe e não viajou.",
        "River Plate": "🚨 CLIMA TENSO: Torcida protestou na saída do ônibus.",
        "Tigre": "✅ FOCADO: Time recebeu bicho extra pela liderança.",
        "Magic": "✅ ELENCO: Todos disponíveis. Franz Wagner recuperado.",
        "Jazz": "⚠️ TRADE RUMORS: Markkanen pode ser poupado (DNP - Trade Pending)."
    }
    
    news = news_db.get(team_name, "Nenhuma notícia relevante de última hora (Elenco provável titular).")
    return f"🕵️‍♂️ INVESTIGAÇÃO: {news}"


def get_coach_tactics(team_name, sport='football'):
    """Returns a tactical summary based on the coach's style."""
    tactics = {
        "Real Madrid": "⚪ Carlo Ancelotti: Estilo 'Camaleão'. Flexível (4-3-3), letal nos contra-ataques com Vini Jr.",
        "Celtics": "🍀 Joe Mazzulla: 'Mazulla-Ball'. Volume de 3pts e espaçamento (5-Out). Defesa switching.",
        "Bayern": "🔴 Vincent Kompany: Pressão sufocante (Gegenpressing). Linha alta, ataque massivo.",
        "Arsenal": "🔴 Mikel Arteta: Futebol Posicional. Triângulos, controle e bola parada mortal.",
        "Liverpool": "🔴 Arne Slot: Alta intensidade, transições rápidas e jogo vertical direto.",
        "Knicks": "🟠 Tom Thibodeau: Defesa física e rotação curta. Jogadores 40+ minutos.",
        "Warriors": "🔵 Steve Kerr: Motion Offense. Cortes e arremessos rápidos.",
        "Lakers": "🟣 JJ Redick: Foco em AD no garrafão e LeBron na criação.",
    }
    return tactics.get(team_name, "📋 Tática: Padrão balanceado.")


def get_table_analysis(home, away, sport="football"):
    """Simulates a lookup of the current League Table."""
    table_db = {
        "River Plate": {"pos": 4, "gp": 18, "gf": 32, "ga": 14},
        "Tigre": {"pos": 1, "gp": 18, "gf": 41, "ga": 10},
        "Bulls": {"pos": 11, "gp": 51, "pts_for": 112.5, "pts_ag": 116.8},
        "Nuggets": {"pos": 2, "gp": 51, "pts_for": 118.2, "pts_ag": 110.1},
        "Lakers": {"pos": 7, "gp": 50, "pts_for": 117.5, "pts_ag": 116.0},
        "Warriors": {"pos": 9, "gp": 49, "pts_for": 119.8, "pts_ag": 118.5},
        "Magic": {"pos": 4, "gp": 52, "pts_for": 111.4, "pts_ag": 108.2},
        "Jazz": {"pos": 13, "gp": 51, "pts_for": 114.1, "pts_ag": 121.5},
        "Hawks": {"pos": 10, "gp": 50, "pts_for": 121.5, "pts_ag": 123.0},
    }
    
    h_stats = table_db.get(home)
    a_stats = table_db.get(away)
    
    if not h_stats or not a_stats:
        return ""

    if sport == "basketball":
        proj_h = (h_stats['pts_for'] + a_stats['pts_ag']) / 2
        proj_a = (a_stats['pts_for'] + h_stats['pts_ag']) / 2
        total = proj_h + proj_a
        return f"📊 TABELA: {home} ({h_stats['pos']}º) ataque {h_stats['pts_for']}. {away} ({a_stats['pos']}º) cede {a_stats['pts_ag']}. Projeção: {int(total)} pts."
    else:
        h_avg_s = round(h_stats['gf'] / h_stats['gp'], 2)
        a_avg_s = round(a_stats['gf'] / a_stats['gp'], 2)
        a_avg_c = round(a_stats['ga'] / a_stats['gp'], 2)
        return f"🔍 RAIO-X: {home} (Pos:{h_stats['pos']}) marca {h_avg_s} gols/jogo. {away} (Pos:{a_stats['pos']}) média de {a_avg_s}, defesa {a_avg_c} sofridos."
