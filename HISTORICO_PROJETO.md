# 📊 BOT PROBABILITY — Histórico Completo do Projeto

**Última Atualização:** 26 de Fevereiro de 2026, 15:39  
**Status:** ✅ Sistema Operacional em Produção  
**Versão Atual:** Neural Cortex 6.0 / Vanguarda Neural

---

## 🎯 VISÃO GERAL

**Bot Probability** é uma plataforma de análise esportiva com IA para geração de picks esportivos premium (NBA + Futebol). O sistema busca dados reais em tempo real via ESPN API e The Odds API, gera picks automaticamente com Monte Carlo e Poisson, e exibe tudo em um dashboard web premium com glassmorphism.

### Missão
> Atingir **80%+ de Green Rate** com um sistema de IA que aprende continuamente dos resultados passados.

---

## 🏗️ ARQUITETURA ATUAL

### Stack Tecnológico

| Camada | Tecnologia |
|---|---|
| Backend | Flask (Python) |
| Banco de Dados Local | SQLite (`database.db`) + `history.json` |
| Banco de Dados Nuvem | Supabase (REST API) |
| Frontend | HTML5 + TailwindCSS + Glassmorphism |
| IA | Monte Carlo (NBA) + Poisson (Futebol) + 42 módulos |
| Dados | ESPN API + The Odds API + Scores365 |
| OCR | Tesseract.js |
| Deploy | Railway (via Procfile + Gunicorn) |

### Arquivos do Projeto (Estado Atual)

```
d:\BOT PROBABILITY\
├── app.py                    # Flask: rotas, autenticação, API
├── ai_engine.py              # Motor IA: 42+ módulos, Monte Carlo, Poisson (~68KB)
├── data_fetcher.py           # Fetcher de jogos/odds/trebles (~45KB)
├── auto_picks.py             # Gerador automático de picks diários (~75KB)
├── specialized_modules.py    # 14 módulos táticos especializados
├── knowledge_base.py         # Elencos, técnicos, fases dos times
├── espn_api.py               # Integração ESPN API
├── odds_api.py               # Integração The Odds API
├── scores365.py              # Scraper de resultados (~31KB)
├── result_checker.py         # Verificação automática de resultados
├── self_learning.py          # Sistema de aprendizado contínuo (~30KB)
├── turbo_fetcher.py          # Fetcher otimizado de alta velocidade (~25KB)
├── real_news.py              # Busca de notícias em inglês
├── update_history_v3.py      # Atualização do histórico v3
├── update_all_today.py       # Script de atualização diária completa
├── force_update_today.py     # Forçar atualização dos resultados de hoje
├── supabase_client.py        # Cliente REST Supabase
├── admin.py                  # Painel admin CLI
├── payment_system.py         # Sistema de pagamentos
├── betano_scraper.py         # Scraper Betano
├── history.json              # Histórico de picks (~217KB)
├── history_trebles.json      # Histórico de trebles/múltiplas (~9KB)
├── learning_state.json       # Estado do aprendizado (~54KB)
├── database.db               # SQLite: usuários e sessões
├── AUDIT_REPORT.md           # Auditoria técnica completa
├── DEPLOY.md                 # Instruções de deploy
├── AGENTS.md                 # Instruções para agentes IA
├── requirements.txt          # Dependências Python
├── Procfile                  # Config Railway/Heroku
├── runtime.txt               # Versão Python para deploy
└── templates/
    ├── index.html            # Dashboard principal (~99KB)
    ├── login.html            # Tela de login
    ├── admin.html            # Painel admin web
    ├── subscribe.html        # Página de assinatura
    ├── payment_success.html  # Pós-pagamento sucesso
    ├── payment_failure.html  # Pós-pagamento falha
    └── payment_pending.html  # Pagamento pendente
```

---

## 📅 LINHA DO TEMPO — EVOLUÇÃO DO PROJETO

