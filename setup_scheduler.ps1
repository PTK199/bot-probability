# setup_scheduler.ps1
# Registra o auto_updater.py no Agendador de Tarefas do Windows
# Executa: Todo dia as 00:30
# Uso: Clique com o botao direito > "Executar com PowerShell" (como Administrador)

$TaskName    = "BotProbability-AutoUpdater"
$ProjectDir  = "d:\BOT PROBABILITY"
$ScriptPath  = "$ProjectDir\auto_updater.py"
$LogPath     = "$ProjectDir\logs\auto_updater.log"

# Encontra o Python instalado
$PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    $PythonPath = "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe"
}
if (-not (Test-Path $PythonPath)) {
    Write-Host "ERRO: Python nao encontrado. Instale o Python ou ajuste o caminho manualmente." -ForegroundColor Red
    exit 1
}

Write-Host "Python encontrado: $PythonPath" -ForegroundColor Green

# Remove tarefa existente (se houver)
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Define a acao: python auto_updater.py
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory $ProjectDir

# Define o gatilho: todo dia as 00:30
$Trigger = New-ScheduledTaskTrigger -Daily -At "00:30"

# Configuracoes da tarefa
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -WakeToRun:$false

# Registra a tarefa para o usuario atual (sem necessidade de Admin)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Force | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Tarefa registrada com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Nome:    $TaskName"
Write-Host " Script:  $ScriptPath"
Write-Host " Horario: Todo dia as 00:30"
Write-Host " Log:     $LogPath"
Write-Host ""
Write-Host "Para testar agora (sem esperar 00:30):" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host ""
