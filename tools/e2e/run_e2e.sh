#!/usr/bin/env bash
# run_e2e.sh — مشغّل اختبار e2e الكامل (10 مهام).
# السيرفرات تُطلَق من هذا الشِل مباشرة (متطلب بيئة التنفيذ)،
# وسائق Python يشغّل المهام العشر عبر المحرك ويتحقق من النتائج.
set -u
cd "$(dirname "$0")"
BASE=/home/user/e2e_runs
MOCK_PORT=${MOCK_PORT:-8899}
BRIDGE_PORT=${EXOS_PORT:-8765}
ENGINE=${EXOS_ENGINE_BIN:-$HOME/.opencode/bin/opencode}
export EXOS_ENGINE_BIN="$ENGINE"

cleanup() {
  [ -n "${MPID:-}" ] && kill "$MPID" 2>/dev/null
  [ -n "${BPID:-}" ] && kill "$BPID" 2>/dev/null
}
trap cleanup EXIT INT TERM

mkdir -p "$BASE"
NATIVE=${NATIVE:-0}   # NATIVE=1 ▶ المزوّد الأصيل file:// بدون جسر

echo "[run_e2e] starting mock site :$MOCK_PORT"
MOCK_PORT=$MOCK_PORT setsid nohup python3 mock_site.py >"$BASE/mock.err.log" 2>&1 < /dev/null &
MPID=$!
sleep 0.7
EXTRA_ARGS="--external-servers"
if [ "$NATIVE" = "1" ]; then
  echo "[run_e2e] وضع NATIVE — بدون جسر (المحرك ⇄ الموقع مباشرة)"
  EXTRA_ARGS="$EXTRA_ARGS --native"
else
  echo "[run_e2e] starting bridge :$BRIDGE_PORT"
  EXOS_SITE="http://127.0.0.1:$MOCK_PORT/agent_exos_api.php" \
  EXOS_PORT="$BRIDGE_PORT" EXOS_LOG="$BASE/bridge.log" \
    setsid nohup python3 exos-bridge.py >"$BASE/bridge.err.log" 2>&1 < /dev/null &
  BPID=$!
  sleep 1
fi

cd "$BASE"
python3 "$OLDPWD/e2e_10_tasks.py" $EXTRA_ARGS
RC=$?
echo "[run_e2e] exit=$RC"
exit $RC
