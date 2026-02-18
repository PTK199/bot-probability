# Guia de Deploy - Vanguarda Neural

## 1. Preparação
Os arquivos necessários para deploy (subida) já foram configurados:
- `Procfile`: Comando de inicialização do servidor.
- `requirements.txt`: Lista de dependências limpa (removidos pacotes pesados não utilizados como Tesseract).
- `runtime.txt`: Versão do Python (3.11.8).

## 2. Escolha da Plataforma

### Opção A: Railway (Recomendado)
A Railway suporta Python nativamente e é muito fácil de usar.
1. Crie uma conta em [railway.app](https://railway.app).
2. Crie um "New Project" -> "Deploy from GitHub repo" (ou suba o código via CLI).
3. A Railway detectará automaticamente o `Procfile` e `requirements.txt`.
4. **Variáveis de Ambiente**:
   - Adicione `FLASK_SECRET_KEY` (gere uma chave segura).
   - Adicione `THE_ODDS_API_KEY` (sua chave da API).

**Atenção sobre o Banco de Dados (SQLite) e Arquivos (history.json):**
Como o Railway/Render usam sistema de arquivos efêmero (os arquivos resetam quando o app reinicia), o histórico salvo em `history.json` e os usuários em `database.db` **serão perdidos** a cada novo deploy ou reinício do servidor.
- **Solução Definitiva:** Migrar para PostgreSQL (A Railway oferece um plugin de Postgres fácil).
- **Solução Temporária:** O sistema funcionará, mas o histórico voltará ao estado original do commit a cada reinício.

### Opção B: Render
Semelhante ao Railway.
1. Crie um "Web Service" conectado ao seu repositório.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app` (o Render lê o Procfile também).

## 3. Segurança do Login
Verificamos que o sistema de login está ativo (`@login_required`).
- Usuário Admin atual: `admin@bot.com`
- Certifique-se de que a senha deste usuário é forte antes de subir para produção.
- Se precisar resetar, use o script `admin.py` localmente ou via Console SSH na plataforma de deploy.

## 4. Próximos Passos (Pós-Deploy)
1. Monitorar os logs para garantir que a API de Odds está respondendo (atenção ao limite de requisições).
2. Se o histórico precisar ser persistente, solicitar a migração para Banco de Dados SQL (Postgres).
