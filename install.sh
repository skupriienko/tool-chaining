#!/usr/bin/env bash
# install.sh — Universal installer for tool-chaining.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "==> Installing tool-chaining in editable mode..."
pip install -e "$REPO_DIR" --quiet
echo "✔ tool-chaining installed successfully. Run 'tool-chain --help' to start."
