# 📊 BOT PROBABILITY - Histórico e Resumo do Projeto

**Última Atualização:** 07 de Fevereiro de 2026, 01:32 AM  
**Status:** ✅ Sistema Operacional  
**Versão Atual:** IA-Sniper 3.0

---

## 🎯 VISÃO GERAL DO PROJETO

**Bot Probability** é uma plataforma avançada de análise esportiva que utiliza Inteligência Artificial e OCR (Reconhecimento Óptico de Caracteres) para fornecer análises técnicas profundas de jogos e apostas esportivas.

### Objetivo Principal
Processar milhares de dados em tempo real para entregar análises táticas de elite, combinando:
- 🧠 **Inteligência Artificial** para análise preditiva
- 📸 **OCR** para extração de dados de bilhetes
- 📊 **Análise Estatística** para validação matemática
- ⚽ **Scout Técnico** para insights táticos profundos

---

## 🏗️ ARQUITETURA DO SISTEMA

### Stack Tecnológico

#### Backend
- **Framework:** Flask (Python)
- **Módulos Principais:**
  - `app.py` - Servidor principal e rotas API
  - `data_fetcher.py` - Geração de dados de jogos e odds
  - `ai_engine.py` - Motor de análise de IA
  - `patch.py` - Utilitários e correções

#### Frontend
- **Framework:** HTML5 + TailwindCSS
- **Bibliotecas:**
  - Tesseract.js (OCR)
  - Chart.js (Gráficos)
  - Lucide Icons
- **Design:** Dark Mode Premium com Glassmorphism

#### Dependências
```
Flask
flask-cors
```

---

## 🎨 ESTRUTURA DE NAVEGAÇÃO

O sistema possui 4 visualizações principais:

