"""
🔄 UPDATE PENDING RESULTS - Atualiza todos os PENDING que já aconteceram
Busca resultados da ESPN para 24/02 e 25/02 e atualiza o history.json
"""

import json
import os
import datetime
import requests

HISTORY_PATH = 'history.json'

# Ligas a buscar na ESPN (todas as que temos no history)
ESPN_LEAGUES = {
    "nba":                   "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date}",
    "eng.1":                 "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates={date}",
    "esp.1":                 "https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard?dates={date}",
    "ita.1":                 "https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/scoreboard?dates={date}",
    "ger.1":                 "https://site.api.espn.com/apis/site/v2/sports/soccer/ger.1/scoreboard?dates={date}",
    "fra.1":                 "https://site.api.espn.com/apis/site/v2/sports/soccer/fra.1/scoreboard?dates={date}",
    "bra.1":                 "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard?dates={date}",
    "eng.fa":                "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.fa/scoreboard?dates={date}",
    "conmebol.libertadores": "https://site.api.espn.com/apis/site/v2/sports/soccer/conmebol.libertadores/scoreboard?dates={date}",
    "conmebol.sudamericana": "https://site.api.espn.com/apis/site/v2/sports/soccer/conmebol.sudamericana/scoreboard?dates={date}",
    "por.1":                 "https://site.api.espn.com/apis/site/v2/sports/soccer/por.1/scoreboard?dates={date}",
    "ned.1":                 "https://site.api.espn.com/apis/site/v2/sports/soccer/ned.1/scoreboard?dates={date}",
    "tur.1":                 "https://site.api.espn.com/apis/site/v2/sports/soccer/tur.1/scoreboard?dates={date}",
    "esp.2":                 "https://site.api.espn.com/apis/site/v2/sports/soccer/esp.2/scoreboard?dates={date}",
}

# Mapeamento de nomes ESPN -> nomes do nosso sistema
TEAM_OVERRIDES = {
    # NBA
    "Boston Celtics": "Celtics", "New York Knicks": "Knicks", "Cleveland Cavaliers": "Cavaliers",
    "Oklahoma City Thunder": "Thunder", "Houston Rockets": "Rockets", "Golden State Warriors": "Warriors",
    "Denver Nuggets": "Nuggets", "LA Clippers": "Clippers", "Los Angeles Clippers": "Clippers",
    "Milwaukee Bucks": "Bucks", "Miami Heat": "Heat", "Phoenix Suns": "Suns",
    "Dallas Mavericks": "Mavericks", "Minnesota Timberwolves": "Timberwolves", "Sacramento Kings": "Kings",
    "Memphis Grizzlies": "Grizzlies", "Los Angeles Lakers": "Lakers", "Atlanta Hawks": "Hawks",
    "Charlotte Hornets": "Hornets", "San Antonio Spurs": "Spurs", "Chicago Bulls": "Bulls",
    "New Orleans Pelicans": "Pelicans", "Utah Jazz": "Jazz", "Portland Trail Blazers": "Trail Blazers",
    "Brooklyn Nets": "Nets", "Indiana Pacers": "Pacers", "Washington Wizards": "Wizards",
    "Orlando Magic": "Magic", "Philadelphia 76ers": "Sixers", "Detroit Pistons": "Pistons",
    "Toronto Raptors": "Raptors",
    # Soccer
    "Tottenham Hotspur": "Tottenham", "Manchester United": "Man United",
    "Manchester City": "Man City", "Wolverhampton Wanderers": "Wolverhampton Wanderers",
    "Nottingham Forest": "Nott. Forest", "Brighton and Hove Albion": "Brighton",
    "Paris Saint-Germain": "PSG",
    "Atlético Mineiro": "Atlético-MG", "Atletico Mineiro": "Atlético-MG",
    "Gremio": "Grêmio", "Grêmio": "Grêmio",
    "Sao Paulo": "São Paulo",
    "Levante UD": "Levante",
    "Deportivo Alavés": "Alavés",
}

ALIASES = {
    "trail blazers": "Trail Blazers",
    "blazers": "Trail Blazers",
    "portland": "Trail Blazers",
    "wolverhampton": "Wolverhampton Wanderers",
    "wolves": "Wolverhampton Wanderers",
    "man city": "Man City",
    "manchester city": "Man City",
    "atletico-mg": "Atlético-MG",
    "atletico mg": "Atlético-MG",
    "atletico mineiro": "Atlético-MG",
    "sao paulo": "São Paulo",
    "grêmio": "Grêmio",
    "gremio": "Grêmio",
}


