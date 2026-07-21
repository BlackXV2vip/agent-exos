#!/usr/bin/env python3
"""
Exos Agent — OpenAI-compatible gateway shim (stdlib only, zero deps)
====================================================================

يحوّل أي backend بسيط بشكل `{"prompt": ...}` إلى واجهة OpenAI القياسية
`/v1/chat/completions` (بما فيها بث SSE) — بحيث يتكلم معها محرّك Exos Agent
فورًا عبر مزوّد `@ai-sdk/openai-compatible`.

⚠️ مبدأ أساسي: المحوّل يتكلم مع بوابتك عبر **قناة مُرخّصة نضيفة فقط**
   (توكن سرّي في الهيدر). لو الاستجابة تحمل توقيع bot-challenge
   (HTML مكوّد / AES challenge كوكي)، يرفض المحوّل بصوتٍ واضح ويرشدك:
   استضف الـ backend على خادم لا يفرض تحديات آليّة — فتح قناة مُرخّصة
   (توكن) أفضل وأبسط من تخطّي أي بوابة.

التشغيل:
    export EXOS_UPSTREAM_URL="https://YOUR-HOST/your_api.php"
    export EXOS_UPSTREAM_TOKEN="choose-a-long-secret"   # يُفحص داخل backend بتاعك
    python3 tools/gateway-shim/shim.py                  # يسمع على 127.0.0.1:8790

وفي exos-agent.json (أو EXOS_AGENT_CONFIG_CONTENT):
    {"provider": {"shim": {"npm": "@ai-sdk/openai-compatible",
      "options": {"baseURL": "http://127.0.0.1:8790/v1", "apiKey": "local"},
      "models": {"exos-brain": {"name": "Exos Brain"}}}},
     "model": "shim/exos-brain"}

توافق الـ backend المطلوب (أقل مواصفات):
    POST EXOS_UPSTREAM_URL
    headers: {"X-Auth-Token": EXOS_UPSTREAM_TOKEN, "Content-Type": "application/json"}
    body:    {"prompt": "<النص المفلطح من الرسائل>"}
    resp:    {"ok": true, "content": "<الرد>"}
"""
import json
import os
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = os.environ.get("EXOS_UPSTREAM_URL", "").rstrip("/")
TOKEN = os.environ.get("EXOS_UPSTREAM_TOKEN", "")
TIMEOUT = float(os.environ.get("EXOS_UPSTREAM_TIMEOUT", "60"))
RETRIES = int(os.environ.get("EXOS_UPSTREAM_RETRIES", "3"))
HOST, PORT = os.environ.get("EXOS_SHIM_HOST", "127.0.0.1"), int(os.environ.get("EXOS_SHIM_PORT", "8790"))

CHALLENGE_SIGNS = ("&lt;script", "toNumbers(", "AES", "challenge")


def flatten(messages):
    """يفلطح رسائل المحادثة إلى برومبت نصّي واحد."""
    parts = []
    for m in messages or []:
        role = m.get("role", "user")
        content = m.get("content", "")
        if isinstance(content, list):
            content = " ".join(str(p.get("text", "")) for p in content if isinstance(p, dict))
        if role in ("system", "tool"):
            continue  # هوية المحرك ونتائج الأدوات لا تُمرر كنص حر هنا
        parts.append(str(content))
    return "\n".join(p for p in parts if p).strip()


def ask_upstream(prompt):
    """طلب واحد للبوابة مع إعادة محاولة عند المهلات فقط."""
    body = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(
        UPSTREAM, data=body, method="POST",
        headers={"Content-Type": "application/json", "X-Auth-Token": TOKEN,
                 "User-Agent": "exos-gateway-shim/1.0"})
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                raw = r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return None, f"upstream HTTP {e.code}"
        except Exception as e:  # timeout/refused → أعد المحاولة
            if attempt == RETRIES - 1:
                return None, f"upstream unreachable after {RETRIES} tries: {e}"
            time.sleep(2)
            continue
        if any(sig in raw for sig in CHALLENGE_SIGNS):
            return None, ("upstream looks like a bot-challenge page, not a JSON API — "
                          "host the backend without anti-automation challenges "
                          "(see tools/gateway-shim/README.md)")
        try:
            data = json.loads(raw)
        except ValueError:
            return None, f"upstream did not return JSON: {raw[:120]!r}"
        if isinstance(data, dict) and data.get("ok") and isinstance(data.get("content"), str):
            return data["content"], None
        return None, f"upstream error: {data!r}"[:200]
    return None, "unreachable"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _j(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/v1/models", "/models"):
            return self._j(200, {"object": "list", "data": [
                {"id": "exos-brain", "object": "model", "owned_by": "exos-agent"}]})
        self._j(404, {"error": "not found"})

    def do_POST(self):
        if not any(self.path.endswith(p) for p in ("/v1/chat/completions", "/chat/completions")):
            return self._j(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._j(400, {"error": "bad json"})
        prompt = flatten(body.get("messages"))
        model = body.get("model", "exos-brain")
        reply, err = ask_upstream(prompt)
        if err:
            return self._j(502, {"error": {"message": err, "type": "upstream_error"}})
        if body.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()

            def chunk(delta, finish=None):
                self.wfile.write(("data: " + json.dumps({
                    "id": "chatcmpl-shim", "object": "chat.completion.chunk",
                    "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}
                ) + "\n\n").encode())

            chunk({"role": "assistant"})
            step = 24
            for i in range(0, len(reply), step):
                chunk({"content": reply[i:i + step]})
            chunk({}, "stop")
            self.wfile.write(b"data: [DONE]\n\n")
        else:
            self._j(200, {"id": "chatcmpl-shim", "object": "chat.completion",
                          "created": int(time.time()), "model": model,
                          "choices": [{"index": 0, "message": {"role": "assistant",
                                       "content": reply}, "finish_reason": "stop"}],
                          "usage": {"prompt_tokens": len(prompt) // 4,
                                    "completion_tokens": len(reply) // 4,
                                    "total_tokens": (len(prompt) + len(reply)) // 4}})


def main():
    if not UPSTREAM:
        raise SystemExit("حدد EXOS_UPSTREAM_URL أولًا (رأس الملف فيه التعليمات)")
    print(f"⚡ Exos shim listening → http://{HOST}:{PORT}/v1  (upstream: {UPSTREAM})")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
