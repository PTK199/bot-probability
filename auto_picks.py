"""
AUTO PICKS ENGINE v2.0 TURBO ⚡ - Gerador Automático de Tips 🤖
Optimized with parallel I/O via turbo_fetcher.

Pipeline:
1. ESPN API → Busca PARALELA em todas as ligas (~8s vs ~80s)
2. Monte Carlo (NBA) / Poisson (Futebol) → Simula resultados
3. 365Scores Intelligence → PARALELO para todos os jogos
4. News Agent → PARALELO para todos os times
5. Ensemble + Trap Hunter + Calibration + Self-Learning
6. EV Gate → Filtra tips sem valor
7. Treble Builder → Monta combos automaticamente
"""

import requests
import datetime
import numpy as np
import math
import random
import time as _time
import sys
import os
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
import json

# Fix encoding for Windows terminals
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Import turbo parallel fetcher
try:
    from turbo_fetcher import (
        fetch_espn_schedule_parallel,
        fetch_365_intelligence_parallel,
        fetch_news_parallel,
        apply_calibration_fast,
        get_cache,
    )
    TURBO_ACTIVE = True
except ImportError:
    TURBO_ACTIVE = False
    print("[AUTO-ENGINE] ⚠️ turbo_fetcher not found, falling back to sequential")

# ══════════════════════════════════════════════
# SECTION 1: POWER RATINGS (Source: ESPN Feb 11 2026)
# ══════════════════════════════════════════════

NBA_POWER = {
    # === TIER S (Elite, 90+) ===
    "Thunder": 95, "Cavaliers": 93, "Celtics": 92,
    # === TIER A (Contenders, 85-89) ===
    "Rockets": 88, "Nuggets": 87, "Knicks": 87, "Timberwolves": 86,
    "Grizzlies": 85, "Warriors": 85,
    # === TIER B (Playoff, 78-84) ===
    "Bucks": 84, "Suns": 83, "Mavericks": 82, "Pacers": 82,
    "Magic": 81, "Clippers": 80, "Lakers": 80, "Heat": 79,
    "Kings": 79, "Sixers": 78,
    # === TIER C (Play-in / Lower, 70-77) ===
    "Hawks": 75, "Spurs": 74, "Bulls": 73, "Pistons": 72,
    "Pelicans": 71, "Raptors": 70, "Hornets": 69,
    # === TIER D (Lottery, <70) ===
    "Blazers": 66, "Jazz": 65, "Nets": 63, "Wizards": 60
}

FOOTBALL_POWER = {
    # Premier League
    "Liverpool": 93, "Arsenal": 91, "Man City": 90, "Manchester City": 90,
    "Chelsea": 82, "Tottenham": 80, "Tottenham Hotspur": 80,
    "Newcastle": 79, "Newcastle United": 79, "Man United": 75, "Manchester United": 75,
    "Aston Villa": 78, "Brighton": 77, "Brighton & Hove Albion": 77,
    "Bournemouth": 74, "AFC Bournemouth": 74, "Fulham": 73,
    "West Ham": 72, "West Ham United": 72, "Crystal Palace": 71, "Brentford": 70,
    "Wolves": 68, "Wolverhampton Wanderers": 68, "Wolverhampton": 68,
    "Nottingham Forest": 72, "Everton": 66, "Leicester": 65, "Leicester City": 65,
    "Ipswich": 60, "Ipswich Town": 60,
    "Southampton": 58, "Leeds": 70, "Leeds United": 70,
    "Burnley": 63, "Sheffield United": 60, "Luton": 58, "Luton Town": 58, "Sunderland": 68,
    # La Liga
    "Barcelona": 92, "Real Madrid": 93, "Atletico Madrid": 85,
    "Athletic Club": 80, "Villarreal": 78, "Real Sociedad": 77, "Betis": 75,
    # Serie A
    "Inter Milan": 90, "Napoli": 86, "Juventus": 84, "AC Milan": 82,
    "Atalanta": 83, "Roma": 78, "Lazio": 77, "Fiorentina": 76,
    # Bundesliga
    "Bayern Munich": 92, "Bayer Leverkusen": 88, "Borussia Dortmund": 83,
    "RB Leipzig": 80, "Stuttgart": 77, "Eintracht Frankfurt": 76,
    # Ligue 1
    "Paris Saint-Germain": 93, "PSG": 93, "Monaco": 82, "Marseille": 80, "Lille": 79,
    # Brasileirão
    "Palmeiras": 88, "Botafogo": 85, "Flamengo": 84, "Fortaleza": 82,
    "Internacional": 80, "São Paulo": 79, "Cruzeiro": 77,
    "Atlético-MG": 76, "Atletico Mineiro": 76,
    "Athletico Paranaense": 76, "Athletico-PR": 76, "CAP": 76,
    "Grêmio": 75, "Bahia": 74, "Corinthians": 78,
    "Vasco": 72, "Vasco da Gama": 72,
    "Fluminense": 71, "Vitória": 65, "Santos": 70,
    "Red Bull Bragantino": 72, "Bragantino": 72,
    "Juventude": 65, "Cuiabá": 63, "Goiás": 64,
    "Coritiba": 66, "Chapecoense": 60, "Mirassol": 62,
}

# ══════════════════════════════════════════════
# SECTION 2: ESPN API FETCHER
# ══════════════════════════════════════════════

LEAGUES = [
    {"name": "NBA", "endpoint": "basketball/nba", "sport": "basketball"},
    {"name": "Premier League", "endpoint": "soccer/eng.1", "sport": "football"},
    {"name": "La Liga", "endpoint": "soccer/esp.1", "sport": "football"},
    {"name": "Serie A", "endpoint": "soccer/ita.1", "sport": "football"},
    {"name": "Bundesliga", "endpoint": "soccer/ger.1", "sport": "football"},
    {"name": "Ligue 1", "endpoint": "soccer/fra.1", "sport": "football"},
    {"name": "Brasileirão", "endpoint": "soccer/bra.1", "sport": "football"},
    {"name": "Champions League", "endpoint": "soccer/uefa.champions", "sport": "football"},
    {"name": "Libertadores", "endpoint": "soccer/conmebol.libertadores", "sport": "football"},
    {"name": "Copa do Brasil", "endpoint": "soccer/bra.copa_do_brasil", "sport": "football"},
    {"name": "FA Cup", "endpoint": "soccer/eng.fa", "sport": "football"},
]

ESPN_BASE = "http://site.api.espn.com/apis/site/v2/sports/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_espn_schedule(target_date):
    """Busca jogos — usa TURBO (paralelo) se disponível, senão fallback sequencial."""
    if TURBO_ACTIVE:
        return fetch_espn_schedule_parallel(target_date)
    
    # --- FALLBACK SEQUENCIAL (legacy) ---
    games = []
    espn_date = target_date.replace("-", "")
    for league in LEAGUES:
        try:
            url = f"{ESPN_BASE}{league['endpoint']}/scoreboard?date={espn_date}"
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code != 200:
                continue
            data = r.json()
            for event in data.get("events", []):
                try:
                    status = event.get("status", {}).get("type", {})
                    if status.get("completed", False):
                        continue
                    comps = event.get("competitions", [])
                    if not comps:
                        continue
                    comp = comps[0]
                    competitors = comp.get("competitors", [])
                    home_c = next((c for c in competitors if c["homeAway"] == "home"), None)
                    away_c = next((c for c in competitors if c["homeAway"] == "away"), None)
                    if not home_c or not away_c:
                        continue
                    h_name = home_c["team"].get("name", home_c["team"]["displayName"])
                    a_name = away_c["team"].get("name", away_c["team"]["displayName"])
                    game_time = "TBD"
                    try:
                        raw = event.get("date", "")
                        dt = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
                        brt = dt - datetime.timedelta(hours=3)
                        game_time = brt.strftime("%H:%M")
                    except:
                        pass
                    espn_odds = {}
                    odds_data = comp.get("odds", [])
                    if odds_data:
                        espn_odds["spread"] = odds_data[0].get("details", "")
                        espn_odds["over_under"] = odds_data[0].get("overUnder", 0)
                    h_record, a_record = "", ""
                    for c in competitors:
                        recs = c.get("records", [])
                        if recs:
                            rec = recs[0].get("summary", "")
                            if c["homeAway"] == "home":
                                h_record = rec
                            else:
                                a_record = rec
                    games.append({
                        "home": h_name, "away": a_name,
                        "league": league["name"], "sport": league["sport"],
                        "time": game_time, "espn_odds": espn_odds,
                        "home_record": h_record, "away_record": a_record,
                    })
                except:
                    continue
        except Exception as e:
            print(f"[AUTO] ESPN error {league['name']}: {e}")
            continue
    print(f"[AUTO-ENGINE] ESPN retornou {len(games)} jogos para {target_date}")
    return games


