#!/usr/bin/env bash
# Mac / Linux setup
set -e
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "Install Python 3 from python.org"; exit 1; }
command -v node >/dev/null || { echo "Install Node.js from nodejs.org"; exit 1; }
python3 -m pip install -r requirements.txt
(cd bridge && npm install)
[ -f .env ] || cp .env.example .env
echo "Done. Put your ANTHROPIC_API_KEY in .env, then run ./start.sh"