def fetch_espn_results(date_str):
    """Busca TODOS os resultados finalizados da ESPN para uma data."""
    date_param = date_str.replace("-", "")
    all_results = {}

    print(f"\n📡 Buscando resultados ESPN para {date_str}...")

    for league_key, url_template in ESPN_LEAGUES.items():
        url = url_template.format(date=date_param)
        try:
            resp = requests.get(url, timeout=12)
            if resp.status_code != 200:
                continue
            data = resp.json()
            events = data.get('events', [])
            if not events:
                continue

            for event in events:
                comps = event.get('competitions', [{}])[0]
                competitors = comps.get('competitors', [])
                if len(competitors) < 2:
                    continue

                home_comp = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
                away_comp = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])

                home_raw = home_comp.get('team', {}).get('displayName', '')
                away_raw = away_comp.get('team', {}).get('displayName', '')

                home_name = TEAM_OVERRIDES.get(home_raw, home_raw)
                away_name = TEAM_OVERRIDES.get(away_raw, away_raw)

                home_score = home_comp.get('score', '0') or '0'
                away_score = away_comp.get('score', '0') or '0'

                status_type = event.get('status', {}).get('type', {})
                is_completed = status_type.get('completed', False)
                state = status_type.get('name', '').lower()

                # Aceita jogos finalizados
                if is_completed or 'final' in state or 'post' in state:
                    try:
                        h_val = int(float(home_score))
                        a_val = int(float(away_score))
                    except:
                        h_val, a_val = 0, 0

                    entry = {
                        "home_val": h_val,
                        "away_val": a_val,
                        "score": f"{h_val}-{a_val}",
                        "home_name": home_name,
                        "away_name": away_name,
                        "league": league_key
                    }

                    all_results[home_name.lower()] = entry
                    all_results[away_name.lower()] = {
                        "home_val": h_val,
                        "away_val": a_val,
                        "score": f"{h_val}-{a_val}",
                        "home_name": home_name,
                        "away_name": away_name,
                        "league": league_key,
                        "is_away_team": True
                    }
                    print(f"   ✅ {home_name} {h_val}-{a_val} {away_name} [{league_key}]")

        except Exception as e:
            pass

    print(f"   📊 Total de resultados encontrados: {len(all_results) // 2} jogos\n")
    return all_results


def find_result(home, away, results_map):
    """Procura resultado correspondente para um jogo."""
    h_lower = home.lower().strip()
    a_lower = away.lower().strip()

    # Aplica aliases
    h_lookup = ALIASES.get(h_lower, h_lower)
    a_lookup = ALIASES.get(a_lower, a_lower)

    # Busca direta
    if h_lookup.lower() in results_map:
        res = results_map[h_lookup.lower()]
        # Verifica se o away bate (ou se é o away_team invertido)
        return res, True  # True = home perspective

    if a_lookup.lower() in results_map:
        res = results_map[a_lookup.lower()]
        return res, False  # False = away perspective

    # Busca parcial
    for key, val in results_map.items():
        if h_lower in key or key in h_lower:
            return val, True
        if a_lower in key or key in a_lower:
            return val, False

    return None, None


def evaluate_selection(selection, h_val, a_val, home, away):
    """Avalia se a aposta ganhou, perdeu ou é void."""
    sel = selection.lower().strip()
    is_win = False
    is_loss = False
    is_void = False

    def team_in(team_name):
        t = team_name.lower()
        if t in sel: return True
        alias = ALIASES.get(t, t)
        if alias.lower() in sel: return True
        # Checa partes do nome
        for part in t.split():
            if len(part) > 3 and part in sel:
                return True
        return False

    if "vence" in sel or " ml" in sel or "moneyline" in sel:
        if team_in(home):
            is_win = h_val > a_val
            is_loss = not is_win
        elif team_in(away):
            is_win = a_val > h_val
            is_loss = not is_win
        else:
            # Tenta inferir quem é o favorito no nome
            pass

    elif "ou empate" in sel or "dupla chance" in sel or "1x" in sel or "x2" in sel:
        if team_in(home) or "1x" in sel:
            is_win = h_val >= a_val
            is_loss = not is_win
        elif team_in(away) or "x2" in sel:
            is_win = a_val >= h_val
            is_loss = not is_win

    elif "dnb" in sel:
        if h_val == a_val:
            is_void = True
        elif team_in(home):
            is_win = h_val > a_val
            is_loss = not is_win
        elif team_in(away):
            is_win = a_val > h_val
            is_loss = not is_win

    elif "over" in sel:
        try:
            line = float(sel.split("over")[1].replace("gols", "").replace("pontos", "").strip().split()[0])
            total = h_val + a_val
            is_win = total > line
            is_loss = not is_win
        except:
            pass

    elif "under" in sel:
        try:
            line = float(sel.split("under")[1].replace("gols", "").replace("pontos", "").strip().split()[0])
            total = h_val + a_val
            is_win = total < line
            is_loss = not is_win
        except:
            pass

    elif "btts" in sel or "ambas marcam" in sel:
        is_win = h_val > 0 and a_val > 0
        is_loss = not is_win

    elif "empate" in sel and "ou" not in sel:
        is_win = h_val == a_val
        is_loss = not is_win

    if is_void:
        return "VOID"
    if is_win:
        return "WON"
    if is_loss:
        return "LOST"
    return "PENDING"


