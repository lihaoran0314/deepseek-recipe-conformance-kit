$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Run: python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -e ".[dev]"' }
& $python -m ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $python -m ruff format --check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $python -m pytest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $python -m recipe_conformance --adapter joined-mock --output reports\mock.json
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
