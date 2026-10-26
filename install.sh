#!/usr/bin/env bash
# One-command setup for macOS / Linux (webcam rig + analysis).
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found - installing from astral.sh..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "Installing Python 3.12 and syncing dependencies..."
uv python install 3.12
uv sync

echo "Running the offline test suite..."
uv run fyp test

cat <<'EOF'

Setup complete.

macOS / Linux (webcam + analysis):
  uv run fyp webcam --stimulus data/sample_paragraph.txt
  uv run fyp --help

Windows / Gazepoint host:
  Run install.ps1 on the Windows PC, install Gazepoint Control, connect the
  GP3 HD to USB 3.0, and confirm the OpenGaze API port is 4242.
EOF