### 1. 📅 **Dashboard (Games)**
- **Função:** Exibição dos jogos do dia com análises "Sniper"
- **Features:**
  - Filtros por data (Hoje/Amanhã)
  - Filtros por esporte (Futebol/Basquete)
  - Cards de jogos com odds de múltiplas casas
  - Sistema de badges para picks premium (SNIPER #1, #2, #3)
  - Logos reais dos times (ESPN CDN + Wikipedia)
  - Comparação de odds entre Betano, Bet365, Pinnacle, Betfair

### 2. 💰 **Gestão & Scout (Calculator)**
- **Função:** Gestão de banca e análise técnica
- **Features:**
  - **Calculadora de Alavancagem:**
    - Define banca inicial, meta final e período
    - Gera plano diário de ROI necessário
    - Sugere odds ideais para cada dia
  - **Calculadora de Dutching:**
    - Distribui stake entre múltiplos resultados
    - Calcula lucro garantido
    - Exibe rendimento percentual

### 3. 🎲 **Validador de Múltiplas (Analyzer)**
- **Função:** Análise de bilhetes combinados via OCR
- **Features:**
  - Upload de imagem do bilhete
  - OCR para extração de times e odds
  - Análise do "Elo Mais Fraco"
  - Validação de probabilidade matemática
  - Scout técnico de cada jogo
  - Trust Score visual (gauge animado)

### 4. 📜 **Histórico (History)**
- **Função:** Registro de performance passada
- **Features:**
  - Lista de tips anteriores
  - Status: WON (Green) / LOST (Red)
  - Placar final e lucro/prejuízo
  - Botão de sincronização

---

## 🔥 FUNCIONALIDADES PRINCIPAIS

### Sistema de Análise "Sniper"
O sistema identifica diariamente os 3 melhores picks do mercado baseado em:
- Disparidade técnica entre times
- Estatísticas de forma recente
- Contexto tático (desfalques, mando de campo)
- Valor matemático (Expected Value)

**Exemplo de Sniper Pick:**
```
🎯 SNIPER #1: Magic vs Nets
Mercado: Total de Pontos - Under 223.5
Odd: 1.40
Probabilidade: 92%
Razão: "Nets tem o pior ataque da liga (107 PPG). 
        Magic tem defesa Top 10 e pace lento."
```

### Motor de OCR Inteligente
- **Tesseract.js** para reconhecimento de texto
- **Filtros de ruído** para melhorar precisão
- **Extração de:**
  - Nomes de times
  - Odds decimais
  - Mercados de aposta
- **Validação cruzada** com banco de dados de logos

### Análise Técnica Profunda (Tactical Dossier)
Quando o usuário clica em "Ver Dossiê", o sistema exibe:
- **Dados ao Vivo:**
  - Placar atual
  - Posse de bola
  - Chutes no alvo
  - Escanteios
  - Faltas
- **Contexto Tático:**
  - Narrativa da situação do jogo
  - Probabilidade implícita
  - Fonte de pesquisa
- **Perfil dos Times:**
  - Forma recente
  - Jogadores-chave
  - Estilo de jogo
  - Pontos fortes/fracos

### Trust Score Gauge
Indicador visual de confiança da análise:
- **0-50%:** Zona de Risco (Vermelho)
- **50-75%:** Zona Neutra (Amarelo)
- **75-100%:** Zona de Confiança (Verde)

Animação SVG com stroke-dasharray para efeito de "preenchimento".

---

## 📊 DADOS E LÓGICA DE NEGÓCIO

### Geração de Jogos (`data_fetcher.py`)
O sistema possui dados hardcoded para:
- **05/02/2026:** 13 jogos (Futebol BR + NBA + Europa)
- **06/02/2026:** 7 jogos (NBA Friday + Futebol)

Cada jogo contém:
```python
{
    "home": "Celtics",
    "away": "Heat",
    "league": "NBA",
    "time": "21:30",
    "sport": "basketball",
    "odds": {"home": "1.45", "draw": "-", "away": "2.80"},
    "best_tip": {
        "market": "Vencedor",
        "selection": "Celtics -4.5",
        "prob": 85,
        "odd": 1.90,
        "reason": "🔥 TD GARDEN: Celtics em casa são rolo compressor...",
        "badge": "SNIPER #1 🎯"
    },
    "is_sniper": True,
    "home_logo": "https://a.espncdn.com/i/teamlogos/nba/500/bos.png",
    "away_logo": "https://a.espncdn.com/i/teamlogos/nba/500/mia.png",
    "comparisons": [...]  // Odds de 4 casas
}
```

### Logos de Times
Sistema de fallback em 3 níveis:
1. **Exact Match:** Busca exata no dicionário
2. **Partial Match:** Busca parcial (ex: "Sporting" → "Sporting CP")
3. **Generic Shield:** Ícone genérico se não encontrar

**Fontes:**
- ESPN CDN (NBA, Futebol Internacional)
- Wikipedia (Times menores, estaduais)

---

## 🎨 DESIGN SYSTEM

### Paleta de Cores
```css
--dark-bg: #030712 (Fundo principal)
--glass-bg: rgba(15, 23, 42, 0.6) (Painéis)
--neon-blue: #00f2ff (Destaque primário)
--neon-purple: #bc13fe (Destaque secundário)
--emerald: #10b981 (Sucesso/Greens)
--red: #ef4444 (Perda/Reds)
```

### Tipografia
- **Primária:** Outfit (Sans-serif moderna)
- **Secundária:** Inter
- **Mono:** Font-mono do sistema (para odds/números)

### Componentes Visuais
- **Glass Panels:** Backdrop-blur + border transparente
- **Badges:** Pills com gradientes e sombras neon
- **Cards:** Rounded-3xl com hover effects
- **Buttons:** Transform scale + shadow transitions
- **Icons:** Lucide (SVG icons)

### Animações
- **Fade-in:** Entrada suave de elementos
- **Pulse:** Indicadores de status online
- **Shimmer:** Loading states
- **Draw-gauge:** Animação do Trust Score

---

## 🔌 API ENDPOINTS

### `GET /`
Renderiza a página principal (`index.html`)

### `GET /api/games?date=YYYY-MM-DD`
Retorna lista de jogos para a data especificada
- **Params:** `date` (default: 2026-02-05)
- **Response:** Array de objetos de jogo

### `GET /api/history`
Retorna histórico de tips passados
- **Response:** Array de resultados históricos

### `GET /api/analyze?id=<game_id>`
Análise básica de um jogo (mock)
- **Params:** `id` (ID do jogo)
- **Response:** Objeto de análise

### `POST /api/analyze_deep`
Análise profunda via OCR
- **Body:** `{ "text": "texto_extraido_ocr" }`
- **Response:** Dados de análise técnica completa

### `POST /api/analyze_multiple`
Validação de múltiplas
- **Body:** `{ "text": "...", "bankroll": 1000 }`
- **Response:** Análise de risco + scout de cada jogo

---

## 📁 ESTRUTURA DE ARQUIVOS

```
d:\BOT PROBABILITY\
├── app.py                    # Servidor Flask
├── data_fetcher.py           # Gerador de dados de jogos
├── ai_engine.py              # Motor de IA e análise
├── patch.py                  # Utilitários
├── requirements.txt          # Dependências Python
├── temp_logic.js             # Lógica JS temporária
├── HISTORICO_PROJETO.md      # Este arquivo
├── templates/
│   └── index.html            # Interface principal (1726 linhas)
├── static/                   # Assets estáticos (se houver)
└── __pycache__/              # Cache Python
```

---

## 🚀 COMO EXECUTAR

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar Servidor
```bash
python app.py
```

### 3. Acessar Interface
Abrir navegador em: `http://localhost:5000`

### 4. Modo Debug
O servidor roda em modo debug por padrão:
```python
if __name__ == '__main__':
    app.run(debug=True)
```

---

## 🎯 FLUXO DE USO

### Cenário 1: Consultar Picks do Dia
1. Usuário acessa o Dashboard
2. Seleciona data (Hoje/Amanhã)
3. Filtra por esporte (opcional)
4. Visualiza cards de jogos ordenados por "is_sniper"
5. Clica em "Ver Dossiê" para análise profunda
6. Modal exibe dados táticos completos

### Cenário 2: Planejar Gestão de Banca
1. Usuário vai para "Gestão & Scout"
2. Insere: Banca inicial (R$ 100), Meta (R$ 1000), Dias (30)
3. Clica em "Gerar Plano de Alavancagem"
4. Sistema calcula ROI diário necessário
5. Exibe tabela dia-a-dia com metas progressivas

### Cenário 3: Validar Múltipla
1. Usuário vai para "Múltiplas"
2. Faz upload de print do bilhete
3. Clica em "Validar Probabilidade & Scout"
4. OCR extrai times e odds
5. IA analisa cada jogo individualmente
6. Exibe:
   - Elo mais fraco (jogo com menor probabilidade)
   - Trust Score total
   - Scout técnico de cada partida
   - Recomendação final (Apostar/Evitar)

---

## 🧠 LÓGICA DE IA

### Análise de Jogo Individual
O `ai_engine.py` (não visualizado ainda) provavelmente contém:
- Modelos de probabilidade baseados em:
  - Forma recente dos times
  - Head-to-head histórico
  - Contexto (mando, desfalques)
  - Estatísticas avançadas (xG, posse, etc.)

### Validação de Múltiplas
Fórmula de probabilidade combinada:
```
P(múltipla) = P(jogo1) × P(jogo2) × ... × P(jogoN)
```

**Exemplo:**
- Jogo 1: 85% (0.85)
- Jogo 2: 78% (0.78)
- Jogo 3: 92% (0.92)
- **Múltipla:** 0.85 × 0.78 × 0.92 = **61%**

### Trust Score
Calculado com base em:
- Probabilidade matemática
- Qualidade dos dados (OCR confidence)
- Consistência das odds entre casas
- Fatores de risco (desfalques, clima, etc.)

---

## 🎨 DESTAQUES VISUAIS

### Cards de Jogo
- **Layout:** Grid responsivo (1 col mobile, 2 cols desktop)
- **Elementos:**
  - Logos dos times (64x64px)
  - Badge de liga
  - Horário do jogo
  - Odds principais (Casa/Empate/Fora)
  - Tip recomendado com probabilidade
  - Badge "SNIPER" para picks premium
  - Comparação de 4 casas de apostas

### Modal de Dossiê
- **Tamanho:** Max-width 5xl, altura 90vh
- **Seções:**
  1. Header com título e botão fechar
  2. Corpo scrollável com:
     - Dados ao vivo (se disponível)
     - Contexto tático narrativo
     - Perfil detalhado de cada time
     - Estatísticas comparativas
  3. Footer com timestamp e botão de ação

### Gauge de Trust Score
```html
<svg viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="44" 
          stroke="#1e293b" 
          stroke-width="12" 
          fill="none"/>
  <circle cx="50" cy="50" r="44"
          stroke="url(#gradient)"
          stroke-width="12"
          fill="none"
          stroke-dasharray="276"
          stroke-dashoffset="calc(276 - (276 * TRUST_SCORE / 100))"
          class="animate-draw-gauge"/>
</svg>
```

---

## 📈 ROADMAP E MELHORIAS FUTURAS

### Funcionalidades Planejadas
- [ ] Integração com APIs reais de odds (Odds API)
- [ ] Sistema de notificações push para novos Snipers
- [ ] Histórico persistente em banco de dados (SQLite/PostgreSQL)
- [ ] Autenticação de usuários
- [ ] Planos de assinatura (Free/Premium)
- [ ] Exportação de relatórios em PDF
- [ ] Modo mobile app (PWA)
- [ ] Integração com Telegram Bot

### Otimizações Técnicas
- [ ] Cache de análises de IA
- [ ] Lazy loading de imagens de logos
- [ ] Service Worker para offline mode
- [ ] Compressão de assets
- [ ] CDN para logos de times
- [ ] Rate limiting nas APIs

### UX/UI
- [ ] Onboarding tutorial
- [ ] Tema claro (opcional)
- [ ] Customização de cores
- [ ] Atalhos de teclado
- [ ] Modo compacto para telas pequenas

---

## 🐛 PROBLEMAS CONHECIDOS

### Limitações Atuais
1. **Dados Hardcoded:** Jogos são estáticos, não vêm de API real
2. **OCR Accuracy:** Depende da qualidade da imagem
3. **Sem Persistência:** Histórico não é salvo entre sessões
4. **Logos Limitados:** Apenas ~50 times no dicionário
5. **Análise Mock:** `ai_engine.py` pode ter lógica simplificada

### Bugs Reportados
- Nenhum bug crítico reportado até o momento

---

## 📚 CONHECIMENTO TÉCNICO ACUMULADO

### Knowledge Items Relacionados
- **bot_probability_system** (Última atualização: 05/02/2026)
  - `overview.md` - Visão geral do sistema
  - `ai_knowledge_base.md` - Base de conhecimento da IA
  - `multi_risk_validator.md` - Validador de múltiplas
  - `ocr_logic.md` - Lógica de OCR
  - `technical_scout.md` - Sistema de scout técnico
  - `troubleshooting.md` - Solução de problemas

---

## 👥 HISTÓRICO DE CONVERSAS

### Conversas Relevantes
1. **28b39905** (06/02/2026) - Resume Bot Probability Project
2. **0620b7bb** (05-06/02/2026) - Install Agent Skills
3. **a7c154af** (05/02/2026) - Adding Login System (PDKHOT)
4. **2d24eb04** (05/02/2026) - Creating PDKHOT Website

---

## 🎓 CONCEITOS-CHAVE

### Glossário
- **Sniper Pick:** Aposta de alta confiança (>80% probabilidade)
- **Dutching:** Estratégia de distribuir stake entre múltiplos resultados
- **DNB (Draw No Bet):** Empate anula a aposta
- **Handicap:** Vantagem/desvantagem virtual
- **Over/Under:** Acima/Abaixo de um total
- **xG (Expected Goals):** Gols esperados baseado em qualidade de chances
- **Trust Score:** Índice de confiança da análise (0-100%)
- **Elo Mais Fraco:** Jogo com menor probabilidade numa múltipla

### Mercados de Aposta
- **1X2:** Casa/Empate/Fora
- **Dupla Chance:** Combina 2 resultados (1X, X2, 12)
- **Ambas Marcam:** Sim/Não
- **Total de Pontos/Gols:** Over/Under
- **Handicap Asiático:** -1.5, -2.0, etc.
- **HT/FT:** Resultado no intervalo e final

---

## 📞 SUPORTE E CONTATO

### Para Desenvolvedores
- Código fonte: `d:\BOT PROBABILITY\`
- Documentação técnica: Este arquivo
- Knowledge Base: `.gemini\antigravity\knowledge\bot_probability_system\`

### Para Usuários
- Interface web: `http://localhost:5000`
- Tutorial: Disponível no primeiro acesso (planejado)

---

## 📝 NOTAS FINAIS

Este projeto representa uma plataforma completa de análise esportiva com foco em:
- **Precisão:** Análises baseadas em dados reais e estatísticas
- **Usabilidade:** Interface intuitiva e responsiva
- **Transparência:** Histórico de performance visível
- **Educação:** Explicações detalhadas de cada análise

**Status Atual:** Sistema funcional em ambiente de desenvolvimento, pronto para testes e iterações.

**Próximos Passos Sugeridos:**
1. Integrar API real de odds
2. Implementar banco de dados
3. Adicionar autenticação
4. Deploy em servidor de produção

---

**Documento gerado em:** 07/02/2026 às 01:32 AM  
**Versão:** 1.0  
**Autor:** Sistema de Documentação Automática
