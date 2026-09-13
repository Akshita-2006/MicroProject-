$ErrorActionPreference = 'Stop'
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    $projectPython = 'python'
}
Push-Location -LiteralPath $PSScriptRoot
try {
    & $projectPython -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8502
    $dashboardExitCode = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $dashboardExitCode
