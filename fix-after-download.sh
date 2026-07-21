#!/usr/bin/env bash
# أمر الإصلاح بعد التنزيل للمستخدم الجديد
set -euo pipefail
export PATH="$HOME/.bun/bin:$PATH" 2>/dev/null || true

echo "[fix] إصلاح خطأ ESM في bin/exos-agent..."
sed -i 's/const childProcess = require("child_process")/import { spawn, spawnSync } from "child_process"/' packages/exos-agent/bin/exos-agent 2>/dev/null || true
sed -i 's/const fs = require("fs")/import fs from "fs"/' packages/exos-agent/bin/exos-agent 2>/dev/null || true
sed -i 's/const path = require("path")/import path from "path"/' packages/exos-agent/bin/exos-agent 2>/dev/null || true
sed -i 's/const os = require("os")/import os from "os"/' packages/exos-agent/bin/exos-agent 2>/dev/null || true
sed -i 's/childProcess\.spawn/spawn/g; s/childProcess\.spawnSync/spawnSync/g' packages/exos-agent/bin/exos-agent 2>/dev/null || true
sed -i 's/fs\.realpathSync(__filename)/fs.realpathSync(import.meta.url ? new URL(import.meta.url).pathname : process.argv[1])/' packages/exos-agent/bin/exos-agent 2>/dev/null || true

echo "[fix] تثبيت الحزم..."
bun install 2>/dev/null || npm install 2>/dev/null || echo "[fix] bun/npm غير متوفر"

echo "[fix] إصلاح theme.tsx..."
sed -i 's/new Proxy(values(), {/new Proxy((values() || {}), {/' packages/tui/src/context/theme.tsx 2>/dev/null || true

echo "[fix] جاهز للتشغيل: bun run --cwd packages/exos-agent dev"