# ══════════════════════════════════════════════
# SECTION 3: SIMULATION ENGINES
# ══════════════════════════════════════════════

def monte_carlo_nba(home_power, away_power, iterations=5000):
    """Monte Carlo para NBA. Retorna probs e scores médios."""
    base = 115
    h_adj = home_power - 80 + 3  # +3 home court
    a_adj = away_power - 80

    h_scores = np.random.normal(base + h_adj, 12, iterations).astype(int)
    a_scores = np.random.normal(base + a_adj, 12, iterations).astype(int)

    home_wins = int(np.sum(h_scores > a_scores))
    prob = (home_wins / iterations) * 100

    return {
        "home_prob": round(prob, 1),
        "away_prob": round(100 - prob, 1),
        "avg_home": int(np.mean(h_scores)),
        "avg_away": int(np.mean(a_scores)),
        "total_avg": int(np.mean(h_scores) + np.mean(a_scores)),
    }


def poisson_football(home_expected, away_expected):
    """Poisson para futebol. Retorna probs de H/D/A e Over 2.5."""
    def pois(lmbda, k):
        return (lmbda ** k * math.exp(-lmbda)) / math.factorial(k)

    home_win = draw = away_win = over_25 = 0.0
    for h in range(8):
        for a in range(8):
            p = pois(home_expected, h) * pois(away_expected, a)
            if h > a:
                home_win += p
            elif h == a:
                draw += p
            else:
                away_win += p
            if h + a > 2:
                over_25 += p

    btts = (1 - math.exp(-home_expected)) * (1 - math.exp(-away_expected))

    return {
        "home_prob": round(home_win * 100, 1),
        "draw_prob": round(draw * 100, 1),
        "away_prob": round(away_win * 100, 1),
        "over_25_prob": round(over_25 * 100, 1),
        "btts_prob": round(btts * 100, 1),
        "expected_total": round(home_expected + away_expected, 2),
    }


# ══════════════════════════════════════════════
# SECTION 4: TIP GENERATOR
# ══════════════════════════════════════════════

def prob_to_odd(prob_pct):
    """Converte probabilidade % em odd decimal."""
    if prob_pct <= 2:
        return 15.00
    if prob_pct >= 98:
        return 1.02
    raw = round(1 / (prob_pct / 100), 2)
    return max(1.01, min(20.0, raw))


def generate_nba_tip(game, sim):
    """Gera melhor tip para jogo NBA. Prioriza Player Props se hover valor; fallback para ML/Over."""
    home, away = game["home"], game["away"]
    h_prob, a_prob = sim["home_prob"], sim["away_prob"]
    total_avg = sim["total_avg"]
    h_rec = game.get("home_record", "")
    a_rec = game.get("away_record", "")
    ou_line = game.get("espn_odds", {}).get("over_under", 0)

    odd_h = prob_to_odd(h_prob)
    odd_a = prob_to_odd(a_prob)
    
    # 1. TENTATIVA DE PLAYER PROP (Prioridade Máxima para NBA - Meta 80% Green)
    # Procurar nas estruturas do 365Scores se temos projetores de Props explodindo.
    intel_data = game.get("_team_intel", {})
    home_intel = intel_data.get("home", {})
    away_intel = intel_data.get("away", {})
    
    # Acessar a engine (já foi chamada no turbo_fetcher, então vamos ler os 'top_performers' injetados)
    from ai_engine import simulate_player_props
    
    best_prop = None
    best_prop_val = 0
    
    for team_intel, is_home in [(home_intel, True), (away_intel, False)]:
        team_name = home if is_home else away
        starters = team_intel.get("starters", [])
        missing = team_intel.get("missing", [])
        # Extrair odds reais se disponíveis (The-Odds-API)
        live_odds = game.get("_live_odds", {})

        # Simular Props para todos os titulares usando a nova Engine
        for player in starters:
            prop_sim = simulate_player_props(player, missing, opponent_defense_rating=1.0) # Def rating placeholder
            if prop_sim:
                pts = prop_sim["projected_pts"]
                avg_pts = player.get("avg_pts", 0)
                
                is_value = prop_sim.get("is_value", False)
                p_name = player.get("name", "")
                
                # Check for REAL bookmaker lines
                real_line_data = None
                p_aliases = [p_name, p_name.split(" ")[-1], player.get("short_name", "")]
                
                for alias in p_aliases:
                    if alias and alias in live_odds:
                        # Tenta pegar linha do pinnacle ou bet365, ou a primeira que vier
                        lines_dict = live_odds[alias].get("lines", {})
                        if "pinnacle" in lines_dict:
                             real_line_data = lines_dict["pinnacle"].get("Over")
                        elif "bet365" in lines_dict:
                             real_line_data = lines_dict["bet365"].get("Over")
                        elif lines_dict:
                             first_bm = list(lines_dict.keys())[0]
                             real_line_data = lines_dict[first_bm].get("Over")
                        break

                # Estimar a linha padrão se não houver linha real
                proj_line = real_line_data["val"] if real_line_data else round(max(14.5, avg_pts - 1.5) * 2) / 2
                
                # Assign a common baseline odd (1.80 to 1.90 is typical for an Over line)
                prop_odd = real_line_data["odd"] if real_line_data else 1.85
                
                # O Score de valor agora respeita a linha REAL (ou estimada AI EV)
                diff = pts - proj_line
                prop_score = diff * 5 + avg_pts  # Combina potencial de explosao com média base
                
                if prop_score > best_prop_val and pts > 15:
                    best_prop_val = prop_score
                    if pts >= proj_line + 1.0: # Softened threshold to allow more +EV edge
                        reason = prop_sim["reasons"][0] if prop_sim["reasons"] else f"Média de {avg_pts:.1f} PTS."
                        
                        # Penalidade de probabilidade se odds forem muito justas (< 1.60)
                        prob_penalty = 0 if prop_odd >= 1.70 else 5
                        prob_calc = min(92, 70 + int(diff * 3)) - prob_penalty
                        
                        best_prop = {
                            "market": "Mercado de Jogadores",
                            "selection": f"{p_name} Over {proj_line:.1f} Pontos",
                            "prob": prob_calc,
                            "odd": prop_odd, 
                            "reason": f"🏀 [PROP SNIPER] {team_name}: {reason} Projeção: {pts:.1f}",
                            "badge": "🎯 PROP SNIPER" if not is_value else "🔥 ALPHA DOG",
                        }
                        # DEBUG
                        print(f"[DEBUG PROPS] Found potential: {p_name} Pts: {pts:.1f} (Line: {proj_line:.1f}) -> Score: {prop_score:.1f}, Prob: {prob_calc}% (Odd: {prop_odd})")

    # Se achou uma Tip de Prop com alta probabilidade, ela reduz a chance do ML aparecer
    if best_prop:
         print(f"[DEBUG PROPS] GAME {home} vs {away} BEST PROP: {best_prop['selection']} with Prob: {best_prop['prob']}%")
         # NBA player props are highly volatile but high value. Lowering threshold to 65% to pass EV models.
         if best_prop["prob"] >= 65:
             return best_prop, True, odd_h, 0, odd_a


    # --- FALLBACK: ML / MÉTODOS ANTIGOS ---
    # Strong favorite ML
    if h_prob >= 72:
        tip = {
            "market": "Vencedor (ML)", "selection": f"{home} Vence",
            "prob": int(h_prob), "odd": odd_h,
            "reason": f"🏀 [MONTE CARLO 5K]: {home} ({h_rec}) com {h_prob}% de vitória. {away} ({a_rec}) inferior em power rating.",
            "badge": "💰 BANKER" if h_prob >= 82 else "🎯 SNIPER",
        }
    elif a_prob >= 72:
        tip = {
            "market": "Vencedor (ML)", "selection": f"{away} Vence",
            "prob": int(a_prob), "odd": odd_a,
            "reason": f"🏀 [MONTE CARLO 5K]: {away} ({a_rec}) com {a_prob}% mesmo fora de casa. {home} ({h_rec}) muito inferior.",
            "badge": "💰 BANKER" if a_prob >= 82 else "🎯 SNIPER",
        }
    elif ou_line and total_avg > ou_line + 2:
        edge = total_avg - ou_line
        over_prob = min(82, 55 + int(edge * 3))
        tip = {
            "market": "Total de Pontos",
            "selection": f"Over {ou_line} Pontos",
            "prob": over_prob, "odd": 1.90,
            "reason": f"🏀 [PACE]: Média simulada {total_avg} pts > Linha {ou_line}. Edge {edge:.1f} pts.",
            "badge": "🚀 OVER",
        }
    elif h_prob > a_prob:
        tip = {
            "market": "Vencedor (ML)", "selection": f"{home} Vence",
            "prob": int(h_prob), "odd": odd_h,
            "reason": f"🏀 [MONTE CARLO 5K]: {home} ({h_rec}) leve favorito com {h_prob}%.",
            "badge": "🎯 SNIPER",
        }
    else:
        tip = {
            "market": "Vencedor (ML)", "selection": f"{away} Vence",
            "prob": int(a_prob), "odd": odd_a,
            "reason": f"🏀 [MONTE CARLO 5K]: {away} ({a_rec}) favorito com {a_prob}%.",
            "badge": "🎯 SNIPER",
        }

    is_sniper = tip["prob"] >= 70
    return tip, is_sniper, odd_h, 0, odd_a



