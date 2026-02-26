# -*- coding: utf-8 -*-
"""
auto_updater.py — Atualização automática do history.json
Executa via Windows Task Scheduler todo dia às 00:30.
Busca resultados de ontem e hoje na ESPN API, avalia WON/LOST,
salva history.json e faz push automático ao GitHub.
"""

import json
import os
import sys
import requests
import logging
from datetime import datetime, timedelta, date

# ── Encoding para Windows ──────────────────────────────────────────────────────
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── Diretório base do projeto ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_PATH = os.path.join(BASE_DIR, "history.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ── Logger ────────────────────────────────────────────────────────────────────
log_file = os.path.join(LOG_DIR, "auto_updater.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("auto_updater")

# ── Ligas ESPN ────────────────────────────────────────────────────────────────
ESPN_LEAGUES = [
    ("basketball/nba",            "NBA"),
    ("soccer/bra.1",              "Brasileirao"),
    ("soccer/eng.1",              "Premier League"),
    ("soccer/esp.1",              "La Liga"),
    ("soccer/ita.1",              "Serie A"),
    ("soccer/ger.1",              "Bundesliga"),
    ("soccer/fra.1",              "Ligue 1"),
    ("soccer/eng.fa",             "FA Cup"),
    ("soccer/UEFA.CHAMPIONS",     "Champions League"),
    ("soccer/UEFA.EUROPA",        "Europa League"),
    ("soccer/esp.2",              "La Liga 2"),
    ("soccer/arg.1",              "La Liga Argentina"),
]

# ── Aliases de times ──────────────────────────────────────────────────────────
ALIASES = {
    "trail blazers": ["blazers", "portland"],
    "timberwolves":  ["wolves", "minnesota"],
    "cavaliers":     ["cavs", "cleveland"],
    "76ers":         ["sixers", "philadelphia"],
    "celtics":       ["boston"],
    "lakers":        ["los angeles lakers"],
    "clippers":      ["los angeles clippers"],
    "warriors":      ["golden state"],
    "nuggets":       ["denver"],
    "bucks":         ["milwaukee"],
    "heat":          ["miami"],
    "knicks":        ["new york knicks"],
    "nets":          ["brooklyn"],
    "thunder":       ["oklahoma"],
    "spurs":         ["san antonio"],
    "raptors":       ["toronto"],
    "grizzlies":     ["memphis"],
    "pistons":       ["detroit"],
    "hawks":         ["atlanta"],
    "wizards":       ["washington"],
    "magic":         ["orlando"],
    "bulls":         ["chicago"],
    "hornets":       ["charlotte"],
    "pelicans":      ["new orleans"],
    "suns":          ["phoenix"],
    "mavericks":     ["dallas", "mavs"],
    "rockets":       ["houston"],
    "kings":         ["sacramento"],
    "jazz":          ["utah"],
    "wolves":        ["wolverhampton"],
    "atletico":      ["atletico-mg", "atletico mg", "atletico mineiro"],
    "sao paulo":     ["tricolor"],
    "gremio":        ["gre-nal"],
    "flamengo":      ["fla"],
    "man city":      ["manchester city"],
    "man utd":       ["manchester united"],
    "red bull bragantino": ["bragantino", "rbb"],
    "athletico":     ["athletico paranaense", "athletico-pr", "cap"],
}


def fuzzy(name1: str, name2: str) -> bool:
    """Verifica se dois nomes de times correspondem (fuzzy match)."""
    a = name1.lower().strip()
    b = name2.lower().strip()
    if a in b or b in a:
        return True
    # Verifica aliases
    for key, vals in ALIASES.items():
        names = [key] + vals
        a_in = any(n in a or a in n for n in names)
        b_in = any(n in b or b in n for n in names)
        if a_in and b_in:
            return True
    return False


def fetch_espn(date_obj: date) -> list:
    """Busca todos os jogos finalizados de uma data na ESPN API."""
    date_str = date_obj.strftime("%Y%m%d")
    games = []
    for path, league in ESPN_LEAGUES:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{path}/scoreboard?dates={date_str}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                continue
            for ev in r.json().get("events", []):
                status = ev.get("status", {}).get("type", {})
                state = status.get("state", "")
                completed = status.get("completed", False)
                if state != "post" and not completed:
                    continue  # só jogos finalizados
                comps = ev.get("competitions", [{}])[0]
                teams = comps.get("competitors", [])
                if len(teams) < 2:
                    continue
                h = next((t for t in teams if t.get("homeAway") == "home"), teams[0])
                a = next((t for t in teams if t.get("homeAway") == "away"), teams[1])
                h_score = h.get("score", "0")
                a_score = a.get("score", "0")
                games.append({
                    "home":     h["team"]["displayName"],
                    "away":     a["team"]["displayName"],
                    "hs":       int(h_score) if str(h_score).isdigit() else 0,
                    "as":       int(a_score) if str(a_score).isdigit() else 0,
                    "league":   league,
                    "date_obj": date_obj,
                })
        except Exception as e:
            log.warning(f"ESPN {league} {date_str}: {e}")
    return games


def find_game(pick: dict, games: list):
    """Encontra o jogo correspondente ao pick na lista de jogos."""
    ph = pick.get("home", pick.get("team1", ""))
    pa = pick.get("away", pick.get("team2", ""))
    for g in games:
        # Tenta match normal
        if fuzzy(ph, g["home"]) and fuzzy(pa, g["away"]):
            return g, False  # (game, invertido)
        # Tenta match invertido (pick home = ESPN away)
        if fuzzy(ph, g["away"]) and fuzzy(pa, g["home"]):
            return g, True
    return None, False


def evaluate(pick: dict, hs: int, as_: int) -> str:
    """Avalia WON/LOST baseado no mercado e resultado."""
    market = pick.get("market", "").upper()
    sel    = pick.get("selection", "").upper()
    ph     = pick.get("home", pick.get("team1", "")).upper()
    pa     = pick.get("away", pick.get("team2", "")).upper()

    # Vencedor / Moneyline
    if "VENCEDOR" in market or "ML" in market or "MONEYLINE" in market:
        sel_clean = sel.replace("VENCE", "").strip()
        home_picked = (ph in sel_clean or sel_clean in ph or
                       any(a in sel_clean or sel_clean in a
                           for a in [ph.split()[0]] if len(ph.split()) > 0))
        away_picked = not home_picked and (pa in sel_clean or sel_clean in pa or
                       any(a in sel_clean or sel_clean in a
                           for a in [pa.split()[0]] if len(pa.split()) > 0))
        if home_picked:
            return "WON" if hs > as_ else "LOST"
        if away_picked:
            return "WON" if as_ > hs else "LOST"
        # fallback: tenta pelo time mais curto
        pick_team = sel_clean.split(" ")[0]
        if fuzzy(pick_team, pick.get("home", "")):
            return "WON" if hs > as_ else "LOST"
        if fuzzy(pick_team, pick.get("away", "")):
            return "WON" if as_ > hs else "LOST"

    # Dupla Chance
    elif "DUPLA CHANCE" in market or "OU EMPATE" in sel:
        is_draw = (hs == as_)
        parts   = sel.replace(" OU EMPATE", "").strip()
        home_match = fuzzy(parts, pick.get("home", ""))
        away_match = fuzzy(parts, pick.get("away", ""))
        if home_match:
            if "EMPATE" in sel:
                return "WON" if (hs >= as_) else "LOST"
            return "WON" if hs > as_ else "LOST"
        if away_match:
            if "EMPATE" in sel:
                return "WON" if (as_ >= hs) else "LOST"
            return "WON" if as_ > hs else "LOST"

    # Over / Under
    elif "OVER" in sel or "UNDER" in sel:
        try:
            nums = [float(x) for x in sel.replace(",", ".").split() if x.replace(".", "").isdigit()]
            if not nums:
                import re
                nums = [float(x) for x in re.findall(r"\d+\.?\d*", sel)]
            line = nums[0] if nums else None
            if line:
                total = hs + as_
                if "OVER" in sel:
                    return "WON" if total > line else "LOST"
                else:
                    return "WON" if total < line else "LOST"
        except Exception:
            pass

    return "PENDING"


def run():
    log.info("=" * 60)
    log.info("Iniciando auto_updater")

    # Carrega history.json
    if not os.path.exists(HISTORY_PATH):
        log.error(f"history.json nao encontrado em {HISTORY_PATH}")
        return

    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    picks = data if isinstance(data, list) else data.get("picks", data.get("history", []))

    pending = [p for p in picks
               if str(p.get("status", "")).upper() in ["PENDING", "", "NONE"]
               or not p.get("status")]
    log.info(f"Picks pendentes: {len(pending)}")

    if not pending:
        log.info("Nenhum pick pendente. Nada a fazer.")
        return

    # Busca jogos de hoje e ontem
    today     = date.today()
    yesterday = today - timedelta(days=1)
    log.info(f"Buscando ESPN: {yesterday} e {today}")

    games_today     = fetch_espn(today)
    games_yesterday = fetch_espn(yesterday)
    all_games = games_today + games_yesterday

    log.info(f"Jogos finalizados encontrados: {len(all_games)}")

    # Atualiza picks
    won = 0; lost = 0; still_pending = 0; updated = 0

    for p in pending:
        game, invertido = find_game(p, all_games)
        if not game:
            still_pending += 1
            continue

        if invertido:
            hs, as_ = game["as"], game["hs"]
        else:
            hs, as_ = game["hs"], game["as"]

        result = evaluate(p, hs, as_)
        ph = p.get("home", p.get("team1", "?"))
        pa = p.get("away", p.get("team2", "?"))

        if result in ("WON", "LOST"):
            p["status"] = result
            p["score"]  = f"{hs}-{as_}"
            updated += 1
            if result == "WON":
                won += 1
                log.info(f"  [WON ] {ph} {hs}x{as_} {pa} | {p.get('market','?')}: {p.get('selection','?')}")
            else:
                lost += 1
                log.info(f"  [LOST] {ph} {hs}x{as_} {pa} | {p.get('market','?')}: {p.get('selection','?')}")
        else:
            still_pending += 1
            log.info(f"  [PEND] {ph} vs {pa} — resultado ainda indefinido")

    log.info(f"Atualizados: {updated} | WON: {won} | LOST: {lost} | Ainda pendente: {still_pending}")

    # Salva history.json
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(picks if isinstance(data, list) else data, f, ensure_ascii=False, indent=2)
    log.info("history.json salvo.")

    # Stats finais
    all_won  = sum(1 for p in picks if str(p.get("status","")).upper() in ["WON","GREEN","WIN"])
    all_lost = sum(1 for p in picks if str(p.get("status","")).upper() in ["LOST","RED","LOSS"])
    all_pend = sum(1 for p in picks if str(p.get("status","")).upper() in ["PENDING","","NONE"] or not p.get("status"))
    rate = all_won / (all_won + all_lost) * 100 if (all_won + all_lost) > 0 else 0
    log.info(f"GREEN RATE: {rate:.1f}% | WON:{all_won} LOST:{all_lost} PEND:{all_pend}")

    # Push ao GitHub
    if updated > 0:
        try:
            sys.path.insert(0, BASE_DIR)
            from git_autopush import autopush
            now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            msg = f"auto: atualiza history [{now_str}] | WON:{won} LOST:{lost} | Green:{rate:.1f}%"
            ok = autopush(msg)
            if ok:
                log.info("Push ao GitHub: OK")
            else:
                log.warning("Push ao GitHub: FALHOU (verifique credenciais)")
        except Exception as e:
            log.error(f"Erro no autopush: {e}")
    else:
        log.info("Nenhuma mudança — push ignorado.")

    log.info("auto_updater finalizado.")


if __name__ == "__main__":
    run()
