$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir
Write-Host '本地预览地址：http://127.0.0.1:8765/'
Write-Host '按 Ctrl+C 停止预览。'
python -m http.server 8765