def generate_football_tip(game, sim):
    """
    Gera melhor tip para jogo de futebol baseado em Poisson.
    CORRIGIDO: Agora considera o favorito REAL (não sempre o mandante).
    Compara power ratings e probs para escolher o melhor pick.
    """
    home, away = game["home"], game["away"]
    hp = sim["home_prob"]
    dp = sim["draw_prob"]
    ap = sim["away_prob"]
    o25 = sim["over_25_prob"]

    odd_h = prob_to_odd(hp)
    odd_d = prob_to_odd(dp)
    odd_a = prob_to_odd(ap)

    # Double Chance for BOTH sides
    dc_home = hp + dp   # Home or Draw
    dc_away = ap + dp   # Away or Draw

    # Get power ratings to understand who the REAL favorite is
    h_pow = FOOTBALL_POWER.get(home, 70)
    a_pow = FOOTBALL_POWER.get(away, 70)
    power_gap = a_pow - h_pow  # Positive = away is stronger

    # ─── TIER 1: Clear Home Favorite (home prob >= 60%) ───
    if hp >= 60:
        tip = {
            "market": "Vencedor", "selection": f"{home} Vence",
            "prob": int(hp), "odd": odd_h,
            "reason": f"⚽ [POISSON]: {home} ({h_pow}pw) com {hp:.0f}% em casa. Domínio estatístico.",
            "badge": "💰 BANKER" if hp >= 72 else "🎯 SNIPER",
        }

    # ─── TIER 2: Clear Away Favorite (away prob >= 45% AND stronger power) ───
    elif ap >= 45 and power_gap >= 10:
        tip = {
            "market": "Vencedor", "selection": f"{away} Vence",
            "prob": int(ap), "odd": odd_a,
            "reason": f"⚽ [POISSON]: {away} ({a_pow}pw) favorito fora com {ap:.0f}%. Qualidade superior (gap +{power_gap}pw).",
            "badge": "🎯 SNIPER",
        }

    # ─── TIER 3: Strong Away ML (>= 55% prob regardless of power) ───
    elif ap >= 55:
        tip = {
            "market": "Vencedor", "selection": f"{away} Vence",
            "prob": int(ap), "odd": odd_a,
            "reason": f"⚽ [POISSON]: {away} ({a_pow}pw) favorito com {ap:.0f}% mesmo fora de casa.",
            "badge": "🎯 SNIPER",
        }

    # ─── TIER 4: DC on the STRONGER team ───
    elif dc_away >= 75 and power_gap >= 8:
        # Away team is much stronger → DC Away is safer
        dc_odd = prob_to_odd(dc_away)
        tip = {
            "market": "Dupla Chance", "selection": f"{away} ou Empate",
            "prob": int(dc_away), "odd": dc_odd,
            "reason": f"⚽ [POISSON]: {away} ({a_pow}pw) é o favorito. DC {away} ({dc_away:.0f}%) é o mais seguro.",
            "badge": "🛡️ SAFE",
        }

    elif dc_home >= 75 and power_gap <= 5:
        # Home team is equal or stronger → DC Home is safer
        dc_odd = prob_to_odd(dc_home)
        tip = {
            "market": "Dupla Chance", "selection": f"{home} ou Empate",
            "prob": int(dc_home), "odd": dc_odd,
            "reason": f"⚽ [POISSON]: {home} ({h_pow}pw) em casa. DC {home} ({dc_home:.0f}%) seguro.",
            "badge": "🛡️ SAFE",
        }

    # ─── TIER 5: Over 2.5 ───
    elif o25 >= 65:
        tip = {
            "market": "Gols", "selection": "Over 2.5 Gols",
            "prob": int(o25), "odd": prob_to_odd(o25),
            "reason": f"⚽ [POISSON]: {o25:.0f}% para Over 2.5. Total esperado: {sim['expected_total']:.1f} gols.",
            "badge": "🚀 OVER",
        }

    # ─── TIER 6: Fallback — DC on the team with HIGHER probability ───
    else:
        if dc_away > dc_home and power_gap >= 5:
            # Away is stronger — pick DC Away
            dc_odd = prob_to_odd(dc_away)
            tip = {
                "market": "Dupla Chance", "selection": f"{away} ou Empate",
                "prob": int(dc_away), "odd": dc_odd,
                "reason": f"⚽ [POISSON]: {away} ({a_pow}pw) favorito. DC {away} ({dc_away:.0f}%) mais seguro.",
                "badge": "🛡️ SAFE",
            }
        else:
            # Home or balanced — pick DC Home (home advantage applies)
            dc_odd = prob_to_odd(dc_home)
            tip = {
                "market": "Dupla Chance", "selection": f"{home} ou Empate",
                "prob": int(dc_home), "odd": dc_odd,
                "reason": f"⚽ [POISSON]: Jogo equilibrado. DC {home} ({dc_home:.0f}%) com fator casa.",
                "badge": "🛡️ SAFE",
            }

    is_sniper = tip["prob"] >= 70
    return tip, is_sniper, odd_h, odd_d, odd_a


# ══════════════════════════════════════════════
# SECTION 5: HELPERS (logos, bookmaker odds)
# ══════════════════════════════════════════════

def get_logo(team_name, sport):
    """Retorna URL do logo. Tenta data_fetcher, fallback para ui-avatars."""
    try:
        from data_fetcher import TEAM_LOGOS
        logo = TEAM_LOGOS.get(team_name)
        if logo:
            return logo
    except:
        pass
    safe = team_name.replace(" ", "+")
    return f"https://ui-avatars.com/api/?name={safe}&size=64&background=1a1a2e&color=a855f7&bold=true"


def gen_bookmaker_odds(base_odd):
    """Gera odds comparativas simuladas de casas de apostas."""
    houses = ["Bet365", "Betano", "1xBet", "Sportingbet", "Pinnacle"]
    result = []
    for h in houses:
        variation = round(random.uniform(-0.08, 0.12), 2)
        result.append({"house": h, "odd": round(base_odd + variation, 2)})
    return sorted(result, key=lambda x: x["odd"], reverse=True)


# ══════════════════════════════════════════════
# SECTION 6: TREBLE BUILDER v3.0 — FORTRESS ENGINE 🏰
# Target: 90%+ green rate through intelligent selection
# ══════════════════════════════════════════════

# League reliability tiers (based on historical predictability)
LEAGUE_RELIABILITY = {
    # TIER S: Most predictable, home advantage is real
    "NBA": 0.95, "Premier League": 0.90, "La Liga": 0.88,
    "Serie A": 0.87, "Bundesliga": 0.90, "Ligue 1": 0.85,
    # TIER A: Good data, moderately predictable
    "Brasileirão": 0.82, "Champions League": 0.78,
    "Eredivisie": 0.83, "Liga Portugal": 0.80,
    # TIER B: Less predictable, higher variance
    "Libertadores": 0.70, "Copa do Brasil": 0.72,
    "Liga MX": 0.75, "Sudamericana": 0.65,
    "FA Cup": 0.68, "Copa del Rey": 0.70,
}

# Market safety hierarchy (DC > ML for combos)
MARKET_SAFETY = {
    "dupla chance": 1.0,    # Safest — covers 2 of 3 outcomes
    "vencedor": 0.85,       # ML — riskier but higher odds
    "total de pontos": 0.80, # Over/Under — volatile
    "gols": 0.75,           # Goals market
}


