#!/usr/bin/env bash
# One-line installer for agent-exos — installs AND runs automatically
set -euo pipefail
echo "[install] Downloading and installing agent-exos..."
curl -fsSL https://raw.githubusercontent.com/BlackXV2vip/agent-exos/main/install | bash
echo "[install] Starting agent..."
exec exos-agent run "مرحبا من التثبيت التلقائي"
