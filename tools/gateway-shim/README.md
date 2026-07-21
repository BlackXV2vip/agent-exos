# ⚡ Exos Gateway Shim — قناة مُرخّصة، بلا تجاوز

محوّل stdlib صغير يجعل أي backend بسيط (`{"prompt": …}` → `{"ok", "content"}`)
يبدو كـ OpenAI API قياسي لمحرّك Exos Agent.

## الفلسفة

- ✅ **القناة المُرخّصة**: توكن سرّي واحد (`X-Auth-Token`) تفحصه داخل السكريبت بتاعك.
  لو البوابة ملكك، فتح قناة مُرخّصة *أبسط وأأمن* من أي تخطّي.
- 🚫 **بلا تجاوز حماية**: لو الرد page بتاع تحدّي آلي (JS challenge/AES cookie)،
  المحوّل يفشل برسالة واضحة. التوقيع ده غالبًا بيفرضه مزود الاستضافة نفسه (الاستضافات المجانية)،
  فحتى لو السكريبت بتاعك، **البوابة مش بتاعتك** — والحل استضافة نظيفة.

## استضافات بدون تحديات آلية (أمثلة، اختر ما يناسبك)

- VPS صغير (أي مزوّد) — تحكم كامل
- Cloudflare Workers / Pages Functions (فري تير)
- Render / Fly.io / Railway (فري تير للتجربة)
- حتى `ngrok` أو `cloudflared` على جهازك لو الـ backend محلي

## أقل مواصفات للـ backend

```http
POST /your_api.php
X-Auth-Token: <EXOS_UPSTREAM_TOKEN>
Content-Type: application/json

{"prompt": "..."}
```

يجيب:

```json
{"ok": true, "content": "..."}
```

تحقق التوكن داخل السكريبت (مثال PHP — السطرين دول كفاية):

```php
if (($_SERVER['HTTP_X_AUTH_TOKEN'] ?? '') !== 'choose-a-long-secret')
    { http_response_code(401); exit(json_encode(['ok'=>false,'error'=>'unauthorized'])); }
```

## التشغيل

```bash
export EXOS_UPSTREAM_URL="https://YOUR-HOST/your_api.php"
export EXOS_UPSTREAM_TOKEN="choose-a-long-secret"
python3 tools/gateway-shim/shim.py          # 127.0.0.1:8790
```

ثم في `exos-agent.json`:

```json
{
  "provider": {
    "shim": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Exos Gateway",
      "options": { "baseURL": "http://127.0.0.1:8790/v1", "apiKey": "local" },
      "models": { "exos-brain": { "name": "Exos Brain" } }
    }
  },
  "model": "shim/exos-brain"
}
```

## متغيرات البيئة

| المتغير | الافتراضي | الغرض |
|---|---|---|
| `EXOS_UPSTREAM_URL` | — (إلزامي) | رابط الـ API |
| `EXOS_UPSTREAM_TOKEN` | فارغ | التوكن المرسل في `X-Auth-Token` |
| `EXOS_UPSTREAM_TIMEOUT` | `60` | مهلة الطلب بالثواني |
| `EXOS_UPSTREAM_RETRIES` | `3` | محاولات عند فشل الشبكة |
| `EXOS_SHIM_HOST/PORT` | `127.0.0.1:8790` | عنوان الاستماع |
