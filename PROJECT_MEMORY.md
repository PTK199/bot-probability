# MEMÓRIA DO PROJETO — BOT PROBABILITY (Neural Cortex 6.0 / Vanguarda Neural)

**Atualizado:** 26/02/2026 às 15:39

---

## O QUE É ESSE PROJETO?

Plataforma de análise esportiva com IA para geração de picks premium (NBA + Futebol).  
Arquitetura: **Cérebro Local (Python/Flask)** + dados reais via **ESPN API + The Odds API** + memória em **Supabase Cloud**.

---

## ESTADO ATUAL (26/02/2026)

- **Status Geral:** ✅ Operacional, pronto para vendas
- **Deploy:** Railway (Procfile + Gunicorn configurados)
- **Green Rate:** ~78% auditado (meta: 80%+)
- **Sistema de Picks:** Automático via `auto_picks.py` (sem hardcode manual)
- **Pagamentos:** `payment_system.py` + páginas de resultado integradas
- **Login/Auth:** Flask-session + hash werkzeug, `secret_key` via `.env`
- **Admin Panel:** `/admin` protegido, acessível via `admin.html`

---

## ARQUITETURA DOS ARQUIVOS-CHAVE

```
app.py              → Flask: rotas, autenticação, 16KB
ai_engine.py        → Motor IA: 42+ módulos, 68KB
auto_picks.py       → Gerador de picks diários, 75KB
data_fetcher.py     → Dados de jogos/odds/trebles, 45KB
self_learning.py    → Aprendizado de 30 dias, 30KB
turbo_fetcher.py    → Fetcher otimizado, 25KB
scores365.py        → Scraper de resultados, 31KB
result_checker.py   → Verificação automática ESPN
espn_api.py         → ESPN API: NBA, PL, CL, La Liga...
specialized_modules.py → 14 módulos táticos
knowledge_base.py   → Elencos e técnicos
history.json        → 217KB de histórico de picks
learning_state.json → 54KB de estado de aprendizado
database.db         → SQLite: usuários
templates/          → 7 templates HTML
```

---

## ÚLTIMAS IMPLEMENTAÇÕES (FEV/2026)

### 🔴 Correções Críticas (25/02)
- [x] Admin backdoor removido
- [x] Senhas hardcoded eliminadas
- [x] `secret_key` movida para `.env`
- [x] Variáveis indefinidas corrigidas
- [x] Instabilidade de sessão resolvida
- [x] Deduplicação de picks no `history.json`

### 🟢 Dados Reais no Dashboard (25/02)
- [x] ESPN API integrada ao `index.html` para jogos live do dia
- [x] NBA + Premier League com dados reais do dia

### 🟢 Sistema de Pagamentos (24/02)
- [x] `payment_system.py` criado
- [x] Pages: `payment_success.html`, `payment_failure.html`, `payment_pending.html`
- [x] `subscribe.html` com planos de assinatura

### 🟢 80% Green Evolution (20–21/02)
- [x] `self_learning.py` — sistema de aprendizado 30 dias
- [x] Backfill histórico, filtros cirúrgicos, detecção de times tóxicos
- [x] `learning_state.json` com dados acumulados

### 🟢 Admin Panel (18/02)
- [x] `templates/admin.html` + `admin.py` + rota `/admin`
- [x] Deploy fix para acesso externo

### 🟢 Automação de Picks (11/02)
- [x] `auto_picks.py` — elimina hardcode manual de picks por data
- [x] `history_trebles.json` — persistência de trebles
- [x] Mobile-first: 9:16 + bottom navigation

---

## PRÓXIMOS PASSOS

1. **Self-Correction:** Conectar `self_learning.py` ao pipeline de geração automática
2. **Dashboard Admin:** Winrate por liga em tempo real
3. **Refactor:** Quebrar `data_fetcher.py` em módulos menores
4. **Telegram Bot:** Notificações automáticas de picks Sniper
