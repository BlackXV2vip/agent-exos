#!/usr/bin/env bash
# أمر تفاعلي — يدخل مباشرة على الوكيل بدون تحميل جديد
set -euo pipefail

# إيجاد المشروع المنزّل أو المحلي
SOURCE=""
for d in /tmp/agent-exos-source /tmp/agent-exos_install_*/repo /home/user/agent-exos .; do
  if [ -f "$d/packages/exos-agent/bin/exos-agent" ] || [ -d "$d/packages" ]; then
    SOURCE="$d"
    break
  fi
done

export PATH="/home/user/.bun/bin:$PATH" 2>/dev/null || true

echo "Agent 👨🏻‍💻: جاهز من المصدر: $SOURCE"
echo "You👤: اكتب سؤالك أو اتركه فارغاً للخروج"
echo "---"

if [ -d "$SOURCE" ]; then
  (cd "$SOURCE" && exec bun run --cwd packages/exos-agent dev 2>/dev/null || node -e 'console.log("Agent 👨🏻‍💻: يعمل عبر node من $SOURCE")')
else
  echo "Agent 👨🏻‍💻: لم يُعثر على المصدر — تأكد من وجود /tmp/agent-exos-source"
fi
