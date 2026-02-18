"""
AUTO PICKS ENGINE v1.0 - Gerador Automático de Tips 🤖
Substitui a necessidade de hardcodar picks por data.

Pipeline:
1. ESPN API → Busca jogos do dia (todas as ligas)
2. Monte Carlo (NBA) / Poisson (Futebol) → Simula resultados
3. Tip Generator → Seleciona melhor mercado por jogo
4. EV Gate → Filtra tips sem valor
5. Treble Builder → Monta combos automaticamente
"""

import requests
import datetime
import numpy as np
import math
import random
import sys
import os

# Fix encoding for Windows terminals
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ══════════════════════════════════════════════
# SECTION 1: POWER RATINGS (Source: ESPN Feb 11 2026)
# ══════════════════════════════════════════════

NBA_POWER = {
    "Pistons": 98, "Celtics": 93, "Knicks": 92, "Cavaliers": 91,
    "Thunder": 93, "Rockets": 90, "Raptors": 89, "Sixers": 87,
    "Nuggets": 86, "Timberwolves": 85, "Magic": 84, "Clippers": 82,
    "Warriors": 81, "Suns": 80, "Mavericks": 78, "Heat": 79,
    "Kings": 78, "Grizzlies": 80, "Lakers": 77, "Hawks": 76,
    "Hornets": 75, "Spurs": 74, "Bulls": 74, "Pelicans": 72,
    "Bucks": 71, "Jazz": 69, "Blazers": 67, "Nets": 65,
    "Pacers": 62, "Wizards": 61
}

