# MEMÓRIA DO PROJETO VANGUARDA NEURAL (CORTEX V6.0)

## O QUE É ESSE PROJETO?
Um sistema de inteligência artificial soberana para análise preditiva de esportes (NBA e Futebol).
Ele opera com uma arquitetura híbrida: **Cérebro Local (Python/Flask)** + **Memória Infinita (Supabase Cloud)**.

## ESTADO ATUAL (11/02/2026 - 01:20)
- **Infraestrutura:** Conectado à Nuvem (Supabase) via `supabase_client.py` (REST API Direta).
- **Dados:** 
  - **260 Times** e **1500+ Jogadores** migrados para o banco de dados SQL na nuvem.
  - Tabela `predictions` ativa para logar cada decisão da IA.
- **Backend:** 
  - `ai_engine.py`: Atualizado com 42 módulos neurais, incluindo `log_match_prediction` para aprendizado contínuo.
  - Limpeza de código realizada (arquivos temporários removidos).

## ÚLTIMAS CORREÇÕES CRÍTICAS
1. [x] **Integração Supabase:** Upload da Knowledge Base completo (Teams/Players).
2. [x] **Logging em Nuvem:** O módulo `neural_cortex_omega` agora salva previsões automaticamente para auditoria futura.
3. [x] **Faxina:** Remoção de 20+ arquivos de lixo/teste (`debug_*.py`, `temp_*.js`, dumps SQL antigos).
4. [x] **Resgate de Conexão:** Implementado cliente HTTP puro para contornar limitações de ambiente Windows.

## PRÓXIMOS PASSOS (EVOLUÇÃO)
1. **Self-Correction:** Usar os dados acumulados na tabela `predictions` para ajustar os pesos dos módulos automaticamente.
2. **Dashboard de Performance:** Criar uma página `/admin` para visualizar a eficácia da IA em tempo real (Winrate por Liga).
3. **Expansão Mobile:** Refinar a interface mobile.

## ARQUITETURA ATUALIZADA
- `app.py`: Servidor API & Web.
- `ai_engine.py`: Núcleo de Processamento (42 Módulos).
- `supabase_client.py`: Ponte para a Nuvem (Persistência).
- `specialized_modules.py`: Extensões Táticas.
- `templates/`: Interface do Usuário (Mobile-First).