### 🟦 FASE 1 — Fundação (05–06/02/2026)
- Criação do projeto base Flask
- Frontend premium com dark mode + glassmorphism
- Sistema de picks hardcoded por data
- OCR integrado (Tesseract.js) para análise de bilhetes
- Sistema de scout técnico (Tactical Dossier)
- Trust Score Gauge (gauge SVG animado)

### 🟦 FASE 2 — IA & Backend (07–11/02/2026)
- **Motor de IA:** 42 módulos incluindo Monte Carlo, Poisson, Markov Chain
- **Supabase:** Integração com banco em nuvem (260 times + 1500+ jogadores)
- **Self-Calibration Engine:** Loop de feedback que ajusta probabilidades
- **EV Gate:** Rejeita tips sem valor matemático (prob > implied + 5%)
- **Emotional Weight:** Morale baseado em resultados recentes do histórico
- **Knowledge Base:** `knowledge_base.py` com elencos e técnicos
- **Auditoria:** `AUDIT_REPORT.md` gerado — 78% de accuracy em 41 tips
- Sistema de logos com fallback em 3 níveis (ESPN CDN → Wikipedia → Shield)
- **Login system** com sessão Flask + hash werkzeug
- Módulos especializados: corners, goals, handicaps, NBA totals, sharp money

### 🟦 FASE 3 — Mobile & Automação (11–17/02/2026)
- **Mobile-First:** Interface adaptativa 9:16 com bottom navigation bar
- **PWA-like:** Detecção de dispositivo móvel + layout nativo
- **`auto_picks.py`:** Gerador automático de picks e trebles (elimina hardcode manual)
  - Busca jogos via ESPN API automaticamente
  - Monte Carlo (NBA) + Poisson (Futebol) dinâmico
  - EV calculado por pick, trebles auto-construídos
- **`real_news.py`:** Busca notícias em inglês para análise contextual
- **`history_trebles.json`:** Persistência de trebles gerados
- **`data_fetcher.py`:** Leitura do `history_trebles.json` para gerenciamento de status

### 🟦 FASE 4 — Admin, Velocidade & Correções (17–19/02/2026)
- **Admin Panel Web:** `templates/admin.html` + `admin.py` + rota `/admin`
- **Turbo Fetcher:** `turbo_fetcher.py` para alta velocidade de fetch (~25KB)
- **`update_history_v3.py`:** Script de atualização do histórico v3
- **`scores365.py`:** Scraper completo de resultados (~31KB)
- **ESPN API expandida:** Endpoints para Champions League e outras ligas europeias
- **`update_history_smart.py`:** Busca dinâmica da data de ontem (v anterior)
- Fix: Date dinâmica no script de atualização
- Fix: Deduplicação de picks no `history.json`

### 🟦 FASE 5 — Self-Learning & Acurácia 80% (20–21/02/2026)
- **`self_learning.py`:** Sistema de aprendizado contínuo de 30 dias (~30KB)
  - Backfill de dados históricos de 30 dias
  - Detecção de mercados voláteis e "times tóxicos"
  - Filtros cirúrgicos para aumentar precision
- **`learning_state.json`:** Estado do aprendizado (~54KB de dados acumulados)
- **Meta:** Atingir 80%+ de Green Rate
- Atualização de status Green/Red no histórico

### 🟦 FASE 6 — Dados Reais & Segurança (24–25/02/2026)
- **Dashboard com dados reais:** ESPN API para NBA + Premier League (25/02/2026)
  - Substituição de dados placeholder por dados live
  - Jogos verificados do dia atual
- **Fix crítico de segurança:**
  - Admin backdoor removido
  - Senhas hardcoded eliminadas
  - Variáveis indefinidas corrigidas
  - `secret_key` movida para `.env`
  - Instabilidade de sessão resolvida
- **Sistema de pagamentos:** `payment_system.py` + páginas de sucesso/falha/pendente
- **Página de assinatura:** `templates/subscribe.html`
- **Deploy:** Configuração Railway com `Procfile` e `runtime.txt`

---

