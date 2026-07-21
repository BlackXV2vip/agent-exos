#!/usr/bin/env bash
# wire-exos.sh — ربط الأداة بـ api.php في أمر واحد.
# ينسخ المزوّد الأصيل إلى ~/.exos-agent/exos-provider ويكتب كونفيج المحركين.
#
#   EXOS_SITE="https://wormgpte.xo.je/agent_exos_api.php"   (الافتراضي)
#   EXOS_TOKEN="..."                                        (اختياري: قناة مرخّصة)
#   EXOS_TOKEN_HEADER="X-Auth-Token"                        (الافتراضي)
set -euo pipefail

SRC="$(cd "$(dirname "$0")/../tools/exos-provider" && pwd)"
DEST="$HOME/.exos-agent/exos-provider"
SITE="${EXOS_SITE:-https://wormgpte.xo.je/agent_exos_api.php}"

echo "[1/3] نسخ المزوّد الأصيل → $DEST"
mkdir -p "$DEST"
cp "$SRC/index.ts" "$DEST/index.ts"

echo "[2/3] كتابة كونفيج المزوّد (baseURL = $SITE)"
python3 - "$SITE" <<'PY'
import json, os, sys
site = sys.argv[1]
prov_js = os.path.expanduser("~/.exos-agent/exos-provider/index.ts")
block = {
    "npm": "file://" + prov_js, "name": "Exos",
    "options": {"baseURL": site},
    "models": {"Agent Exos": {"name": "Agent Exos", "tool_call": True,
                              "limit": {"context": 128000, "output": 8192}}},
}
for d, fn in ((os.path.expanduser("~/.config/opencode"), "opencode.json"),
              (os.path.expanduser("~/.config/exos-agent"), "exos-agent.json")):
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, fn)
    cfg = {}
    if os.path.exists(p):
        try: cfg = json.load(open(p))
        except Exception: cfg = {}
    cfg.setdefault("$schema", "https://opencode.ai/config.json")
    cfg.setdefault("permission", {"*": "allow"})
    cfg.setdefault("provider", {})["exos"] = block
    cfg.setdefault("model", "exos/Agent Exos")
    json.dump(cfg, open(p, "w"), indent=2, ensure_ascii=False)
    print("  ✓", p)
PY

echo "[3/3] تم ✅  المحرك الآن يكلم api.php مباشرة (بدون جسر وبدون openai-compatible)"
echo "      جرّب: exos-agent run \"جرّب أداة bash\""
