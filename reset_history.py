import json
import os
import shutil
import sys

# Encoding
try:
    sys.stdout.reconfigure(encoding='utf-8')
except: pass

print("🧹 [SYSTEM] INICIANDO PROTOCOLO DE RESET DE HISTÓRICO...")

# 1. Backup de Segurança
if os.path.exists('history.json'):
    shutil.copy('history.json', 'history_OLD_backup.json')
    print("📦 Backup de segurança criado: history_OLD_backup.json")

# 2. Reset (Manter apenas 11/02 se existir, senão zerar)
target_date = "11/02"
kept_count = 0

try:
    if os.path.exists('history.json'):
        with open('history.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Filtra apenas jogos de hoje
        new_data = [d for d in data if d.get('date') == target_date]
        kept_count = len(new_data)
        
        with open('history.json', 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
            
        print(f"✨ Sucesso! Histórico limpo. {kept_count} registros de hoje ({target_date}) foram preservados/iniciados.")
    else:
        # Cria arquivo vazio
        with open('history.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("✨ Arquivo history.json criado (vazio).")

except Exception as e:
    print(f"❌ Erro crítico no reset: {e}")