## 🔥 FUNCIONALIDADES PRINCIPAIS (ESTADO ATUAL)

### 1. Geração Automática de Picks (`auto_picks.py`)
- Busca jogos do dia via ESPN API automaticamente
- Aplica Monte Carlo (NBA) e Poisson (Futebol) para cada jogo
- Calcula EV (Expected Value) e filtra picks negativos
- Gera trebles automáticos com os 3 melhores picks
- Salva em `history.json` e `history_trebles.json`

### 2. Motor de IA (`ai_engine.py` — 68KB)
- **42+ módulos neurais** incluindo:
  - `calculate_monte_carlo_simulation` — 5000 iterações com numpy
  - `calculate_poisson_probability` — Cálculo matemático puro para futebol
  - `neural_cortex_omega` — Pipeline principal de análise (375 linhas)
  - `self_calibration_engine` — Ajusta pesos baseado no histórico real
  - `trap_hunter_funnel` — Identifica armadilhas de mercado
  - `golden_path_optimizer` — Compara mercados e escolhe o melhor
  - `detect_blood_in_water` — Times em queda livre
  - `calculate_nba_b2b_impact` — Impacto de back-to-back

### 3. Sistema de História (`history.json` — 217KB)
- Registro completo de todos os picks
- Status automático: `WON` / `LOST` / `PENDING`
- Atualização via ESPN API (placar final)
- Deduplicação implementada (sem picks duplicados)

### 4. Self-Learning de 30 Dias (`self_learning.py`)
- Analisa resultados dos últimos 30 dias
- Identifica padrões de vitória por liga/mercado
- Ajusta pesos dos filtros automaticamente
- Estado persistido em `learning_state.json`