def _calc_safety_score(game):
    """
    Calculate a composite safety score (0-100) for treble inclusion.
    Higher = safer to include in a combo.
    """
    tip = game["best_tip"]
    prob = tip.get("prob", 50)
    odd = float(tip.get("odd", 1.5))
    league = game.get("league", "Unknown")
    selection = tip.get("selection", "").lower()
    reason = tip.get("reason", "").lower()
    badge = tip.get("badge", "")
    
    # BASE: Raw probability (0-100)
    score = prob
    
    # BOOST: League reliability (+0 to +5)
    league_mult = LEAGUE_RELIABILITY.get(league, 0.70)
    score *= league_mult  # Scale by reliability
    
    # BOOST: Market safety
    market_mult = 1.0
    for mkt, mult in MARKET_SAFETY.items():
        if mkt in tip.get("market", "").lower():
            market_mult = mult
            break
    score *= market_mult
    
    # PENALTY: Trap detected (-15)
    if "trap" in reason:
        score -= 15
    
    # PENALTY: EV Gate warning (-10)
    if "ev gate" in badge.lower():
        score -= 10
    
    # PENALTY: Low odd (juice bets, likely inflated prob)
    if odd < 1.15:
        score -= 12  # Too juicy = likely trap
    elif odd < 1.25:
        score -= 5
    
    # PENALTY: Very high odd (risky for combos)
    if odd > 2.0:
        score -= 8
    elif odd > 1.8:
        score -= 3
    
    # BOOST: Dupla Chance market (covers 2 outcomes!)
    if "ou empate" in selection or "dupla chance" in tip.get("market", "").lower():
        score += 8
    
    # BOOST: BANKER badge
    if "banker" in badge.lower():
        score += 10
    
    # BOOST: SAFE badge
    if "safe" in badge.lower():
        score += 5
    
    # BOOST: SNIPER badge
    if "sniper" in badge.lower():
        score += 3
    
    # PENALTY: Unknown league
    if league not in LEAGUE_RELIABILITY:
        score -= 8
    
    return max(0, min(100, score))


def _calc_combo_probability(picks):
    """
    Calculate REAL combined probability for a combo.
    Uses independence discount (games aren't perfectly independent).
    """
    if not picks:
        return 0
    
    probs = [p["best_tip"]["prob"] / 100 for p in picks]
    
    # Raw multiplication (assumes independence)
    raw_combined = 1.0
    for p in probs:
        raw_combined *= p
    
    # Independence discount: 2-leg = 0.97, 3-leg = 0.93, 4-leg = 0.88
    # (Accounts for hidden correlations: weather, referee school, etc.)
    discount = {2: 0.97, 3: 0.93, 4: 0.88}.get(len(picks), 0.85)
    
    adjusted = raw_combined * discount
    return int(adjusted * 100)


def _diversification_check(picks):
    """
    Ensure picks are diversified (no more than 2 from same league).
    Returns True if the combo passes diversification rules.
    """
    league_count = {}
    for p in picks:
        league = p.get("league", "Unknown")
        league_count[league] = league_count.get(league, 0) + 1
    
    # No league should have more than 2 picks in a combo
    return all(count <= 2 for count in league_count.values())


def build_trebles(processed_games):
    """
    FORTRESS TREBLE BUILDER v3.0 🏰
    
    7-Layer intelligence for 90%+ green rate:
    1. FORTRESS filter: prob >= 68, no traps, no EV GATE
    2. League reliability tiers
    3. Correlation-aware combined probability
    4. Diversification (no same-league stacking)
    5. Market quality hierarchy (DC > ML > Over)
    6. Smart safety scoring
    7. Three treble tiers: BUNKER, FORTRESS, VALUE
    """
    trebles = []
    
    # ═══════════════════════════════════════
    # STAGE 1: FORTRESS FILTER (strict selection)
    # Only the SAFEST picks enter the treble pool
    # ═══════════════════════════════════════
    
    fortress_pool = []
    for g in processed_games:
        tip = g["best_tip"]
        prob = tip.get("prob", 0)
        badge = tip.get("badge", "")
        reason = tip.get("reason", "").lower()
        odd = float(tip.get("odd", 1.5))
        
        # HARD FILTERS - If any fail, pick is excluded from combos
        if prob < 62:
            continue  # Too low confidence
        if "trap" in reason and odd < 1.20:
            continue  # Trap + juice = dangerous
        if odd < 1.08:
            continue  # Bad risk/reward ratio for combos
        if odd > 2.50:
            continue  # Too volatile for combo inclusion
        
        # Calculate safety score
        safety = _calc_safety_score(g)
        g["_safety_score"] = safety
        fortress_pool.append(g)
    
    # Sort by safety score (highest = safest)
    fortress_pool.sort(key=lambda x: x.get("_safety_score", 0), reverse=True)
    
    print(f"[TREBLE-ENGINE] 🏰 Fortress pool: {len(fortress_pool)} picks (from {len(processed_games)} total)")
    for g in fortress_pool[:8]:
        print(f"  → {g['home_team']} vs {g['away_team']}: {g['best_tip']['selection']} "
              f"(prob:{g['best_tip']['prob']}%, safety:{g.get('_safety_score', 0):.0f})")
    
    # Categorize picks
    ml_keywords = ["vence", "ml", "ou empate", "dupla chance", "vitória", "win"]
    over_keywords = ["over", "acima", "mais de"]
    
    dc_picks = [g for g in fortress_pool if "ou empate" in g["best_tip"]["selection"].lower()]
    ml_picks = [g for g in fortress_pool if any(kw in g["best_tip"]["selection"].lower() for kw in ["vence", "vitória", "win"])]
    over_picks = [g for g in fortress_pool if any(kw in g["best_tip"]["selection"].lower() for kw in over_keywords)]
    safe_picks = dc_picks + ml_picks  # DC first (safer), then ML
    
    # Remove duplicates while preserving order
    seen = set()
    safe_unique = []
    for p in safe_picks:
        key = f"{p['home_team']}-{p['away_team']}"
        if key not in seen:
            seen.add(key)
            safe_unique.append(p)
    safe_picks = safe_unique
    
    # ═══════════════════════════════════════
    # TREBLE 1: 🛡️ BUNKER (2-leg, ultra-safe)
    # Target: 85-95% combined probability
    # Only DC picks or very high ML picks
    # ═══════════════════════════════════════
    
    bunker_candidates = [g for g in fortress_pool if g.get("_safety_score", 0) >= 55]
    
    if len(bunker_candidates) >= 2:
        # Pick the 2 safest, ensuring diversification
        picks = []
        used_leagues = set()
        for g in bunker_candidates:
            if len(picks) >= 2:
                break
            league = g.get("league", "")
            # Allow max 1 per league in BUNKER
            if league in used_leagues and len(bunker_candidates) > 3:
                continue
            picks.append(g)
            used_leagues.add(league)
        
        if len(picks) >= 2:
            total_odd = 1
            sels = []
            for p in picks:
                total_odd *= float(p["best_tip"]["odd"])
                sels.append({
                    "match": f"{p['away_team']} @ {p['home_team']}", 
                    "pick": f"{p['best_tip']['selection']} (@{p['best_tip']['odd']})",
                    "league": p.get("league", ""),
                    "prob": p["best_tip"]["prob"]
                })
            
            combo_prob = _calc_combo_probability(picks)
            
            trebles.append({
                "name": "🛡️ BUNKER BLINDADO",
                "total_odd": f"{total_odd:.2f}",
                "probability": f"{combo_prob}%",
                "selections": sels,
                "copy_text": (
                    f"🛡️ BUNKER BLINDADO (Safety: {combo_prob}%)\n" + 
                    "\n".join([f"• {s['pick']} [{s['league']}]" for s in sels]) + 
                    f"\n💰 Odd Total: {total_odd:.2f}"
                )
            })
            print(f"[TREBLE-ENGINE] 🛡️ BUNKER: {combo_prob}% @ {total_odd:.2f}")
    
    # ═══════════════════════════════════════
    # TREBLE 2: 🏰 FORTRESS (3-leg, balanced)
    # Target: 65-80% combined probability
    # Mix of DC + ML for better odds
    # ═══════════════════════════════════════
    
    fortress_candidates = [g for g in fortress_pool if g.get("_safety_score", 0) >= 48]
    
    if len(fortress_candidates) >= 3:
        picks = []
        used_leagues = set()
        for g in fortress_candidates:
            if len(picks) >= 3:
                break
            league = g.get("league", "")
            if league in used_leagues and len(fortress_candidates) > 5:
                continue
            picks.append(g)
            used_leagues.add(league)
        
        if len(picks) >= 3 and _diversification_check(picks):
            total_odd = 1
            sels = []
            for p in picks:
                total_odd *= float(p["best_tip"]["odd"])
                sels.append({
                    "match": f"{p['away_team']} @ {p['home_team']}", 
                    "pick": f"{p['best_tip']['selection']} (@{p['best_tip']['odd']})",
                    "league": p.get("league", ""),
                    "prob": p["best_tip"]["prob"]
                })
            
            combo_prob = _calc_combo_probability(picks)
            
            trebles.append({
                "name": "🏰 FORTRESS (3-LEGS)",
                "total_odd": f"{total_odd:.2f}",
                "probability": f"{combo_prob}%",
                "selections": sels,
                "copy_text": (
                    f"🏰 FORTRESS (Safety: {combo_prob}%)\n" + 
                    "\n".join([f"• {s['pick']} [{s['league']}]" for s in sels]) + 
                    f"\n💰 Odd Total: {total_odd:.2f}"
                )
            })
            print(f"[TREBLE-ENGINE] 🏰 FORTRESS: {combo_prob}% @ {total_odd:.2f}")
    
    # ═══════════════════════════════════════
    # TREBLE 3: 🔥 VALUE HUNTER (3-leg, higher risk/reward)
    # Uses a broader pool including Over picks
    # ═══════════════════════════════════════
    
    value_candidates = [g for g in fortress_pool if g.get("_safety_score", 0) >= 40]
    
    if safe_picks and over_picks and len(value_candidates) >= 3:
        # 2 safest ML/DC + 1 best Over
        picks = []
        used_leagues = set()
        
        # First: add 2 safest ML/DC
        for g in safe_picks:
            if len(picks) >= 2:
                break
            league = g.get("league", "")
            if league in used_leagues:
                continue
            picks.append(g)
            used_leagues.add(league)
        
        # Then: add 1 best Over (different league)
        for g in over_picks:
            if len(picks) >= 3:
                break
            league = g.get("league", "")
            if league in used_leagues:
                continue
            picks.append(g)
            used_leagues.add(league)
        
        if len(picks) >= 3 and _diversification_check(picks):
            total_odd = 1
            sels = []
            for p in picks:
                total_odd *= float(p["best_tip"]["odd"])
                sels.append({
                    "match": f"{p['away_team']} @ {p['home_team']}", 
                    "pick": f"{p['best_tip']['selection']} (@{p['best_tip']['odd']})",
                    "league": p.get("league", ""),
                    "prob": p["best_tip"]["prob"]
                })
            
            combo_prob = _calc_combo_probability(picks)
            
            trebles.append({
                "name": "🔥 VALUE HUNTER",
                "total_odd": f"{total_odd:.2f}",
                "probability": f"{combo_prob}%",
                "selections": sels,
                "copy_text": (
                    f"🔥 VALUE HUNTER (Prob: {combo_prob}%)\n" + 
                    "\n".join([f"• {s['pick']} [{s['league']}]" for s in sels]) + 
                    f"\n💰 Odd Total: {total_odd:.2f}"
                )
            })
            print(f"[TREBLE-ENGINE] 🔥 VALUE HUNTER: {combo_prob}% @ {total_odd:.2f}")
    
    # ═══════════════════════════════════════
    # TREBLE 4: 💎 DIAMANTE (4-leg, high reward if pool is deep)
    # Only built if we have 6+ fortress-quality picks
    # ═══════════════════════════════════════
    
    if len(fortress_candidates) >= 6:
        picks = []
        used_leagues = set()
        for g in fortress_candidates:
            if len(picks) >= 4:
                break
            league = g.get("league", "")
            if league in used_leagues:
                continue
            picks.append(g)
            used_leagues.add(league)
        
        if len(picks) >= 4 and _diversification_check(picks):
            total_odd = 1
            sels = []
            for p in picks:
                total_odd *= float(p["best_tip"]["odd"])
                sels.append({
                    "match": f"{p['away_team']} @ {p['home_team']}", 
                    "pick": f"{p['best_tip']['selection']} (@{p['best_tip']['odd']})",
                    "league": p.get("league", ""),
                    "prob": p["best_tip"]["prob"]
                })
            
            combo_prob = _calc_combo_probability(picks)
            
            trebles.append({
                "name": "💎 DIAMANTE 4-LEGS",
                "total_odd": f"{total_odd:.2f}",
                "probability": f"{combo_prob}%",
                "selections": sels,
                "copy_text": (
                    f"💎 DIAMANTE (Prob: {combo_prob}%)\n" + 
                    "\n".join([f"• {s['pick']} [{s['league']}]" for s in sels]) + 
                    f"\n💰 Odd Total: {total_odd:.2f}"
                )
            })
            print(f"[TREBLE-ENGINE] 💎 DIAMANTE: {combo_prob}% @ {total_odd:.2f}")
    
    if not trebles:
        print("[TREBLE-ENGINE] ⚠️ No trebles built — insufficient fortress-quality picks")
    
    return trebles