def main():
    print("=" * 60)
    print("🔄 ATUALIZADOR DE RESULTADOS PENDENTES")
    print("=" * 60)

    # Carrega histórico
    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        history = json.load(f)

    now = datetime.datetime.now()

    # Identifica datas com PENDING
    pending_dates = set()
    for entry in history:
        if entry.get('status') == 'PENDING':
            date_str = entry.get('date', '')
            if date_str:
                # Converte DD/MM -> YYYY-MM-DD
                try:
                    parts = date_str.split('/')
                    if len(parts) == 2:
                        dd, mm = parts
                        year = now.year
                        dt = datetime.datetime(year, int(mm), int(dd))
                        # Se a data está no futuro exato (hoje), verifica horário
                        if dt.date() < now.date():
                            pending_dates.add(dt.strftime("%Y-%m-%d"))
                        elif dt.date() == now.date():
                            # Inclui hoje também - busca para jogos que já ocorreram hoje
                            pending_dates.add(dt.strftime("%Y-%m-%d"))
                except:
                    pass

    if not pending_dates:
        print("✅ Nenhum jogo PENDING encontrado em datas passadas!")
        return

    print(f"\n📅 Datas com PENDING: {sorted(pending_dates)}")

    # Busca resultados ESPN para cada data
    all_espn = {}
    for date_str in sorted(pending_dates):
        results = fetch_espn_results(date_str)
        all_espn[date_str] = results

    # Atualiza o histórico
    total_updated = 0
    total_won = 0
    total_lost = 0
    total_void = 0

    for i, entry in enumerate(history):
        if entry.get('status') != 'PENDING':
            continue

        date_str = entry.get('date', '')
        home = entry.get('home', '')
        away = entry.get('away', '')
        selection = entry.get('selection', '')
        odd = float(entry.get('odd', 1.0))

        if not date_str or not home or not away:
            continue

        # Converte data para YYYY-MM-DD
        try:
            parts = date_str.split('/')
            dd, mm = parts
            target_dt = datetime.datetime(now.year, int(mm), int(dd))
            target_date_full = target_dt.strftime("%Y-%m-%d")
        except:
            continue

        # Verifica se temos resultados para esta data
        if target_date_full not in all_espn:
            continue

        results_for_date = all_espn[target_date_full]
        res, is_home_perspective = find_result(home, away, results_for_date)

        if res is None:
            print(f"   ⚠️ Sem resultado ESPN: {home} vs {away} ({date_str})")
            continue

        h_val = res['home_val']
        a_val = res['away_val']

        # Para jogos de futebol com perspectiva invertida (away team)
        # Verifica se os scores precisam ser invertidos
        # ESPN nos dá sempre home_val do time da chave (home_name)
        res_home_name = res.get('home_name', '').lower()
        our_home_lower = home.lower()
        our_away_lower = away.lower()

        # Determina os placares corretos (nossa perspectiva)
        h_alias = ALIASES.get(our_home_lower, our_home_lower)
        a_alias = ALIASES.get(our_away_lower, our_away_lower)

        if h_alias.lower() == res_home_name or our_home_lower == res_home_name:
            # Nossa home = ESPN home, placares corretos
            our_h = h_val
            our_a = a_val
        else:
            # Nossa home = ESPN away, inverte
            our_h = a_val
            our_a = h_val

        score_str = f"{our_h}-{our_a}"
        new_status = evaluate_selection(selection, our_h, our_a, home, away)

        if new_status == 'PENDING':
            # Jogo ainda não decidido na nossa lógica, mantém pending
            print(f"   ❓ Não resolvido: {home} vs {away} | {selection} | Placar: {score_str}")
            continue

        # Calcula lucro
        if new_status == "WON":
            profit = f"+{int((odd - 1) * 100)}%"
            badge = "✅ GREEN"
            total_won += 1
        elif new_status == "LOST":
            profit = "-100%"
            badge = "❌ RED"
            total_lost += 1
        elif new_status == "VOID":
            profit = "0% (VOID)"
            badge = "🔄 VOID"
            total_void += 1
        else:
            profit = entry.get('profit', '...')
            badge = entry.get('badge', '🤖 AI PICK')

        # Atualiza entrada
        history[i]['status'] = new_status
        history[i]['score'] = score_str
        history[i]['profit'] = profit
        history[i]['badge'] = badge
        total_updated += 1

        icon = "🟢" if new_status == "WON" else "🔴" if new_status == "LOST" else "⚪"
        print(f"   {icon} ATUALIZADO: {home} vs {away} | {selection}")
        print(f"      Placar: {score_str} | Status: {new_status} | Lucro: {profit}")

    # Salva histórico atualizado
    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"✅ ATUALIZAÇÃO CONCLUÍDA!")
    print(f"   📊 Total atualizado: {total_updated} jogos")
    print(f"   🟢 WON: {total_won}")
    print(f"   🔴 LOST: {total_lost}")
    print(f"   ⚪ VOID: {total_void}")
    print("=" * 60)


if __name__ == "__main__":
    main()