### 5. Frontend Premium (`templates/index.html` — 99KB)
- Dark mode com glassmorphism
- Cards de jogos com logos (ESPN CDN)
- Comparação de odds entre 4 casas (Betano, Bet365, Pinnacle, Betfair)
- Sistema de badges Sniper (#1, #2, #3)
- Modal de Dossiê Tático
- Trust Score Gauge animado (SVG)
- Share/download de cards (html2canvas)
- Mobile-first com bottom navigation

### 6. Sistema de Autenticação & Pagamentos
- Login com Flask-session + hash werkzeug
- `secret_key` fixa via variável de ambiente
- Planos de assinatura (`subscribe.html`)
- Integração de pagamentos (`payment_system.py`)
- Admin panel restrito (`/admin`)

---

## 📊 PERFORMANCE DO SISTEMA

| Métrica | Valor |
|---|---|
| **Green Rate Registrado** | ~78% (histórico auditado em 11/02) |
| **Meta Atual** | 80%+ |
| **Total de Picks** | 100+ (history.json ~217KB) |
| **Ligas Cobertas** | NBA, Premier League, Champions League, La Liga, Serie A, Brasileirão |
| **Módulos de IA** | 42+ |
| **Linhas de Código** | ~7.000+ |

---

## 🔌 API ENDPOINTS

| Endpoint | Método | Função |
|---|---|---|
| `/` | GET | Dashboard principal |
| `/login` | GET/POST | Autenticação |
| `/subscribe` | GET | Página de assinatura |
| `/admin` | GET | Painel admin (restrito) |
| `/api/games?date=YYYY-MM-DD` | GET | Picks do dia |
| `/api/history` | GET | Histórico completo |
| `/api/trebles` | GET | Histórico de trebles |
| `/api/analyze?id=<id>` | GET | Análise de jogo |
| `/api/analyze_deep` | POST | Análise via OCR |
| `/api/analyze_multiple` | POST | Validação de múltiplas |
| `/api/sync_history` | POST | Sincronizar resultados |
| `/api/payment/*` | POST | Webhooks de pagamento |

---

## 🐛 PROBLEMAS CONHECIDOS / LIMITAÇÕES

| # | Problema | Gravidade | Status |
|---|---|---|---|
| 1 | `data_fetcher.py` monolito (1600+ linhas em 1 função) | Alta | Pendente refactor |
| 2 | Vários módulos de IA retornam dados simulados | Média | Documentado |
| 3 | Knowledge base estática (elencos não auto-atualizam) | Média | Backlog |
| 4 | OCR accuracy depende da qualidade da imagem | Baixa | Design limitation |
| 5 | Supabase subutilizado (opera principalmente local) | Baixa | Backlog |

---

## 🚀 ROADMAP — PRÓXIMOS PASSOS

### 🔥 Alta Prioridade
- [ ] Conectar `self_learning.py` ao pipeline principal de geração de picks
- [ ] Refatorar `data_fetcher.py` em módulos menores
- [ ] Dashboard de performance admin (winrate por liga em tempo real)

### 📌 Médio Prazo
- [ ] Self-Correction automático dos módulos de IA baseado em dados acumulados
- [ ] Notificações Telegram quando picks Sniper são gerados
- [ ] Exportação de relatórios em PDF
- [ ] Implementar módulos de IA que hoje são simulados (weather, travel, lineup)

### 💡 Longo Prazo
- [ ] Expansão mobile (PWA completo com offline mode)
- [ ] Integração com mais casas de apostas via scraper
- [ ] Inteligência de arbitragem cross-house

---

## 🚀 COMO EXECUTAR

```bash
# Instalar dependências
pip install -r requirements.txt

# Ativar variáveis de ambiente (.env)
# (Preencher FLASK_SECRET_KEY, THE_ODDS_API_KEY, SUPABASE_URL, SUPABASE_KEY)

# Iniciar servidor
python app.py
# → http://localhost:5000

# Gerar picks do dia
python auto_picks.py

# Atualizar resultados de hoje
python update_all_today.py

# Forçar atualização de resultados
python force_update_today.py
```

---

## 👥 LOG DE CONVERSAS (HISTÓRICO COMPLETO)

| Data | Conversa ID | Tópico |
|---|---|---|
| 05–06/02 | `a7c154af` | Adding Login System (PDKHOT) |
| 05–06/02 | `2d24eb04` | Creating PDKHOT Website |
| 05–06/02 | `0620b7bb` | Install Agent Skills |
| 06/02 | `28b39905` | Resume Bot Probability Project |
| 09–10/02 | `713a3b05` | Updating Game Results Accuracy (Heat → Red) |
| 10/02 | `ec52afd4` | Updating Game Results (Everton, Chelsea) |
| 10/02 | `63ceabe4` | Mobile App Experience (9:16, bottom nav) |
| 10/02 | `c9afa038` | Modare Website Development |
| 11/02 | `f93f5b72` | Automating Daily Picks (auto_picks.py criado) |
| 11/02 | `e4bcc364` | Refining News Fetching (inglês) |
| 12/02 | `09298faf` | Updating Game History Accuracy |
| 17/02 | `4fd10349` | Updating Daily Picks |
| 17–18/02 | `73ae1146` | Optimizing System Speed (turbo_fetcher) |
| 18/02 | `d29669cb` | Admin Panel Deployment Fix |
| 19/02 | `a467dabf` | Implementing Treble Persistence |
| 19/02 | `35c0a708` | Updating and Verifying History |
| 19/02 | `8b70cd3f` | Updating Game History (ESPN API para Champions) |
| 20/02 | `e717f4aa` | Update Green and Red History |
| 20–21/02 | `9eec8bbe` | 80% Green Evolution (self_learning.py) |
| 24/02 | `d634c440` | Updating Last Three Days |
| 24/02 | `81e0a9d3` | Checking Website Readiness For Sales |
| 25/02 | `f5590734` | Updating Website Picks |
| 25/02 | `7cdea81e` | Populating Dashboard with Real Data (ESPN live) |
| 25/02 | `ef303931` | Fixing Critical Bugs (segurança, backdoor, sessão) |

---

**Documento atualizado em:** 26/02/2026 às 15:39  
**Versão:** 3.0  
**Autor:** Sistema de Documentação Automática
