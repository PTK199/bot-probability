import sqlite3
from datetime import datetime, timedelta
import user_manager

# Configuração
DB_NAME = "database.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def adicionar_dias(email, dias):
    conn = conectar()
    cursor = conn.cursor()
    
    # Verifica se o usuário existe
    cursor.execute("SELECT id, data_validade FROM users WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    
    if not usuario:
        print(f"❌ Erro: Usuário {email} não encontrado!")
        conn.close()
        return

    # Lógica de Renovação Inteligente
    agora = datetime.now()
    validade_atual_str = usuario[1]
    
    # Formato consistente com o user_manager
    fmt = "%Y-%m-%d %H:%M:%S"
    
    if validade_atual_str:
        try:
            # Tenta converter com ou sem microssegundos para ser robusto
            if "." in validade_atual_str:
                validade_atual = datetime.strptime(validade_atual_str, "%Y-%m-%d %H:%M:%S.%f")
            else:
                validade_atual = datetime.strptime(validade_atual_str, fmt)
        except:
            validade_atual = agora
            
        # Se ainda não venceu, soma a partir da validade atual. Se já venceu, soma a partir de AGORA.
        nova_base = validade_atual if validade_atual > agora else agora
    else:
        nova_base = agora
        
    nova_validade = nova_base + timedelta(days=dias)
    nova_validade_str = nova_validade.strftime(fmt)
    
    cursor.execute("UPDATE users SET data_validade = ? WHERE email = ?", (nova_validade_str, email))
    conn.commit()
    conn.close()
    
    print(f"✅ SUCESSO! O acesso de {email} foi estendido até: {nova_validade_str}")

def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT email, data_validade FROM users")
    todos = cursor.fetchall()
    conn.close()
    
    print("\n--- 📋 LISTA DE USUÁRIOS ---")
    for u in todos:
        validade_str = u[1]
        if not validade_str:
            status = "🔴 VENCIDO"
            vence_em = "Nunca"
        else:
            try:
                if "." in validade_str:
                    v_dt = datetime.strptime(validade_str, "%Y-%m-%d %H:%M:%S.%f")
                else:
                    v_dt = datetime.strptime(validade_str, "%Y-%m-%d %H:%M:%S")
                status = "🟢 ATIVO" if v_dt > datetime.now() else "🔴 VENCIDO"
                vence_em = v_dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                status = "🔴 ERRO"
                vence_em = "Data Invalida"
                
        print(f"[{status}] {u[0]} | Vence em: {vence_em}")
    print("----------------------------\n")

# MENU PRINCIPAL
while True:
    print("\n👑 PAINEL DE DEUS - GERENCIADOR DO BOT")
    print("1. Listar Usuários")
    print("2. Renovar Acesso (+7 dias, +30 dias...)")
    print("3. Criar Novo Usuário (Manual)")
    print("4. Sair")
    
    opcao = input("Escolha uma opção: ")
    
    if opcao == "1":
        listar_usuarios()
    elif opcao == "2":
        email = input("Digite o email do usuário: ")
        try:
            dias = int(input("Quantos dias adicionar? (Ex: 7): "))
            adicionar_dias(email, dias)
        except ValueError:
            print("❌ Digite um número válido de dias.")
    elif opcao == "3":
        email = input("Email: ")
        senha = input("Senha: ")
        try:
            if user_manager.create_user(email, senha):
                print("✅ Usuário criado com sucesso!")
            else:
                print("❌ Usuário já existe.")
        except Exception as e:
            print(f"❌ Erro ao criar: {e}")
    elif opcao == "4":
        print("Até logo, Chefe! 🚀")
        break
