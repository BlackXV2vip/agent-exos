#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mock_brain.py — محاكي نموذج Agent Exos لاختبارات e2e.
يستقبل البرومبت المسطّح من الـ bridge ويقرّر الخطوة التالية وفق سيناريوهات E2E-T01..T10.
كل سيناريو يتحقق بنفسه من نتيجة كل أداة (expect) قبل طلب الخطوة التالية —
أي فشل يعني أن المحرك نفّذ الأداة خطأً أو أن البروتوكول انكسر.
"""
import hashlib
import json
import re

BANNER = "EXOS_TOOL_PROTOCOL_V2"
BASE = "/home/user/e2e_runs"

# ---------------------------------------------------------------- تحليل الجولات
def parse_rounds(prompt):
    """يستخرج [(tool_name, args_json, result_text), ...] بالترتيب من البرومبت المسطّح."""
    rounds = []
    lines = prompt.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"Assistant used tool (\w+) with arguments (.*)$", lines[i])
        if not m:
            i += 1
            continue
        name, args_s = m.group(1), m.group(2)
        res, j = [], i + 1
        while j < len(lines):
            l2 = lines[j]
            if l2.startswith("Assistant used tool ") or l2.startswith("User:") \
               or l2.startswith("Assistant:") or l2.startswith("==="):
                break
            res.append(l2)
            j += 1
        rounds.append((name, args_s, "\n".join(res)))
        i = j
    return rounds

def expect_sub(*subs):
    def chk(res):
        for s in subs:
            if s not in res:
                return False, "missing %r" % s
        return True, "ok"
    return chk

def expect_exos_count(min_n):
    def chk(res):
        n = len(re.findall(r"[\w\-./]+\.exos", res))
        return (n >= min_n), "found %d .exos paths (want>=%d)" % (n, min_n)
    return chk

def expect_def(ref):
    def chk(res):
        n = res.count("def ")
        return (n >= ref), "found %d 'def ' (want>=%d)" % (n, ref)
    return chk

# ---------------------------------------------------------------- قيم مستقلة للتحقق
_H1   = hashlib.sha256(b"exos-1").hexdigest()[:8]                       # T1
_ACC  = "line-1\nline-2\nline-3\n"
_MD5  = hashlib.md5(_ACC.encode()).hexdigest()                          # T1
_SHA3 = hashlib.sha256(("EXOS_T1_OK %s\n" % _H1 + _ACC).encode()).hexdigest()  # T1
_DATA = "ExosCoreData-2026"                                             # T10
_DIGEST = hashlib.sha256(("exos-salt:" + _DATA).encode()).hexdigest()   # T10

DOC_TOKEN = "EXOS-DOC-TOKEN-881122"                                     # T5
API_TOKEN = "API-TOKEN-4451"                                            # T9
SECRET_CODE = "EXO-9917"                                                # T7

def d(name, args):
    return "<<EXOS_TOOL:%s>>" % json.dumps({"name": name, "arguments": args}, ensure_ascii=False)

def step(tool, args, expect=None):
    return {"tool": tool, "args": args, "expect": expect}

# ---------------------------------------------------------------- السيناريوهات
T1 = [
    step("bash", {"command": "mkdir -p %s/t1 && cd %s/t1 && "
        "printf 'import hashlib\\nprint(\"EXOS_T1_OK\", hashlib.sha256(b\"exos-1\").hexdigest()[:8])\\n' > gen.py && "
        "python3 gen.py > run1.txt && cat run1.txt" % (BASE, BASE)},
        expect_sub("EXOS_T1_OK", _H1)),
    step("bash", {"command": "cd %s/t1 && for i in 1 2 3; do echo \"line-$i\" >> acc.txt; done && "
        "sort acc.txt | md5sum" % BASE},
        expect_sub(_MD5)),
    step("bash", {"command": "cd %s/t1 && cat run1.txt acc.txt | sha256sum" % BASE},
        expect_sub(_SHA3)),
]

T2 = [
    step("write", {"filePath": "%s/t2/config.json" % BASE, "content":
        json.dumps({"app": "exos-core", "version": "1.0.0",
                    "limits": {"cpu": 4, "mem": "512M", "io": {"read": 100, "write": 50}},
                    "flags": ["agent", "tools", "bridge"], "enabled": True}, indent=2)}),
    step("read", {"filePath": "%s/t2/config.json" % BASE},
        expect_sub('"version": "1.0.0"', '"exos-core"', '"read": 100')),
    step("edit", {"filePath": "%s/t2/config.json" % BASE,
                  "oldString": '"version": "1.0.0"', "newString": '"version": "2.4.1"'}),
    step("read", {"filePath": "%s/t2/config.json" % BASE},
        expect_sub('"version": "2.4.1"')),
]

T3 = [
    step("bash", {"command": f"rm -rf {BASE}/t3 && mkdir -p {BASE}/t3/a {BASE}/t3/b/c {BASE}/t3/d/e/f && "
        "for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14; do "
        "case $i in 0[1-5]) dir=a;; 0[6-9]|10) dir=b/c;; *) dir=d/e/f;; esac; "
        f"echo seed-$i > {BASE}/t3/$dir/n$i.exos; done && "
        f"echo x > {BASE}/t3/a/junk1.tmp && echo x > {BASE}/t3/b/c/junk2.tmp && echo x > {BASE}/t3/junk3.tmp && "
        f"find {BASE}/t3 -name '*.exos' | wc -l"},
        expect_sub("14")),
    step("glob", {"pattern": "**/*.exos", "path": "%s/t3" % BASE},
        expect_exos_count(14)),
]

T4 = [
    step("bash", {"command": f"rm -rf {BASE}/t4 && mkdir -p {BASE}/t4/src && "
        f"printf 'def alpha():\\n    return \"SECRET_TOKEN_77\"\\n' > {BASE}/t4/src/alpha.py && "
        f"printf 'def beta():\\n    x = \"SECRET_TOKEN_77\"\\n    return x\\ndef helper():\\n    pass\\n' > {BASE}/t4/src/beta.py && "
        f"printf 'def gamma():\\n    return 1\\n' > {BASE}/t4/src/gamma.py && "
        f"echo 'SECRET_TOKEN_77 in plain text' > {BASE}/t4/notes.txt && "
        f"ls {BASE}/t4/src"},
        expect_sub("alpha.py", "beta.py", "gamma.py")),
    step("grep", {"pattern": "SECRET_TOKEN_77", "path": f"{BASE}/t4"},
        expect_sub("alpha.py", "beta.py", "notes.txt")),
    step("grep", {"pattern": "def ", "path": f"{BASE}/t4/src", "include": "*.py"},
        expect_def(4)),
]

T5 = [
    step("webfetch", {"url": "http://127.0.0.1:8899/doc.html", "format": "text"},
        expect_sub(DOC_TOKEN, "Agent Exos Handbook")),
]

T6_TODOS = [
    {"id": "1", "content": "فحص بيئة النشر والتحقق من التبعيات", "status": "completed", "priority": "high"},
    {"id": "2", "content": "بناء حزمة exos-agent من السورس المعاد تسميته", "status": "in_progress", "priority": "high"},
    {"id": "3", "content": "تشغيل اختبارات bridge الوحدوية العشر", "status": "pending", "priority": "medium"},
    {"id": "4", "content": "نشر النسخة الجديدة على Termux", "status": "pending", "priority": "medium"},
    {"id": "5", "content": "تدوير الأسرار المكشوفة فوراً", "status": "pending", "priority": "high"},
]
T6 = [
    step("todowrite", {"todos": T6_TODOS}),
]

T7 = [
    step("task", {"description": "قراءة ملف سري عبر وكيل فرعي",
                  "prompt": "[E2E-T07-SUB] اقرأ الملف %s/t7/secret.txt بالكامل ثم أعد محتواه مسبوقاً بـ SUBANS:" % BASE,
                  "subagent_type": "general"},
        expect_sub(SECRET_CODE)),
]

T7_SUB = [
    step("read", {"filePath": "%s/t7/secret.txt" % BASE},
        expect_sub(SECRET_CODE)),
]

T8 = [
    step("skill", {"name": "exos-report"},
        expect_sub("EXOS-REPORT-V1", "ملخص", "تفاصيل", "خاتمة")),
    step("write", {"filePath": "%s/t8/report.md" % BASE, "content":
        "EXOS-REPORT-V1\n\n## ملخص\nاختبار تحميل الـ skill نجح.\n\n"
        "## تفاصيل\nتم تحميل SKILL.md عبر أداة skill ثم اتباع تعليماتها حرفياً.\n\n"
        "## خاتمة\nالبروتوكول كامل: skill → write.\n"}),
]

T9 = [
    step("webfetch", {"url": "http://127.0.0.1:8899/api/status", "format": "text"},
        expect_sub(API_TOKEN, "operational")),
    step("write", {"filePath": "%s/t9/status.json" % BASE, "content":
        json.dumps({"fetched_token": API_TOKEN, "checked": True}, indent=2)}),
]

T10 = [
    step("write", {"filePath": "%s/t10/hasher.py" % BASE, "content":
        "import hashlib, sys\n"
        "data = open(sys.argv[1], 'rb').read()\n"
        "print(\"DIGEST=\" + hashlib.sha256(b'exos-salt:' + data).hexdigest())\n"}),
    step("bash", {"command": "cd %s/t10 && python3 hasher.py data.txt" % BASE},
        expect_sub("DIGEST=" + _DIGEST)),
    step("edit", {"filePath": "%s/t10/hasher.py" % BASE,
                  "oldString": "print(\"DIGEST=\"", "newString": "print(\"DIGEST2=\""}),
    step("bash", {"command": "cd %s/t10 && python3 hasher.py data.txt > out.txt && cat out.txt" % BASE},
        expect_sub("DIGEST2=" + _DIGEST)),
    step("grep", {"pattern": "DIGEST2", "path": "%s/t10" % BASE},
        expect_sub("out.txt", "DIGEST2=" + _DIGEST)),
    step("read", {"filePath": "%s/t10/out.txt" % BASE},
        expect_sub("DIGEST2=" + _DIGEST)),
]

SCENARIOS = {
    "01": (T1, lambda r: "T1-COMPLETE sha3=%s" % _SHA3[:16]),
    "02": (T2, lambda r: "T2-COMPLETE version=2.4.1"),
    "03": (T3, lambda r: "T3-COMPLETE exos=14 tmp=3"),
    "04": (T4, lambda r: "T4-COMPLETE matches=3 defs>=4"),
    "05": (T5, lambda r: "T5-COMPLETE token=%s" % DOC_TOKEN),
    "06": (T6, lambda r: "T6-COMPLETE todos=5"),
    "07": (T7, lambda r: "T7-COMPLETE code=%s" % SECRET_CODE),
    "07-SUB": (T7_SUB, lambda r: "SUBANS: %s" % SECRET_CODE),
    "08": (T8, lambda r: "T8-COMPLETE report=EXOS-REPORT-V1"),
    "09": (T9, lambda r: "T9-COMPLETE token=%s" % API_TOKEN),
    "10": (T10, lambda r: "T10-COMPLETE digest=%s" % _DIGEST),
}

# ---------------------------------------------------------------- نقطة القرار
def decide(prompt):
    if BANNER not in prompt:
        return "جلسة اختبار Agent Exos"
    mk = re.search(r"\[E2E-T(\d{2})(-SUB)?\]", prompt)
    if not mk:
        return "تم الاستلام — لا يوجد سيناريو مطابق لهذا البرومبت."
    key = mk.group(1) + (mk.group(2) or "")
    scen = SCENARIOS.get(key)
    if not scen:
        return "E2E_FAIL: لا يوجد سيناريو %s" % key
    steps, final = scen
    rounds = parse_rounds(prompt)
    for idx, (name, args_s, res) in enumerate(rounds):
        if idx >= len(steps):
            return "E2E_FAIL %s: جولة زائدة غير متوقعة" % key
        st = steps[idx]
        if name != st["tool"]:
            return "E2E_FAIL %s خطوة %d: طُلبت أداة %s والمطلوب %s" % (key, idx + 1, name, st["tool"])
        exp = st.get("expect")
        if exp:
            ok, msg = exp(res)
            if not ok:
                return "E2E_FAIL %s خطوة %d (%s): %s | الناتج: %s" % (
                    key, idx + 1, name, msg, res[:250].replace("\n", " "))
    if len(rounds) == len(steps):
        return final(rounds)
    st = steps[len(rounds)]
    return d(st["tool"], st["args"])

if __name__ == "__main__":
    # فحص ذاتي سريع: محاكاة جولات T01
    p = "User: [E2E-T01] ابني\n\n=== %s ===" % BANNER
    r1 = decide(p)
    assert r1.startswith("<<EXOS_TOOL:"), r1
    obj = json.loads(r1[len("<<EXOS_TOOL:"):-2])
    assert obj["name"] == "bash", obj
    p2 = p + "\nAssistant used tool bash with arguments {}\nTool result (call x): EXOS_T1_OK %s\n" % _H1
    r2 = decide(p2)
    assert "md5sum" in r2, r2
    print("mock_brain self-check OK")
