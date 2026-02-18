#!/usr/bin/env bash
# -------------------------------------------------------
# setup_env.sh — Create virtualenv and install dependencies
# -------------------------------------------------------
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "==> Creating virtual environment in ${PROJECT_ROOT}/venv ..."
python3 -m venv "${PROJECT_ROOT}/venv"

echo "==> Activating virtual environment ..."
source "${PROJECT_ROOT}/venv/bin/activate"

echo "==> Installing dependencies ..."
pip install --upgrade pip
pip install -r "${PROJECT_ROOT}/requirements.txt"

echo ""
echo "✅  Environment ready. Activate with:"
echo "    source venv/bin/activate    (Linux/macOS)"
echo "    venv\\Scripts\\activate       (Windows)"
