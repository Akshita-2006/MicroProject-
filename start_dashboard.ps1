$ErrorActionPreference = 'Stop'
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $bundledPython) {
    & $bundledPython -m streamlit run (Join-Path $PSScriptRoot 'dashboard\app.py') --server.address 127.0.0.1
} else {
    python -m streamlit run (Join-Path $PSScriptRoot 'dashboard\app.py') --server.address 127.0.0.1
}
