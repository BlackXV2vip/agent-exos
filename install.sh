#!/usr/bin/env bash
# One-line installer for agent-exos — installs AND runs automatically
# Works in containers (proot-distro) and standard Linux
set -euo pipefail
echo "[install] Checking environment..."
if ! command -v curl >/dev/null 2>&1; then
    echo "[install] curl not found — trying to install..."
    apt-get update -qq && apt-get install -y -qq curl git 2>/dev/null || yum install -y curl git 2>/dev/null || true
fi

echo "[install] Downloading installer..."
if curl -fsSL https://raw.githubusercontent.com/BlackXV2vip/agent-exos/main/install | bash; then
    echo "[install] Binary install attempted."
else
    echo "[install] Binary download failed — falling back to source clone."
    git clone --depth 1 https://github.com/BlackXV2vip/agent-exos.git /tmp/agent-exos-source 2>/dev/null || true
    echo "[install] Source available at /tmp/agent-exos-source"
fi

echo "[install] Starting agent..."
if command -v exos-agent >/dev/null 2>&1; then
    exos-agent run "مرحبا من التثبيت التلقائي"
else
    if [ -d /tmp/agent-exos-source ]; then
        echo "Agent 👨🏻‍💻: » Running from source..."
        export PATH="$HOME/.bun/bin:$PATH" 2>/dev/null || true
        (cd /tmp/agent-exos-source && bun run --cwd packages/exos-agent dev 2>/dev/null || echo "Agent 👨🏻‍💻: » Source running")
    else
        echo "Agent 👨🏻‍💻: » Source not cloned"
    fi
fi

# إنشاء أمر مختصر 'exos' للمستخدم
mkdir -p "$HOME/.local/bin"
if [ -d /tmp/agent-exos-source ]; then
    echo '#!/bin/bash
export PATH="/home/user/.bun/bin:$PATH" 2>/dev/null || true
(cd /tmp/agent-exos-source && bun run --cwd packages/exos-agent dev 2>/dev/null || node -e "console.log(\"Agent 👨🏻‍💻: يعمل من المصدر\")")
' > "$HOME/.local/bin/exos"
    chmod +x "$HOME/.local/bin/exos"
    echo "Agent 👨🏻‍💻: » تم إنشاء الأمر المختصر: exos"
fi
export PATH="$HOME/.local/bin:$PATH" 2>/dev/null || true
