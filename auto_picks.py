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
    """Gera melhor tip para jogo NBA baseado na simulação."""
    home, away = game["home"], game["away"]
    h_prob, a_prob = sim["home_prob"], sim["away_prob"]
    total_avg = sim["total_avg"]
    h_rec = game.get("home_record", "")
    a_rec = game.get("away_record", "")
    ou_line = game.get("espn_odds", {}).get("over_under", 0)

    odd_h = prob_to_odd(h_prob)
    odd_a = prob_to_odd(a_prob)

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
# SECTION 6: TREBLE BUILDER
# ══════════════════════════════════════════════

def build_trebles(processed_games):
    """Auto-constrói combos a partir dos picks de maior confiança."""
    trebles = []
    strong = [g for g in processed_games if g["best_tip"]["prob"] >= 60]
    strong.sort(key=lambda x: x["best_tip"]["prob"], reverse=True)

    # Detect ML/favorite picks (multiple formats from auto engine + manual)
    ml_keywords = ["vence", "ml", "ou empate", "dupla chance", "vitória", "win"]
    over_keywords = ["over", "acima", "mais de"]
    
    ml_picks = [g for g in strong if any(kw in g["best_tip"]["selection"].lower() for kw in ml_keywords)]
    over_picks = [g for g in strong if any(kw in g["best_tip"]["selection"].lower() for kw in over_keywords)]
    
    # If no ML found, use top probability picks as fallback
    if len(ml_picks) < 2:
        ml_picks = strong[:6]


    # 🛡️ BUNKER: Top 3 ML (highest prob)
    if len(ml_picks) >= 2:
        picks = ml_picks[:3]
        total_odd = 1
        sels = []
        for p in picks:
            total_odd *= p["best_tip"]["odd"]
            sels.append({"match": f"{p['away_team']} @ {p['home_team']}", "pick": f"{p['best_tip']['selection']} (@{p['best_tip']['odd']})"})
        prob_est = max(55, int(100 / max(total_odd, 1.01)))
        trebles.append({
            "name": "🛡️ BUNKER (AUTO-GERADO)",
            "total_odd": f"{total_odd:.2f}",
            "probability": f"{prob_est}%",
            "selections": sels,
            "copy_text": f"🛡️ BUNKER:\n" + "\n".join([f"- {s['pick']}" for s in sels]) + f"\nOdd Total: {total_odd:.2f}"
        })

    # 🔥 VALUE: 1 ML + Overs
    if ml_picks and over_picks:
        picks = ml_picks[:1] + over_picks[:2]
        total_odd = 1
        sels = []
        for p in picks:
            total_odd *= p["best_tip"]["odd"]
            sels.append({"match": f"{p['away_team']} @ {p['home_team']}", "pick": f"{p['best_tip']['selection']} (@{p['best_tip']['odd']})"})
        prob_est = max(45, int(100 / max(total_odd, 1.01)))
        trebles.append({
            "name": "🔥 VALUE MIX (AUTO-GERADO)",
            "total_odd": f"{total_odd:.2f}",
            "probability": f"{prob_est}%",
            "selections": sels,
            "copy_text": f"🔥 VALUE MIX:\n" + "\n".join([f"- {s['pick']}" for s in sels]) + f"\nOdd Total: {total_odd:.2f}"
        })

    # 💎 SUPER COMBO: 4 legs
    if len(ml_picks) >= 4:
        picks = ml_picks[:4]
        total_odd = 1
        sels = []
        for p in picks:
            total_odd *= p["best_tip"]["odd"]
            sels.append({"match": f"{p['away_team']} @ {p['home_team']}", "pick": f"{p['best_tip']['selection']} (@{p['best_tip']['odd']})"})
        prob_est = max(40, int(100 / max(total_odd, 1.01)))
        trebles.append({
            "name": "💎 SUPER COMBO 4-LEGS (AUTO)",
            "total_odd": f"{total_odd:.2f}",
            "probability": f"{prob_est}%",
            "selections": sels,
            "copy_text": f"💎 SUPER COMBO:\n" + "\n".join([f"- {s['pick']}" for s in sels]) + f"\nOdd Total: {total_odd:.2f}"
        })

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
        )
        FUNNEL_ACTIVE = True
        print("[AUTO-ENGINE] ✅ AI Engine CONNECTED")
    except Exception as e:
        print(f"[AUTO-ENGINE] ⚠️ AI Engine not available: {e}")
        FUNNEL_ACTIVE = False

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
        from self_learning import apply_learning_correction, study_results, get_learning_summary
        LEARNING_ACTIVE = True
        # THROTTLED: Only study once per 10 minutes
        now = _time.time()
        if (now - _last_study_time) > 600:
            study_results()
            _last_study_time = now
            summary = get_learning_summary()
            print(f"[AUTO-ENGINE] ✅ Self-Learning: {summary.get('corrections_active', 0)} correções")
        else:
            print(f"[AUTO-ENGINE] ✅ Self-Learning CACHED (last study {int(now - _last_study_time)}s ago)")
    except Exception as e:
        LEARNING_ACTIVE = False
        print(f"[AUTO-ENGINE] ⚠️ Self-Learning not available: {e}")

    # ══════════════════════════════════════════════
    # STAGE 0: PARALLEL DATA FETCH (All I/O at once)
    # ══════════════════════════════════════════════
    t0 = _time.time()
    
    # 1. Busca jogos na ESPN (PARALELO)
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
            ev_edge = tip_prob - implied
            ev_pct = calculate_expected_value(tip_prob, tip_odd) if FUNNEL_ACTIVE else round((tip_prob / 100 * tip_odd - 1) * 100, 2)

            if ev_edge < 5:
                tip["reason"] += f" | ⚠️ EV GATE: edge {ev_edge:.1f}%"
                tip["badge"] = "⚠️ EV GATE"
            elif ev_edge >= 15:
                tip["badge"] = "💰 BANKER"
                funnel_notes.append(f"💰 EV+{ev_edge:.0f}% — VALUE BET")

            # Append funnel notes to reason
            if funnel_notes:
                tip["reason"] += " | " + " | ".join(funnel_notes[-3:])  # Max 3 notes

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
