#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mock_site.py — محاكي موقع agent_exos_api.php لاختبارات e2e محلياً.
- يحاكي تحدي WAF الحقيقي (toNumbers + AES-CBC + كوكي __test) بمفاتيح عشوائية كل مرة.
- يرد على POST {"prompt": ...} بنفس صيغة الموقع: {"ok": true, "content": ...}.
- يقدّم صفحة /doc.html وواجهة /api/status لاختبار webfetch.
"""
import json
import os
import re
import sys
import time
import http.server

from Crypto.Cipher import AES

import mock_brain

PORT  = int(os.environ.get("MOCK_PORT", "8899"))
WAF   = "--no-waf" not in sys.argv
DELAY = float(os.environ.get("MOCK_DELAY", "0"))

DOC_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Agent Exos Handbook</title></head>
<body>
<h1>Agent Exos Handbook</h1>
<p>وثيقة الاختبار الداخلية — الرمز الفريد: <b>EXOS-DOC-TOKEN-881122</b></p>
<p>هذه الصفحة تُستخدم للتحقق من أداة webfetch ضمن اختبارات e2e.</p>
</body></html>"""

_issued = set()

def challenge_html():
    """يبني تحدي testcookie حقيقي: القيمة المشفّرة تُفك بالمفتاح/المتجه المعروضين."""
    key, iv, raw = os.urandom(16), os.urandom(16), os.urandom(16)
    ct = AES.new(key, AES.MODE_CBC, iv).encrypt(raw)
    _issued.add(raw.hex())
    return ("<html><body><script>"
            "function toNumbers(d){var e=[];d.replace(/(..)/g,function(d){e.push(parseInt(d,16))});return e}"
            "function toHex(){for(var d=[],cx=0;cx<arguments.length;cx++)"
            "d.push((256+arguments[cx]).toString(16).slice(1));return d.join(\"\")}"
            "var slowAES={decrypt:function(c,m,k,p){return c}};"
            "var a=toNumbers(\"%s\"),b=toNumbers(\"%s\"),c=toNumbers(\"%s\");"
            "document.cookie=\"__test=\"+toHex(slowAES.decrypt(c,2,a,b))+\"; path=/\";"
            "location.href=\"?i=1\";"
            "</script></body></html>") % (key.hex(), iv.hex(), ct.hex())

class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code, body, ctype="text/html"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

    def _cookie_ok(self):
        m = re.search(r"__test=([a-f0-9]{32,})", self.headers.get("Cookie", ""))
        return bool(m and m.group(1) in _issued)

    def do_GET(self):
        if self.path.startswith("/doc.html"):
            self._send(200, DOC_HTML.encode("utf-8"))
            return
        if self.path.startswith("/api/status"):
            body = json.dumps({"status": "operational", "token": "API-TOKEN-4451",
                               "ts": int(time.time())}).encode()
            self._send(200, body, "application/json")
            return
        if WAF and not self._cookie_ok():
            self._send(200, challenge_html().encode())
            return
        self._send(200, b"OK")

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n).decode("utf-8", "replace") or "{}")
        except Exception:
            data = {}
        if WAF and not self._cookie_ok():
            self._send(403, json.dumps({"ok": False, "error": "waf blocked"}).encode(),
                       "application/json")
            return
        if DELAY:
            time.sleep(DELAY)
        content = mock_brain.decide(str(data.get("prompt", "")))
        self._send(200, json.dumps({"ok": True, "content": content}).encode("utf-8"),
                   "application/json")

def main():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print("mock site on :%d (waf=%s delay=%s)" % (PORT, WAF, DELAY), file=sys.stderr, flush=True)
    srv.serve_forever()

if __name__ == "__main__":
    main()