# ══════════════════════════════════════════════
# SECTION 7: MAIN ENTRY POINT
# ══════════════════════════════════════════════

# ═══════════════════════════════════════════════════
# THROTTLED LEARNING (max once per 10 min)
# ═══════════════════════════════════════════════════
_last_study_time = 0

def get_auto_games(target_date):
    """
    Entrada principal do Auto Engine v2.0 TURBO ⚡
    Retorna {"games": [...], "trebles": [...]}.
    
    OTIMIZAÇÕES v2.0:
    - ESPN fetch paralelo (10 ligas simultâneas)
    - 365Scores intelligence paralelo (todos jogos simultâneos)
    - News Agent paralelo (todos times simultâneos)
    - study_results() com throttle (máx 1x/10min)
    - Calibração cacheada
    """
    global _last_study_time
    t_total_start = _time.time()
    print(f"[AUTO-ENGINE] 🤖⚡ Gerando picks TURBO para {target_date}...")

    # ══════════════════════════════════════════════
    # IMPORT ALL SPECIALIST MODULES (THE FULL FUNNEL)
    # ══════════════════════════════════════════════
    try:
        from ai_engine import (
            ensemble_prediction_model,
            trap_hunter_funnel,
            calculate_expected_value,
            protocol_unstoppable_90,
            funnel_laundromat,
            coach_tactical_matrix,
        )
        FUNNEL_ACTIVE = True
        print("[AUTO-ENGINE] ✅ AI Engine CONNECTED (+ GOD MODE + LAUNDROMAT + COACH DNA)")
    except Exception as e:
        print(f"[AUTO-ENGINE] ⚠️ AI Engine not available: {e}")
        FUNNEL_ACTIVE = False

    try:
        from specialized_modules import tracker_sharp_money
        SHARP_MONEY_ACTIVE = True
        print("[AUTO-ENGINE] ✅ Sharp Money Tracker CONNECTED")
    except Exception as e:
        SHARP_MONEY_ACTIVE = False
        print(f"[AUTO-ENGINE] ⚠️ Sharp Money not available: {e}")

    try:
        from knowledge_base import SPORTS_KNOWLEDGE
        KB_ACTIVE = True
        print(f"[AUTO-ENGINE] ✅ Knowledge Base CONNECTED ({len(SPORTS_KNOWLEDGE)} teams)")
    except Exception as e:
        SPORTS_KNOWLEDGE = {}
        KB_ACTIVE = False

    CALIBRATION_ACTIVE = TURBO_ACTIVE  # Use turbo cached version

    try:
        from scores365 import get_lineup_intelligence
        SCORES365_ACTIVE = True
        print("[AUTO-ENGINE] ✅ 365Scores Intelligence CONNECTED")
    except Exception as e:
        SCORES365_ACTIVE = False
        get_lineup_intelligence = None
        print(f"[AUTO-ENGINE] ⚠️ 365Scores not available: {e}")

    try:
        from self_learning import apply_learning_correction, study_results, get_learning_summary, get_active_thresholds
        LEARNING_ACTIVE = True
        # THROTTLED: Only study once per 10 minutes
        now = _time.time()
        if (now - _last_study_time) > 600:
            study_results()
            _last_study_time = now
            summary = get_learning_summary()
            learned_thresholds = get_active_thresholds()
            print(f"[AUTO-ENGINE] ✅ Self-Learning: {summary.get('corrections_active', 0)} correções | Sniper: {learned_thresholds.get('sniper')}%")
        else:
            learned_thresholds = get_active_thresholds()
            print(f"[AUTO-ENGINE] ✅ Self-Learning CACHED (Sniper: {learned_thresholds.get('sniper')}%)")
            
        # Global learning state for downstream filtering
        from self_learning import get_learning_state
        GLOBAL_LEARNING = get_learning_state()
    except Exception as e:
        LEARNING_ACTIVE = False
        GLOBAL_LEARNING = {}
        print(f"[AUTO-ENGINE] ⚠️ Self-Learning not available: {e}")

    # ══════════════════════════════════════════════
    # STAGE 0: PARALLEL DATA FETCH (All I/O at once)
    # ══════════════════════════════════════════════
    t0 = _time.time()
    
    # 1. Busca jogos na ESPN (PARALELO)
    cache_file = os.path.join(CACHE_DIR, f"today_{target_date}.json")
    # Forçando o reprocessamento temporário ignorando o cache para rodar os props da NBA
    # if os.path.exists(cache_file): 
    #    print(f"[AUTO-ENGINE] ☑️ Picks for {target_date} already generated.")
    #    return {"games": [], "trebles": []}
    
    
    raw_games = fetch_espn_schedule(target_date)
    if not raw_games:
        print("[AUTO-ENGINE] ⚠️ Nenhum jogo encontrado na ESPN")
        return {"games": [], "trebles": []}
    
    t_espn = _time.time() - t0
    print(f"[AUTO-ENGINE] ⚡ ESPN: {len(raw_games)} games in {t_espn:.1f}s")

    # 2. Pre-fetch 365Scores intelligence for ALL games in PARALLEL
    intel_map = {}
    if SCORES365_ACTIVE and TURBO_ACTIVE and get_lineup_intelligence:
        try:
            intel_map = fetch_365_intelligence_parallel(raw_games, target_date, get_lineup_intelligence)
        except Exception as e:
            print(f"[AUTO-ENGINE] ⚠️ Parallel 365S failed: {e}")
    
    print(f"[AUTO-ENGINE] 📡 {len(raw_games)} jogos. Processando FUNIL TURBO...")

    # 2. Gera tips para cada jogo — FULL FUNNEL PIPELINE
    processed = []
    for game in raw_games:
        try:
            sport = game["sport"]
            home = game["home"]
            away = game["away"]
            league = game["league"]
            funnel_notes = []

            # ─── STAGE 0.5: INJECT LIVE ODDS & 365SCORES LINEUPS ───
            # 1. Inject Live Bookmaker Odds
            try:
                from odds_api import get_nba_player_props
                if "_live_odds" not in game:
                    # Fetch odds once per run and cache in the first game object (or pass globally)
                    game["_live_odds"] = get_nba_player_props(target_date, "player_points")
            except Exception as e:
                print(f"[AUTO-ENGINE] ⚠️ Stage 0.5 OddsAPI error: {e}")
                
            # 2. Inject 365Scores Lineups
            if SCORES365_ACTIVE:
                try:
                    intel = intel_map.get(home)
                    # For NBA, always fetch lineups explicitly because it dictates our Player Props algorithm
                    needs_fetch = not intel and (not TURBO_ACTIVE or sport == 'basketball')
                    if needs_fetch and get_lineup_intelligence:
                        sport_365 = "basketball" if sport == "basketball" else "football"
                        intel = get_lineup_intelligence(home, away, target_date, sport=sport_365)
                        if intel:
                            intel_map[home] = intel # Cache it so STAGE 3.5 doesn't re-fetch
                            
                    if intel:
                        game["_team_intel"] = {
                            "home": {
                                "starters": intel.get("home_starters", []),
                                "missing": intel.get("home_missing", [])
                            },
                            "away": {
                                "starters": intel.get("away_starters", []),
                                "missing": intel.get("away_missing", [])
                            }
                        }
                        if sport == "basketball":
                            h_st = len(game["_team_intel"]["home"]["starters"])
                            a_st = len(game["_team_intel"]["away"]["starters"])
                            print(f"[DEBUG PIPELINE] {home} (Starters: {h_st}) vs {away} (Starters: {a_st}) injected")
                except Exception as e:
                    print(f"[AUTO-ENGINE] ⚠️ Stage 0.5 Lineups error for {home}: {e}")

            # ─── STAGE 1: RAW SIMULATION (Poisson / Monte Carlo) ───
            if sport == "basketball":
                h_pow = NBA_POWER.get(home, 75)
                a_pow = NBA_POWER.get(away, 75)
                sim = monte_carlo_nba(h_pow, a_pow)
                tip, is_sniper, oh, od, oa = generate_nba_tip(game, sim)
            else:
                h_pow = FOOTBALL_POWER.get(home, 70)
                a_pow = FOOTBALL_POWER.get(away, 70)
                h_exp = 1.20 * (h_pow / 75)
                a_exp = 1.15 * (a_pow / 75)
                sim = poisson_football(h_exp, a_exp)
                tip, is_sniper, oh, od, oa = generate_football_tip(game, sim)

            raw_prob = tip.get("prob", 50)
            tip_odd = float(tip.get("odd", 1.5))

            # ─── STAGE 1.5: LEAGUE VOLATILITY PENALTY ───
            # Cups and continental competitions are MUCH less predictable
            VOLATILE_LEAGUES = {
                "Champions League": -5,
                "Libertadores": -7,
                "Copa do Brasil": -5,
                "FA Cup": -6,
                "Copa del Rey": -5,
                "Sudamericana": -8,
                "Europa League": -4,
                "Conference League": -3,
            }
            vol_adj = VOLATILE_LEAGUES.get(league, 0)
            if vol_adj != 0:
                tip["prob"] = max(30, tip["prob"] + vol_adj)
                funnel_notes.append(f"🧠 Liga {league}: {vol_adj}%")

            # ─── STAGE 2: ENSEMBLE VOTING (3 models vote) ───
            if FUNNEL_ACTIVE:
                try:
                    basic_probs = {
                        "home_win": sim.get("home_prob", 40),
                        "draw": sim.get("draw_prob", 25),
                        "away_win": sim.get("away_prob", 35),
                    }
                    ensemble = ensemble_prediction_model(basic_probs)

                    # Use ensemble-corrected probability for the selected outcome
                    sel_lower = tip.get("selection", "").lower()
                    if "vence" in sel_lower or "ml" in sel_lower:
                        # Check if it's home or away pick
                        if home.lower() in sel_lower or any(p in sel_lower for p in home.lower().split()):
                            ensemble_prob = ensemble.get("home_win", raw_prob)
                        else:
                            ensemble_prob = ensemble.get("away_win", raw_prob)
                    elif "ou empate" in sel_lower or "dupla chance" in tip.get("market", "").lower():
                        if home.lower() in sel_lower or any(p in sel_lower for p in home.lower().split()):
                            ensemble_prob = ensemble.get("home_win", 0) + ensemble.get("draw", 0)
                        else:
                            ensemble_prob = ensemble.get("away_win", 0) + ensemble.get("draw", 0)
                    else:
                        ensemble_prob = raw_prob  # Over/Under stays raw

                    # Blend: 60% raw Poisson + 40% ensemble
                    blended_prob = int(raw_prob * 0.6 + ensemble_prob * 0.4)
                    if abs(blended_prob - raw_prob) > 3:
                        funnel_notes.append(f"🗳️ ENSEMBLE: {raw_prob}% → {blended_prob}%")
                    tip["prob"] = blended_prob
                except Exception as e:
                    funnel_notes.append(f"⚠️ Ensemble bypass: {e}")

            # ─── STAGE 3: KNOWLEDGE BASE CONTEXT ───
            if KB_ACTIVE:
                try:
                    # Look up team profiles for tactical context
                    h_key = home.lower().split()[-1] if home else ""
                    a_key = away.lower().split()[-1] if away else ""
                    h_profile = SPORTS_KNOWLEDGE.get(h_key, {})
                    a_profile = SPORTS_KNOWLEDGE.get(a_key, {})

                    # Form-based adjustment
                    h_phase = h_profile.get("phase", "").lower()
                    a_phase = a_profile.get("phase", "").lower()

                    # Boost if betting on a team in elite/dominant phase
                    elite_tags = ["elite", "campeão", "dominan", "lethal", "firepower", "machine"]
                    crisis_tags = ["rebuild", "crise", "struggling", "tanking"]

                    sel_is_home = home.lower() in tip.get("selection", "").lower()

                    if sel_is_home:
                        if any(t in h_phase for t in elite_tags):
                            tip["prob"] = min(95, tip["prob"] + 3)
                            funnel_notes.append(f"📊 KB: {home} em fase ELITE")
                        if any(t in a_phase for t in crisis_tags):
                            tip["prob"] = min(95, tip["prob"] + 2)
                            funnel_notes.append(f"📊 KB: {away} em CRISE")
                        if any(t in h_phase for t in crisis_tags):
                            tip["prob"] = max(30, tip["prob"] - 5)
                            funnel_notes.append(f"⚠️ KB: {home} em fase NEGATIVA")
                    else:
                        if any(t in a_phase for t in elite_tags):
                            tip["prob"] = min(95, tip["prob"] + 3)
                            funnel_notes.append(f"📊 KB: {away} em fase ELITE")
                        if any(t in h_phase for t in crisis_tags):
                            tip["prob"] = min(95, tip["prob"] + 2)
                            funnel_notes.append(f"📊 KB: {home} em CRISE")
                        if any(t in a_phase for t in crisis_tags):
                            tip["prob"] = max(30, tip["prob"] - 5)
                            funnel_notes.append(f"⚠️ KB: {away} em fase NEGATIVA")
                except Exception as e:
                    pass  # KB is supplemental, don't block

            # ─── STAGE 3.5: 365SCORES LINEUP INTELLIGENCE (PRE-FETCHED) ───
            if SCORES365_ACTIVE:
                try:
                    # Use pre-fetched data from parallel batch (or fetch single if not turbo)
                    intel = intel_map.get(home)
                    if not intel and not TURBO_ACTIVE and get_lineup_intelligence:
                        sport_365 = "basketball" if sport == "basketball" else "football"
                        intel = get_lineup_intelligence(home, away, target_date, sport=sport_365)
                    
                    if intel:
                        adj = intel.get("prob_adjustment", 0)
                        if adj != 0:
                            sel_lower = tip.get("selection", "").lower()
                            is_home_pick = home.lower() in sel_lower or any(p in sel_lower for p in home.lower().split() if len(p) > 3)
                            if is_home_pick:
                                tip["prob"] = max(30, min(95, tip["prob"] + adj))
                            else:
                                tip["prob"] = max(30, min(95, tip["prob"] - adj))
                            funnel_notes.append(f"🏥 365S: adj {adj:+d}% (desfalques)")

                        hf = intel.get("home_formation", "")
                        af = intel.get("away_formation", "")
                        if hf and af:
                            funnel_notes.append(f"📋 {home} {hf} vs {away} {af}")

                        sentiment = intel.get("public_sentiment", {})
                        if sentiment.get("total_votes", 0) > 500:
                            h_vote = sentiment.get("home_pct", 0)
                            a_vote = sentiment.get("away_pct", 0)
                            funnel_notes.append(f"🗳️ Público: {home} {h_vote}% | {away} {a_vote}%")

                        for fact in intel.get("key_facts", []):
                            if fact.startswith("❌") or fact.startswith("⚠️"):
                                funnel_notes.append(fact)
                                break
                except Exception as e:
                    print(f"[AUTO-ENGINE] ⚠️ 365Scores error for {home}: {e}")

            # ─── STAGE 4: TRAP HUNTER (detect suspicious odds) ───
            if FUNNEL_ACTIVE:
                try:
                    match_name = f"{home} vs {away}"
                    traps = trap_hunter_funnel(tip["prob"], tip_odd, match_name)
                    if traps:
                        tip["prob"] = max(30, tip["prob"] - 8)
                        tip["reason"] += f" | 🕵️ TRAP DETECTED"
                        funnel_notes.append(traps[0])
                except Exception:
                    pass

            # ─── STAGE 4.1: GOD MODE (UNSTOPPABLE 90% PROTOCOL) ───
            # Gives massive +20% boost to TRUE LOCKS (elite form + health + motivation)
            if FUNNEL_ACTIVE and KB_ACTIVE:
                try:
                    h_key = home.lower().split()[-1] if home else ""
                    a_key = away.lower().split()[-1] if away else ""
                    h_profile = SPORTS_KNOWLEDGE.get(h_key, {})
                    a_profile = SPORTS_KNOWLEDGE.get(a_key, {})
                    
                    sel_lower = tip.get("selection", "").lower()
                    is_home_pick = home.lower() in sel_lower or any(
                        p in sel_lower for p in home.lower().split() if len(p) > 3
                    )
                    
                    if is_home_pick:
                        god_boost, god_reasons = protocol_unstoppable_90(h_profile, a_profile, True)
                    else:
                        god_boost, god_reasons = protocol_unstoppable_90(a_profile, h_profile, False)
                    
                    if god_boost > 0:
                        tip["prob"] = min(97, tip["prob"] + god_boost)
                        tip["badge"] = "🔐 GOD MODE"
                        for gr in god_reasons[:2]:
                            funnel_notes.append(gr)
                        print(f"[AUTO-ENGINE] 🔐 GOD MODE ACTIVATED: {home} vs {away} (+{god_boost}%)")
                except Exception:
                    pass

            # ─── STAGE 4.2: LAUNDROMAT (BOOKIE TRAP DETECTOR) ───
            # Detects when public favorites have suspiciously high odds
            if FUNNEL_ACTIVE and KB_ACTIVE:
                try:
                    h_key = home.lower().split()[-1] if home else ""
                    a_key = away.lower().split()[-1] if away else ""
                    h_profile = SPORTS_KNOWLEDGE.get(h_key, {"name": home})
                    a_profile = SPORTS_KNOWLEDGE.get(a_key, {"name": away})
                    h_profile["name"] = home
                    a_profile["name"] = away
                    
                    laundry_adj, laundry_msg = funnel_laundromat(
                        h_profile, float(tip.get("odd", 1.5)), a_profile
                    )
                    if laundry_adj != 0:
                        tip["prob"] = max(30, tip["prob"] + laundry_adj)
                        funnel_notes.append(f"🧼 LAUNDROMAT: {laundry_adj:+d}%")
                except Exception:
                    pass

            # ─── STAGE 4.3: SHARP MONEY TRACKER (365S SENTIMENT) ───
            # Uses 365Scores public voting data to detect reverse line movement
            if SHARP_MONEY_ACTIVE and SCORES365_ACTIVE:
                try:
                    intel = intel_map.get(home)
                    if intel:
                        sentiment = intel.get("public_sentiment", {})
                        total_votes = sentiment.get("total_votes", 0)
                        
                        if total_votes > 300:
                            h_vote = sentiment.get("home_pct", 50)
                            a_vote = sentiment.get("away_pct", 50)
                            
                            sel_lower = tip.get("selection", "").lower()
                            is_home_pick = home.lower() in sel_lower or any(
                                p in sel_lower for p in home.lower().split() if len(p) > 3
                            )
                            
                            # Determine if we're betting WITH or AGAINST the public
                            our_pct = h_vote if is_home_pick else a_vote
                            
                            if our_pct > 70:
                                # Public is heavily on our side — check for trap
                                if tip_odd > 1.60:
                                    # High public% + high odds = potential trap
                                    sharp_adj, sharp_msg = tracker_sharp_money(
                                        home if is_home_pick else away, our_pct, "up"
                                    )
                                    if sharp_adj != 0:
                                        tip["prob"] = max(30, tip["prob"] + sharp_adj)
                                        funnel_notes.append(f"💰 SHARP: {sharp_msg[:60]}")
                            elif our_pct < 30:
                                # We're contrarian — smart money might be with us
                                sharp_adj, sharp_msg = tracker_sharp_money(
                                    home if is_home_pick else away, our_pct, "down"
                                )
                                if sharp_adj > 0:
                                    tip["prob"] = min(95, tip["prob"] + 3)
                                    funnel_notes.append("💰 SHARP: Contrarian play — smart money aligned")
                except Exception:
                    pass

            # ─── STAGE 5: SELF-CALIBRATION (CACHED — no file re-read) ───
            if CALIBRATION_ACTIVE:
                try:
                    calibrated = apply_calibration_fast(tip["prob"], tip_odd, league)
                    if calibrated != tip["prob"]:
                        funnel_notes.append(f"📐 CALIBRAÇÃO: {tip['prob']}% → {calibrated}% (baseado em histórico)")
                        tip["prob"] = calibrated
                except Exception:
                    pass

            # ─── STAGE 5.5: SELF-LEARNING CORRECTIONS ───
            if LEARNING_ACTIVE:
                try:
                    learned_prob, learn_notes = apply_learning_correction(
                        tip["prob"], tip_odd, league, tip.get("selection", ""), home, away
                    )
                    if learned_prob != tip["prob"]:
                        funnel_notes.append(f"🧠 AUTOCONHECIMENTO: {tip['prob']}% → {learned_prob}%")
                        for ln in learn_notes:
                            funnel_notes.append(ln)
                        tip["prob"] = learned_prob
                except Exception:
                    pass

            # ─── STAGE 6: FINAL EV GATE ───
            tip_prob = tip.get("prob", 50)
            implied = (1 / tip_odd) * 100 if tip_odd > 0 else 100
            # ─── STAGE 7: DYNAMIC BADGE & SNIPER RE-EVALUATION ───
            # Re-evaluate is_sniper and badges using CORRECTED prob and LEARNED thresholds
            final_prob = tip.get("prob", 50)
            thresholds = learned_thresholds if LEARNING_ACTIVE else {"sniper": 72, "banker": 82, "minimum": 62}
            
            is_sniper = final_prob >= thresholds.get("sniper", 72)
            
            # Re-assign badge if it's not already something special like GOD MODE
            if "GOD MODE" not in tip.get("badge", ""):
                if final_prob >= thresholds.get("banker", 82):
                    tip["badge"] = "💰 BANKER"
                elif final_prob >= thresholds.get("sniper", 72):
                    tip["badge"] = "🎯 SNIPER"
                elif "EV GATE" not in tip.get("badge", ""):
                    tip["badge"] = "🛡️ SAFE" if final_prob >= 65 else "🔎 ANALYZE"

            # Append funnel notes to reason
            if funnel_notes:
                tip["reason"] += " | " + " | ".join(funnel_notes[-3:])  # Max 3 notes

            # ─── STAGE 8: 80% GREEN SURGICAL FILTERS ───
            toxic_teams = GLOBAL_LEARNING.get("toxic_teams", {})
            blacklisted_leagues = GLOBAL_LEARNING.get("blacklisted_leagues", [])
            market_efficiency = GLOBAL_LEARNING.get("market_efficiency", {})
            
            # 1. Variance Protection
            mkt_key = "ML" if "vence" in tip['selection'].lower() else "DC"
            league_mkt_key = f"{game['league']} ({mkt_key})"
            eff = market_efficiency.get(league_mkt_key, 100)
            if eff < 60:
                tip['prob'] -= 7
                tip['reason'] += f" | 🛡️ VAR PROTECT: {eff}% eff"
                
            # 2. Toxic Team Protection
            h_toxic = toxic_teams.get(home, "")
            a_toxic = toxic_teams.get(away, "")
            if "TOXIC" in str(h_toxic) or "TOXIC" in str(a_toxic):
                tip['prob'] = int(tip['prob'] * 0.75) # Heavy cut
                tip['reason'] += f" | 🔥 TOXIC TEAM: {h_toxic or a_toxic}"
            elif "UNRELIABLE" in str(h_toxic) or "UNRELIABLE" in str(a_toxic):
                tip['prob'] -= 10
                tip['reason'] += f" | ⚠️ UNRELIABLE TEAM"

            # 3. League Blacklist
            if game['league'] in blacklisted_leagues:
                tip['prob'] = int(tip['prob'] * 0.5)
                tip['reason'] += " | 🚫 BLACKLISTED LEAGUE"

            # Re-Finalize Badge after surgical filters
            is_sniper = tip['prob'] >= thresholds.get("sniper", 72)
            if tip['prob'] >= thresholds.get("banker", 82):
                tip["badge"] = "💰 BANKER"
            elif tip['prob'] >= thresholds.get("sniper", 72):
                tip["badge"] = "🎯 SNIPER"
            elif tip['prob'] < 60:
                tip["badge"] = "❌ AVOID"

            processed.append({
                "sport": sport,
                "home_team": home,
                "away_team": away,
                "league": game["league"],
                "time": game["time"],
                "odds": {"home": str(oh), "draw": str(od), "away": str(oa)},
                "best_tip": {**tip, "prob": max(5, min(99, tip["prob"]))},
                "is_sniper": is_sniper,
                "home_logo": get_logo(home, sport),
                "away_logo": get_logo(away, sport),
                "bet_url": "#",
                "comparisons": gen_bookmaker_odds(tip_odd),
            })
        except Exception as e:
            print(f"[AUTO-ENGINE] Erro em {game.get('home','')} vs {game.get('away','')}: {e}")
            continue

    # Sort: snipers primeiro, depois por horário
    processed.sort(key=lambda x: (not x.get("is_sniper", False), x["time"]))

    # --- 🕵️ REAL NEWS AGENT (PARALLEL GOOGLE INTELLIGENCE) ---
    print("[AUTO-ENGINE] 🕵️ [NEWS AGENT] Escutando conversas de vestiário...")
    
    try:
        import real_news
        
        # Build list of teams to scan (top 5 or all snipers)
        teams_to_scan = []
        scan_limit = 5
        scanned = 0
        scan_games = []
        
        for game in processed:
            if scanned >= scan_limit and not game.get('is_sniper'):
                break
            teams_to_scan.append((game['home_team'], game['sport']))
            teams_to_scan.append((game['away_team'], game['sport']))
            scan_games.append(game)
            scanned += 1
        
        # PARALLEL news fetch for all teams at once
        if TURBO_ACTIVE and teams_to_scan:
            news_map = fetch_news_parallel(teams_to_scan, real_news.search_team_news)
        else:
            news_map = {}
            for team, sport in teams_to_scan:
                news_map[team] = real_news.search_team_news(team, sport)
        
        # Apply news to processed games
        for game in scan_games:
            h_news = news_map.get(game['home_team'], "")
            a_news = news_map.get(game['away_team'], "")
            
            h_bad = any(kw in h_news.lower() for kw in ["lesão", "fora", "dúvida"])
            a_bad = any(kw in a_news.lower() for kw in ["lesão", "fora", "dúvida"])
            
            tip = game['best_tip']
            sel = tip['selection'].lower()
            
            if "casa" in sel or game['home_team'].lower() in sel:
                if h_bad:
                    tip['prob'] = max(30, tip['prob'] - 5)
                    tip['reason'] += f" | ⚠️ ALERTA: {h_news[:50]}..."
                if a_bad:
                    tip['prob'] = min(99, tip['prob'] + 3)
                    tip['reason'] += f" | 🗞️ INFO: Rival com problemas."
            elif "fora" in sel or game['away_team'].lower() in sel:
                if a_bad:
                    tip['prob'] = max(30, tip['prob'] - 5)
                    tip['reason'] += f" | ⚠️ ALERTA: {a_news[:50]}..."
                if h_bad:
                    tip['prob'] = min(99, tip['prob'] + 3)
    except Exception as e:
        print(f"[AUTO-ENGINE] ⚠️ Erro no News Agent: {e}")

    # 3. Builds trebles
    trebles = build_trebles(processed)

    # [-NEW-] Local Persistence for Trebles (JSON)
    try:
        local_hist_file = "history_trebles.json"
        
        # Load existing
        if os.path.exists(local_hist_file):
            with open(local_hist_file, "r", encoding="utf-8") as f:
                existing_trebles = json.load(f)
        else:
            existing_trebles = []
        
        # Prepare date
        d_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
        date_fmt = d_obj.strftime("%d/%m")

        # Append new unique trebles
        added_count = 0
        for t in trebles:
            # Check for duplicates (same name AND same date)
            is_dup = False
            for old in existing_trebles:
                if old.get("name") == t["name"] and old.get("date") == date_fmt:
                    is_dup = True
                    break
            
            if not is_dup:
                # Structure for saving
                new_t = {
                    "created_at": datetime.datetime.now().isoformat(),
                    "date": date_fmt,
                    "name": t["name"],
                    "odd": t["total_odd"], # Using 'odd' to match frontend expectation
                    "total_odd": t["total_odd"],
                    "status": "PENDING",
                    "profit": "---", 
                    "selections": [s["pick"] for s in t["selections"]], # Visual strings
                    "components": [] # Structured for updates
                }

                # Populate components for components-level tracking
                for s in t["selections"]:
                    new_t["components"].append({
                        "match": s["match"],
                        "pick": s["pick"],
                        "prob": s.get("prob", 0),
                        "status": "PENDING"
                    })
                
                existing_trebles.insert(0, new_t) # Newest first
                added_count += 1
        
        # Save back
        if added_count > 0:
            with open(local_hist_file, "w", encoding="utf-8") as f:
                json.dump(existing_trebles, f, indent=4, ensure_ascii=False)
            print(f"[AUTO-ENGINE] 💾 Persisted {added_count} new trebles to {local_hist_file}")
            
    except Exception as e:
        print(f"[AUTO-ENGINE] ⚠️ Error saving local treble history: {e}")

    # --- CLOUD SYNC AUTOMATION (non-blocking) ---
    try:
        from supabase_client import log_match_prediction, get_supabase
        
        for g in processed:
             log_match_prediction(g['home_team'], g['away_team'], g['best_tip'])

        client = get_supabase()
        if client:
            d_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
            date_fmt = d_obj.strftime("%d/%m")
            
            for t in trebles:
                 existing = client.table("trebles").select("*", eq_field="name", eq_value=t['name'])
                 is_dup = False
                 if existing:
                     for e in existing:
                         if e.get('date') == date_fmt:
                             is_dup = True
                             break
                 
                 if not is_dup:
                     payload = {
                        "date": date_fmt,
                        "name": t['name'],
                        "odd": float(t['total_odd']),
                        "status": "PENDING",
                        "profit": "Aguardando",
                        "selections": [s['pick'] for s in t['selections']],
                        "synced_at": datetime.datetime.now().isoformat()
                     }
                     client.table("trebles").insert(payload)
                     print(f"[AUTO-ENGINE] ☁️ Sincronizado treble: {t['name']}")
    except Exception as e:
        print(f"[AUTO-ENGINE] ⚠️ Erro no Cloud Sync: {e}")

    t_total = _time.time() - t_total_start
    print(f"[AUTO-ENGINE] ⚡ TURBO COMPLETE: {len(processed)} picks + {len(trebles)} combos em {t_total:.1f}s")
    return {"games": processed, "trebles": trebles}

if __name__ == "__main__":
    import sys
    import datetime
    target = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.now().strftime("%Y-%m-%d")
    res = get_auto_games(target)
    if res and res.get('trebles'):
        for t in res['trebles']:
            print(t.get('copy_text', ''))