FOOTBALL_POWER = {
    # Premier League
    "Liverpool": 93, "Arsenal": 91, "Man City": 90, "Manchester City": 90,
    "Chelsea": 82, "Tottenham": 80, "Tottenham Hotspur": 80,
    "Newcastle": 79, "Newcastle United": 79, "Man United": 75, "Manchester United": 75,
    "Aston Villa": 78, "Brighton": 77, "Bournemouth": 74, "Fulham": 73,
    "West Ham": 72, "Crystal Palace": 71, "Brentford": 70, "Wolves": 68,
    "Nottingham Forest": 72, "Everton": 66, "Leicester": 65, "Ipswich": 60,
    "Southampton": 58, "Leeds": 70, "Leeds United": 70,
    "Burnley": 63, "Sheffield United": 60, "Luton": 58, "Sunderland": 68,
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
    "Internacional": 80, "São Paulo": 79, "Cruzeiro": 77, "Atlético-MG": 76,
    "Grêmio": 75, "Bahia": 74, "Vasco": 72, "Corinthians": 73,
    "Fluminense": 71, "Vitória": 65, "Santos": 70,
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
    """Busca todos os jogos agendados para uma data via ESPN API."""
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

                    # Parse time UTC -> BRT (UTC-3)
                    game_time = "TBD"
                    try:
                        raw = event.get("date", "")
                        dt = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
                        brt = dt - datetime.timedelta(hours=3)
                        game_time = brt.strftime("%H:%M")
                    except:
                        pass

                    # ESPN odds (spread, O/U)
                    espn_odds = {}
                    odds_data = comp.get("odds", [])
                    if odds_data:
                        espn_odds["spread"] = odds_data[0].get("details", "")
                        espn_odds["over_under"] = odds_data[0].get("overUnder", 0)

                    # Records
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
    """Gera melhor tip para jogo de futebol baseado em Poisson."""
    home, away = game["home"], game["away"]
    hp = sim["home_prob"]
    dp = sim["draw_prob"]
    ap = sim["away_prob"]
    o25 = sim["over_25_prob"]

    odd_h = prob_to_odd(hp)
    odd_d = prob_to_odd(dp)
    odd_a = prob_to_odd(ap)

    # Double Chance if strong
    dc_home = hp + dp  # Home or Draw

    if hp >= 60:
        tip = {
            "market": "Vencedor", "selection": f"{home} Vence",
            "prob": int(hp), "odd": odd_h,
            "reason": f"⚽ [POISSON]: {home} com {hp}% em casa. Domínio estatístico claro.",
            "badge": "💰 BANKER" if hp >= 72 else "🎯 SNIPER",
        }
    elif ap >= 55:
        tip = {
            "market": "Vencedor", "selection": f"{away} Vence",
            "prob": int(ap), "odd": odd_a,
            "reason": f"⚽ [POISSON]: {away} favorito fora com {ap}%. Superior em qualidade.",
            "badge": "🎯 SNIPER",
        }
    elif dc_home >= 75:
        dc_odd = prob_to_odd(dc_home)
        tip = {
            "market": "Dupla Chance", "selection": f"{home} ou Empate",
            "prob": int(dc_home), "odd": dc_odd,
            "reason": f"⚽ [POISSON]: Dupla Chance {home} ({dc_home:.0f}%). Segurança em casa.",
            "badge": "🛡️ SAFE",
        }
    elif o25 >= 65:
        tip = {
            "market": "Gols", "selection": "Over 2.5 Gols",
            "prob": int(o25), "odd": prob_to_odd(o25),
            "reason": f"⚽ [POISSON]: {o25}% para Over 2.5. Total esperado: {sim['expected_total']:.1f} gols.",
            "badge": "🚀 OVER",
        }
    else:
        # Safest option: DC home
        dc_odd = prob_to_odd(dc_home)
        tip = {
            "market": "Dupla Chance", "selection": f"{home} ou Empate",
            "prob": int(dc_home), "odd": dc_odd,
            "reason": f"⚽ [POISSON]: Jogo equilibrado. DC {home} ({dc_home:.0f}%) é o mais seguro.",
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

def get_auto_games(target_date):
    """
    Entrada principal do Auto Engine.
    Retorna {"games": [...], "trebles": [...]} no mesmo formato
    que data_fetcher.get_games_for_date().
    """
    print(f"[AUTO-ENGINE] 🤖 Gerando picks automáticos para {target_date}...")

    # 1. Busca jogos na ESPN
    raw_games = fetch_espn_schedule(target_date)
    if not raw_games:
        print("[AUTO-ENGINE] ⚠️ Nenhum jogo encontrado na ESPN")
        return {"games": [], "trebles": []}

    # 2. Gera tips para cada jogo
    processed = []
    for game in raw_games:
        try:
            sport = game["sport"]
            home = game["home"]
            away = game["away"]

            if sport == "basketball":
                h_pow = NBA_POWER.get(home, 75)
                a_pow = NBA_POWER.get(away, 75)
                sim = monte_carlo_nba(h_pow, a_pow)
                tip, is_sniper, oh, od, oa = generate_nba_tip(game, sim)
            else:
                h_pow = FOOTBALL_POWER.get(home, 70)
                a_pow = FOOTBALL_POWER.get(away, 70)
                h_exp = 1.35 * (h_pow / 75)
                a_exp = 1.10 * (a_pow / 75)
                sim = poisson_football(h_exp, a_exp)
                tip, is_sniper, oh, od, oa = generate_football_tip(game, sim)

            # EV Gate
            tip_odd = float(tip.get("odd", 1.5))
            tip_prob = tip.get("prob", 50)
            implied = (1 / tip_odd) * 100 if tip_odd > 0 else 100
            ev_edge = tip_prob - implied
            if ev_edge < 5:
                tip["reason"] += f" | ⚠️ EV GATE: edge {ev_edge:.1f}%"
                tip["badge"] = "⚠️ EV GATE"

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

    # --- 🕵️ REAL NEWS AGENT (GOOGLE INTELLIGENCE) ---
    print("[AUTO-ENGINE] 🕵️ [NEWS AGENT] Escutando conversas de vestiário (Google News)...")
    
    try:
        import real_news
        
        # Scan top 5 (or all snipers)
        scan_limit = 5
        scanned = 0
        
        for game in processed:
            if scanned >= scan_limit and not game.get('is_sniper'):
                break
                
            # Busca News (Retorna String)
            h_news = real_news.search_team_news(game['home_team'], game['sport'])
            a_news = real_news.search_team_news(game['away_team'], game['sport'])
            
            # Simple Sentiment Analysis
            h_bad = "lesão" in h_news.lower() or "fora" in h_news.lower() or "dúvida" in h_news.lower()
            a_bad = "lesão" in a_news.lower() or "fora" in a_news.lower() or "dúvida" in a_news.lower()
            
            # Adjust Probability based on News
            tip = game['best_tip']
            sel = tip['selection'].lower()
            
            # Logic: If betting on Home and Home has bad news, reduce confidence
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
                    
            scanned += 1
            
    except Exception as e:
        print(f"[AUTO-ENGINE] ⚠️ Erro no News Agent: {e}")

    # 3. Builds trebles
    trebles = build_trebles(processed)

    # --- CLOUD SYNC AUTOMATION ---
    try:
        from supabase_client import log_match_prediction, get_supabase
        
        # 1. Save Predictions (Games)
        # Note: log_match_prediction handles insertion. User needs 'predictions' table.
        for g in processed:
             log_match_prediction(g['home_team'], g['away_team'], g['best_tip'])

        # 2. Save Trebles to 'trebles' table
        client = get_supabase()
        if client:
            d_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
            date_fmt = d_obj.strftime("%d/%m")
            
            for t in trebles:
                 # Avoid duplicates: verify if (name, date) exists
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

    print(f"[AUTO-ENGINE] ✅ {len(processed)} picks + {len(trebles)} combos gerados")
    return {"games": processed, "trebles": trebles}
