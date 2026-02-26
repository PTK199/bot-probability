# -*- coding: utf-8 -*-
"""
git_autopush.py - Auto-commit e push para o GitHub após qualquer atualização.
Uso: from git_autopush import autopush; autopush("mensagem")
  ou: python git_autopush.py "mensagem opcional"
"""
import subprocess
import sys
from datetime import datetime


def autopush(message: str = None) -> bool:
    """
    Faz git add -A, git commit e git push automaticamente.
    Retorna True se sucesso, False se erro.
    """
    if not message:
        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        message = f"auto: atualiza history e dados [{now}]"

    cmds = [
        ['git', 'add', '-A'],
        ['git', 'commit', '-m', message],
        ['git', 'push'],
    ]

    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.returncode != 0:
            # "nothing to commit" nao e erro real
            if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
                print("[git] Nada para commitar — repositorio ja esta atualizado.")
                return True
            print(f"[git] ERRO em '{' '.join(cmd)}':\n{result.stderr}")
            return False
        if cmd[1] != 'add':
            print(f"[git] OK: {result.stdout.strip()}")

    return True


if __name__ == '__main__':
    msg = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else None
    success = autopush(msg)
    sys.exit(0 if success else 1)
