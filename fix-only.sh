#!/usr/bin/env bash
# يعدل الملفات فقط — بدون تحميل جديد
set -euo pipefail

PROJECT="${1:-/tmp/agent-exos-source}"
if [ ! -d "$PROJECT" ] && [ -d "/tmp/agent-exos_install_"* ]; then
  for d in /tmp/agent-exos_install_*/repo; do
    [ -d "$d" ] && PROJECT="$d" && break
  done
fi
if [ ! -d "$PROJECT" ]; then
  echo "Agent 👨🏻‍💻: المشروع غير موجود في $PROJECT"
  echo "You👤: هل نزّلت المشروع أولاً؟ جرب: curl ... | bash"
  exit 1
fi

echo "Agent 👨🏻‍💻: تعديل الملفات فقط في $PROJECT"

# إصلاح ESM
sed -i 's/const childProcess = require("child_process")/import { spawn, spawnSync } from "child_process"/' "$PROJECT/packages/exos-agent/bin/exos-agent" 2>/dev/null || true
sed -i 's/const fs = require("fs")/import fs from "fs"/' "$PROJECT/packages/exos-agent/bin/exos-agent" 2>/dev/null || true
sed -i 's/const path = require("path")/import path from "path"/' "$PROJECT/packages/exos-agent/bin/exos-agent" 2>/dev/null || true
sed -i 's/const os = require("os")/import os from "os"/' "$PROJECT/packages/exos-agent/bin/exos-agent" 2>/dev/null || true
sed -i 's/childProcess\.spawn/spawn/g; s/childProcess\.spawnSync/spawnSync/g' "$PROJECT/packages/exos-agent/bin/exos-agent" 2>/dev/null || true
sed -i 's/fs\.realpathSync(__filename)/fs.realpathSync(import.meta.url ? new URL(import.meta.url).pathname : process.argv[1])/' "$PROJECT/packages/exos-agent/bin/exos-agent" 2>/dev/null || true

# إصلاح Theme
sed -i 's/new Proxy(values(), {/new Proxy((values() || {}), {/' "$PROJECT/packages/tui/src/context/theme.tsx" 2>/dev/null || true

echo "Agent 👨🏻‍💻: تم التعديل ✅ — لا تحميل جديد"
