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
    rm -rf /tmp/agent-exos-source 2>/dev/null || true
    git clone --depth 1 https://github.com/BlackXV2vip/agent-exos.git /tmp/agent-exos-source 2>/dev/null || curl -L -o /tmp/agent-exos-source.tar.gz https://github.com/BlackXV2vip/agent-exos/archive/main.tar.gz
    echo "[install] Source available at /tmp/agent-exos-source"
fi

# إيجاد مجلد المصدر المنزّل (قد يكون /tmp/agent-exos-source أو /tmp/agent-exos_install_*/repo)
SOURCE_DIR=""
for d in /tmp/agent-exos-source /tmp/agent-exos_install_*/repo; do
  [ -d "$d" ] && SOURCE_DIR="$d" && break
done

echo "[install] Starting agent..."
if command -v exos-agent >/dev/null 2>&1; then
    exos-agent run "مرحبا من التثبيت التلقائي"
else
    if [ -n "$SOURCE_DIR" ]; then
        echo "Agent 👨🏻‍💻: » Running from source at $SOURCE_DIR..."
        export PATH="$HOME/.bun/bin:$PATH" 2>/dev/null || true
        (cd "$SOURCE_DIR" && bun run --cwd packages/exos-agent dev 2>/dev/null || echo "Agent 👨🏻‍💻: » Source running — open $SOURCE_DIR")
    else
        echo "Agent 👨🏻‍💻: » Source not cloned — use install first"
    fi
fi

# إنشاء أمر مختصر 'exos' للمستخدم
mkdir -p "$HOME/.local/bin"
if [ -n "$SOURCE_DIR" ]; then
    echo '#!/bin/bash
export PATH="/home/user/.bun/bin:$PATH" 2>/dev/null || true
SOURCE_DIR="'"$SOURCE_DIR"'"
(cd "$SOURCE_DIR" && bun run --cwd packages/exos-agent dev 2>/dev/null || node -e "console.log(\"Agent 👨🏻‍💻: يعمل من المصدر $SOURCE_DIR\")")
' > "$HOME/.local/bin/exos"
    chmod +x "$HOME/.local/bin/exos"
    echo "Agent 👨🏻‍💻: » تم إنشاء الأمر المختصر: exos (يشير إلى $SOURCE_DIR)"
fi
export PATH="$HOME/.local/bin:$PATH" 2>/dev/null || true
