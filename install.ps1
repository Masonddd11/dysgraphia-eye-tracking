# One-command setup for Windows (Gazepoint GP3 HD data-collection host).
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found - installing from astral.sh..."
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

Write-Host "Installing Python 3.12 and syncing dependencies..."
uv python install 3.12
uv sync

Write-Host "Running the offline test suite..."
uv run fyp test

Write-Host @"

Setup complete.

Windows / Gazepoint host:
  1. Install Gazepoint Control and connect the GP3 HD (USB 3.0).
  2. Confirm the OpenGaze API port is 4242 in Gazepoint Control.
  3. uv run fyp calibrate
  4. uv run fyp both --stimulus data\sample_paragraph.txt

macOS / Linux (webcam + analysis): run install.sh instead.
"@
