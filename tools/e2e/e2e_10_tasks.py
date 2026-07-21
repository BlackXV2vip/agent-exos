#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
e2e_10_tasks.py — اختبار e2e شامل: 10 مهام معقدة جداً عبر محرك الوكيل الحقيقي.

السلسلة الكاملة لكل مهمة:
  المحرك (opencode/exos-agent) → exos-bridge (بروتوكول EXOS_TOOL) → mock_site (WAF+دماغ)
  → tool_call → تنفيذ حقيقي على القرص → نتيجة → ... → إجابة نهائية.

التحقق ثلاثي المستويات:
  1) الدماغ يتحقق من ناتج كل أداة قبل الخطوة التالية.
  2) السائق يتحقق من ظهور علامة النجاح النهائية في مخرجات المحرك.
  3) السائق يتحقق من الآثار الجانبية على نظام الملفات بشكل مستقل.
"""
import glob as pyglob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

BASE = "/home/user/e2e_runs"
ROOT = os.path.dirname(os.path.abspath(__file__))
NATIVE_PROVIDER = os.path.normpath(os.path.join(ROOT, "..", "exos-provider", "index.ts"))
ENGINE = os.environ.get("EXOS_ENGINE_BIN", os.path.expanduser("~/.opencode/bin/opencode"))
BRIDGE_PORT = int(os.environ.get("EXOS_PORT", "8765"))
MOCK_PORT = int(os.environ.get("MOCK_PORT", "8899"))
ANSI = re.compile(r"\x1b\[[0-9;]*m")

TASKS = {
    "01": "[E2E-T01] سلسلة بناء متعددة المراحل داخل {B}/t1: ولّد سكربت هاش بايثون، شغّله، راكم ملفات، واحسب بصمات md5 و sha256 للتحقق من سلامة السلسلة كاملة.",
    "02": "[E2E-T02] أنشئ ملف إعدادات JSON متداخل في {B}/t2/config.json بخمسة مفاتيح، اقرأه للتحقق، ثم عدّل رقم الإصدار من 1.0.0 إلى 2.4.1 وأعد القراءة للتأكيد.",
    "03": "[E2E-T03] ازرع شجرة ملفات .exos موزعة على مجلدات متداخلة (14 ملفاً) مع ملفات .tmp مشتتة، ثم اعثر عليها كلها بنمط glob وتجاهل الملفات المشتتة.",
    "04": "[E2E-T04] ازرع مشروع بايثون صغير فيه أسرار نصية، ثم اعثر على كل مواضع SECRET_TOKEN_77 عبر الملفات، ثم احصِ تعريفات الدوال def داخل ملفات .py فقط.",
    "05": "[E2E-T05] اجلب الوثيقة من http://127.0.0.1:8899/doc.html واستخرج منها الرمز الفريد وعنوان الكتاب.",
    "06": "[E2E-T06] ضع خطة نشر إصدار جديد من Agent Exos في 5 مهام مرتبة بالأولوية والحالة باستخدام أداة المهام.",
    "07": "[E2E-T07] فوّض وكيلاً فرعياً لقراءة ملف سري {B}/t7/secret.txt واسترجاع رمزه، ثم أكد الرمز في إجابتك النهائية.",
    "08": "[E2E-T08] حمّل مهارة exos-report واتبع تعليماتها بدقة لتوليد تقرير في {B}/t8/report.md بالصيغة الموحدة المطلوبة.",
    "09": "[E2E-T09] استعلم واجهة http://127.0.0.1:8899/api/status ثم احفظ الرمز المستلم في ملف JSON منظم داخل {B}/t9/status.json.",
    "10": "[E2E-T10] سلسلة تكاملية كاملة: اكتب سكربت hasher.py يحسب sha256 لملح+ملف، شغّله، عدّل بادئة إخراجه، أعد التشغيل مع حفظ الناتج، ابحث عن السطر بالنتيجة، ثم اقرأ الملف النهائي وتأكد من البصمة.",
}

H1 = hashlib.sha256(b"exos-1").hexdigest()[:8]
DATA = "ExosCoreData-2026"
DIGEST = hashlib.sha256(("exos-salt:" + DATA).encode()).hexdigest()

def fs_checks(tid):
    e = lambda m: (_ for _ in ()).throw(AssertionError(m))
    if tid == "01":
        r = open(f"{BASE}/t1/run1.txt").read()
        a = open(f"{BASE}/t1/acc.txt").read()
        if "EXOS_T1_OK" not in r or len(a.splitlines()) != 3: e("t1 files bad")
        if hashlib.sha256((r + a).encode()).hexdigest()[:16] != hashlib.sha256(
            ("EXOS_T1_OK %s\n" % H1 + "line-1\nline-2\nline-3\n").encode()).hexdigest()[:16]:
            e("t1 sha mismatch")
        return "run1.txt+acc.txt sha256 ✓"
    if tid == "02":
        cfg = json.load(open(f"{BASE}/t2/config.json"))
        if cfg["version"] != "2.4.1" or cfg["limits"]["io"]["read"] != 100: e("t2 json bad")
        return "config.json version=2.4.1 ✓"
    if tid == "03":
        n = len(pyglob.glob(f"{BASE}/t3/**/*.exos", recursive=True))
        if n != 14: e(f"t3 found {n}")
        return f"glob fscount={n} ✓"
    if tid == "04":
        hits = [f for f in pyglob.glob(f"{BASE}/t4/**/*", recursive=True)
                if os.path.isfile(f) and "SECRET_TOKEN_77" in open(f, errors="replace").read()]
        if len(hits) != 3: e(f"t4 hits={hits}")
        return "grep fsverify=3files ✓"
    if tid == "08":
        rep = open(f"{BASE}/t8/report.md").read()
        if not rep.startswith("EXOS-REPORT-V1"): e("t8 header")
        for h in ("ملخص", "تفاصيل", "خاتمة"):
            if h not in rep: e(f"t8 missing {h}")
        return "report.md صيغة موحدة ✓"
    if tid == "09":
        st = json.load(open(f"{BASE}/t9/status.json"))
        if st.get("fetched_token") != "API-TOKEN-4451": e("t9 token")
        return "status.json token ✓"
    if tid == "10":
        out = open(f"{BASE}/t10/out.txt").read().strip()
        if out != "DIGEST2=" + DIGEST: e(f"t10 digest {out}")
        return "out.txt sha256 مستقل ✓"
    return "—"

EXPECT = {
    "01": "T1-COMPLETE", "02": "T2-COMPLETE", "03": "T3-COMPLETE",
    "04": "T4-COMPLETE", "05": "T5-COMPLETE", "06": "T6-COMPLETE",
    "07": "T7-COMPLETE", "08": "T8-COMPLETE", "09": "T9-COMPLETE",
    "10": "T10-COMPLETE",
}

def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=kw.pop("timeout", 60), stdin=subprocess.DEVNULL, **kw)

def wait_http(url, tries=60):
    import urllib.request
    for _ in range(tries):
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            time.sleep(0.25)
    return False

def main():
    procs = []
    external = "--external-servers" in sys.argv
    native = "--native" in sys.argv   # المزوّد الأصيل file:// بدون جسر
    try:
        # ---------- تجهيز مساحة العمل
        shutil.rmtree(BASE, ignore_errors=True)
        os.makedirs(BASE)
        sh(["git", "init", "-q"], cwd=BASE)
        os.makedirs(f"{BASE}/t7"); open(f"{BASE}/t7/secret.txt", "w").write("EXO-9917")
        os.makedirs(f"{BASE}/t10"); open(f"{BASE}/t10/data.txt", "w").write(DATA)
        for skroot in (f"{BASE}/.opencode/skills", f"{BASE}/.exos-agent/skills"):
            sk = os.path.join(skroot, "exos-report")
            os.makedirs(sk)
            open(f"{sk}/SKILL.md", "w").write(
                "---\nname: exos-report\ndescription: توليد تقارير Agent Exos بالصيغة الموحدة EXOS-REPORT-V1\n---\n"
                "# مهارة تقارير Exos\nكل تقرير يجب أن:\n1. يبدأ بالسطر الأول `EXOS-REPORT-V1` حرفياً.\n"
                "2. يحوي ثلاثة أقسام بالترتيب: `ملخص` ثم `تفاصيل` ثم `خاتمة`.\n3. لا يسبق السطر الأول أي محتوى.\n")
        if native:
            # المزوّد الأصيل: file:// — المحرك يكلم الموقع مباشرة ({"prompt"})
            provider_block = {"provider": {"exos": {
                "npm": "file://" + NATIVE_PROVIDER, "name": "Exos",
                "options": {"baseURL": f"http://127.0.0.1:{MOCK_PORT}/agent_exos_api.php"},
                "models": {"Agent Exos": {"name": "Agent Exos", "tool_call": True,
                                          "limit": {"context": 128000, "output": 8192}}}}}}
        else:
            provider_block = {"provider": {"exos": {
                "npm": "@ai-sdk/openai-compatible", "name": "Exos",
                "options": {"baseURL": f"http://127.0.0.1:{BRIDGE_PORT}/v1"},
                "models": {"Agent Exos": {"name": "Agent Exos", "tool_call": True,
                                          "limit": {"context": 128000, "output": 8192}}}}}}
        prov_cfg = dict({
            "$schema": "https://opencode.ai/config.json",
            "permission": {"*": "allow", "bash": "allow", "edit": "allow",
                           "webfetch": "allow", "external_directory": "allow"}},
            **provider_block)
        # كونفيج المشروع: opencode.json (المحرك الرسمي) + exos-agent.json (المعاد تسميته)
        open(f"{BASE}/opencode.json", "w").write(json.dumps(prov_cfg, indent=2))
        open(f"{BASE}/exos-agent.json", "w").write(json.dumps(prov_cfg, indent=2))
        # مزوّد exos في الكونفيج العالمي أيضاً — أي instance ثانوية (share/sync)
        # تشتغل من مجلد بلا كونفيج مشروع يجب أن تجد المزوّد وإلا تسمّم الجلسة
        for gdir, gfile in ((os.path.expanduser("~/.config/opencode"), "opencode.json"),
                            (os.path.expanduser("~/.config/exos-agent"), "exos-agent.json")):
            os.makedirs(gdir, exist_ok=True)
            gpath = os.path.join(gdir, gfile)
            gcfg = {}
            if os.path.exists(gpath):
                try:
                    gcfg = json.load(open(gpath))
                except Exception:
                    gcfg = {}
            gcfg.setdefault("$schema", "https://opencode.ai/config.json")
            gcfg.setdefault("permission", {"*": "allow"})
            gcfg.setdefault("provider", {}).update(provider_block["provider"])
            open(gpath, "w").write(json.dumps(gcfg, indent=2))

        # ---------- تشغيل الموقع الوهمي + الجسر
        env = dict(os.environ, MOCK_PORT=str(MOCK_PORT))
        if not external:
            mock_err = open(f"{BASE}/mock.err.log", "w")
            bridge_err = open(f"{BASE}/bridge.err.log", "w")
            procs.append(subprocess.Popen([sys.executable, os.path.join(ROOT, "mock_site.py")],
                                          env=env, stdin=subprocess.DEVNULL, start_new_session=True,
                                          stdout=subprocess.DEVNULL, stderr=mock_err))
            if not native and not "--native" in sys.argv:
                benv = dict(os.environ, EXOS_SITE=f"http://127.0.0.1:{MOCK_PORT}/agent_exos_api.php",
                            EXOS_PORT=str(BRIDGE_PORT), EXOS_LOG=f"{BASE}/bridge.log")
                procs.append(subprocess.Popen([sys.executable, os.path.join(ROOT, "exos-bridge.py")],
                                              env=benv, stdin=subprocess.DEVNULL, start_new_session=True,
                                              stdout=subprocess.DEVNULL, stderr=bridge_err))
        if not wait_http(f"http://127.0.0.1:{MOCK_PORT}/doc.html"):
            print("FATAL: mock site لم يشتغل"); return 2
        if not native and not wait_http(f"http://127.0.0.1:{BRIDGE_PORT}/v1/models"):
            print("FATAL: bridge لم يشتغل"); return 2
        if not os.path.exists(ENGINE):
            print("FATAL: المحرك غير موجود:", ENGINE); return 2

        # ---------- إحماء e2e عبر السلسلة كاملة قبل المهام
        try:
            import urllib.request as _u
            if native:
                # إحماء مباشر ضد الموقع الوهمي ببروتوكول {"prompt"}
                warm = json.dumps({"prompt": "User: [E2E-T05] إحماء\n\n=== EXOS_TOOL_PROTOCOL_V2 ==="}).encode()
                rq = _u.Request(f"http://127.0.0.1:{MOCK_PORT}/agent_exos_api.php", data=warm,
                                headers={"Content-Type": "application/json",
                                         "Cookie": "__test=skip", "User-Agent": "Mozilla/5.0"})
                print("warm-up: mock(site) جاهز")
            else:
                warm = json.dumps({"model": "Agent Exos",
                    "messages": [{"role": "user", "content": "[E2E-T05] إحماء"}],
                    "tools": [{"function": {"name": "webfetch", "description": "d",
                                            "parameters": {"type": "object"}}}]}).encode()
                rq = _u.Request(f"http://127.0.0.1:{BRIDGE_PORT}/v1/chat/completions", data=warm,
                                headers={"Content-Type": "application/json"})
                d = json.loads(_u.urlopen(rq, timeout=30).read())
                tc = d["choices"][0]["message"]["tool_calls"][0]["function"]["name"]
                print("warm-up: WAF+bridge+mock سلسلة سليمة (tool_call=%s)" % tc)
        except Exception as ex:
            print("FATAL: warm-up فشل:", ex); return 2

        print("=" * 74)
        print("  e2e — المحرك: %s" % ENGINE)
        print("=" * 74)
        results = []
        t_all = time.time()
        for tid in sorted(TASKS):
            prompt = TASKS[tid].replace("{B}", BASE)
            t0 = time.time()
            # ملاحظة: المحرك (bun) يتعطل لو stdout=PIPE — لذلك نوجّه لملف حقيقي
            logf = os.path.join(BASE, "run_T%s.log" % tid)
            try:
                with open(logf, "w") as lf:
                    p = subprocess.Popen([ENGINE, "run", prompt, "-m", "exos/Agent Exos"],
                                         cwd=BASE, stdin=subprocess.DEVNULL,
                                         stdout=lf, stderr=subprocess.STDOUT)
                    p.wait(timeout=240)
                with open(logf, encoding="utf-8", errors="replace") as lf:
                    out = ANSI.sub("", lf.read())
            except subprocess.TimeoutExpired:
                p.kill()
                out = "TIMEOUT"
            dt = time.time() - t0
            ok = EXPECT[tid] in out and "E2E_FAIL" not in out
            note = ""
            if ok:
                try:
                    note = fs_checks(tid)
                except AssertionError as ex:
                    ok, note = False, "FS: %s" % ex
            if not ok and not note:
                tail = " | ".join(out.strip().splitlines()[-3:])[:160]
                note = tail
            results.append((tid, ok, dt, note))
            print("T%s  %s  %5.1fs  %s" % (tid, "PASS ✅" if ok else "FAIL ❌", dt, note), flush=True)

        npass = sum(1 for _, ok, _, _ in results if ok)
        print("-" * 74)
        print("النتيجة الإجمالية: %d/10 ناجحة في %.1fs" % (npass, time.time() - t_all))
        if native:
            print("الوضع: المزوّد الأصيل file:// — المحرك كلم الموقع مباشرة بدون جسر")
        else:
            ntool = 0
            try:
                ntool = sum(1 for l in open(f"{BASE}/bridge.log", encoding="utf-8") if "TOOL_CALL" in l)
            except Exception:
                pass
            print("عدد استدعاءات الأدوات عبر الجسر: %d" % ntool)
        return 0 if npass == 10 else 1
    finally:
        for p in procs:
            try: p.terminate()
            except Exception: pass

if __name__ == "__main__":
    sys.exit(main())
