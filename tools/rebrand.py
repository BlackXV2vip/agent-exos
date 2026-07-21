#!/usr/bin/env python3
"""
Agent Exos rebrand pipeline: opencode -> exos-agent / Exos Agent
=================================================================
Case-aware token replacement across all tracked files + path renames.

Rules:
  opencode-ai  -> exos-agent        (npm scope @opencode-ai -> @exos-agent)
  OPENCODE     -> EXOS_AGENT        (env vars, SCREAMING_CASE)
  OpenCode     -> ExosAgent         (PascalCase identifiers) | "Exos Agent" in prose (.md)
  openCode     -> exosAgent         (camelCase)
  Opencode     -> ExosAgent         (identifiers) | "Exos Agent" in prose (.md)
  opencode     -> exos-agent        (lowercase: binary, paths, urls)

Skipped entirely: LICENSE (MIT attribution is legally required), binary files,
and this script itself.

Usage:
  python3 tools/rebrand.py --dry-run   # stats only, no changes
  python3 tools/rebrand.py --apply     # apply replacements + git mv renames
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SELF = os.path.relpath(os.path.abspath(__file__), ROOT)
SKIP_FILES = {"LICENSE", SELF}
PROSE_EXT = {".md", ".mdx", ".mdc"}

B = r"(?<![A-Za-z0-9]){tok}(?![A-Za-z0-9])"  # token boundary


def rules(prose: bool):
    oc = "Exos Agent" if prose else "ExosAgent"
    lo = "exos-agent"
    return [
        # npm scope must run before the generic lowercase rule
        (re.compile(r"opencode-ai"), "exos-agent"),
        # github app slug "opencodegent"
        (re.compile(r"opencodegent"), "exos-agent"),
        # embedded inside longer identifiers: createOpencodeClient,
        # OpencodeClient, opencodeZen, OpenCodeEvent, WslOpencodeCheck...
        (re.compile(r"OPENCODE(?=[A-Z])"), "EXOS_AGENT"),
        (re.compile(r"OpenCode(?=[A-Z])"), "ExosAgent"),
        (re.compile(r"Opencode(?=[A-Z])"), "ExosAgent"),
        (re.compile(r"opencode(?=[A-Z])"), "exosAgent"),
        # inflected prose forms: OpenCodes (genitive), Opencodeom (Bosnian)...
        (re.compile(r"(?<![A-Za-z0-9])OpenCode(?=[a-z])"), oc),
        (re.compile(r"(?<![A-Za-z0-9])Opencode(?=[a-z])"), oc),
        (re.compile(r"(?<![A-Za-z0-9])opencode(?=[a-z])"), lo),
        (re.compile(r"(?<=[a-z])Opencode(?![A-Za-z0-9])"), "ExosAgent"),
        (re.compile(r"(?<=[a-z])OpenCode(?![A-Za-z0-9])"), "ExosAgent"),
        (re.compile(r"(?<=[a-z])opencode(?![A-Za-z0-9])"), "exosAgent"),
        # URL-encoded contexts: %5Copencode, %27opencode%27
        (re.compile(r"(?<=%[0-9A-Fa-f][0-9A-Fa-f])Opencode"), "ExosAgent"),
        (re.compile(r"(?<=%[0-9A-Fa-f][0-9A-Fa-f])OpenCode"), "ExosAgent"),
        (re.compile(r"(?<=%[0-9A-Fa-f][0-9A-Fa-f])OPENCODE"), "EXOS_AGENT"),
        (re.compile(r"(?<=%[0-9A-Fa-f][0-9A-Fa-f])opencode"), "exos-agent"),
        # whole-word forms
        (re.compile(B.format(tok="OPENCODE")), "EXOS_AGENT"),
        (re.compile(B.format(tok="OpenCode")), oc),
        (re.compile(B.format(tok="openCode")), "exosAgent"),
        (re.compile(B.format(tok="Opencode")), oc),
        (re.compile(B.format(tok="opencode")), "exos-agent"),
    ]


# External npm packages that merely CONTAIN the old name — they live on the
# registry and are NOT part of this repo, so their names must be restored
# after the token pass (keeps the pipeline idempotent).
PRESERVE = [
    ("exos-agent-gitlab-auth", "opencode-gitlab-auth"),
    ("exos-agent-poe-auth", "opencode-poe-auth"),
]


def preserve_externals(text: str) -> str:
    for wrong, right in PRESERVE:
        text = text.replace(wrong, right)
    return text


CODE_RULES = rules(prose=False)
PROSE_RULES = rules(prose=True)

FENCE = re.compile(r"^(```|~~~)")
INLINE = re.compile(r"(`+)(.+?)\1")


def transform_prose_line(line: str) -> str:
    """Code rules inside `inline code`, prose rules outside."""
    out, last = [], 0
    for m in INLINE.finditer(line):
        seg = line[last:m.start()]
        for r, rep in PROSE_RULES:
            seg = r.sub(rep, seg)
        out.append(seg)
        code_seg = m.group(0)
        for r, rep in CODE_RULES:
            code_seg = r.sub(rep, code_seg)
        out.append(code_seg)
        last = m.end()
    seg = line[last:]
    for r, rep in PROSE_RULES:
        seg = r.sub(rep, seg)
    out.append(seg)
    return "".join(out)


def transform(path: str, text: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext not in PROSE_EXT:
        for r, rep in CODE_RULES:
            text = r.sub(rep, text)
        return preserve_externals(text)
    in_fence = False
    lines = []
    for line in text.splitlines(keepends=True):
        if FENCE.match(line.lstrip()):
            in_fence = not in_fence
            # fence lines themselves can carry titles: ```json title="opencode.json"
            for r, rep in CODE_RULES:
                line = r.sub(rep, line)
            lines.append(line)
            continue
        if in_fence:
            for r, rep in CODE_RULES:
                line = r.sub(rep, line)
            lines.append(line)
        else:
            lines.append(transform_prose_line(line))
    return preserve_externals("".join(lines))


def new_path(path: str) -> str:
    out = []
    for part in path.split("/"):
        for r, rep in CODE_RULES:
            part = r.sub(rep, part)
        out.append(part)
    return "/".join(out)


def is_binary(data: bytes) -> bool:
    return b"\0" in data[:8192]


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    return [p.decode() for p in out.split(b"\0") if p]


def main():
    apply = "--apply" in sys.argv
    files = tracked_files()
    stats = {"changed": 0, "skipped_bin": 0, "skipped_files": [], "renames": 0}
    per_rule = {rep: 0 for _, rep in CODE_RULES + PROSE_RULES}

    # ---- text pass ----
    for rel in files:
        if rel in SKIP_FILES:
            stats["skipped_files"].append(rel)
            continue
        full = os.path.join(ROOT, rel)
        try:
            data = open(full, "rb").read()
        except OSError:
            continue
        if is_binary(data):
            stats["skipped_bin"] += 1
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            stats["skipped_bin"] += 1
            continue
        new = transform(rel, text)
        if new != text:
            stats["changed"] += 1
            for r, rep in rules(os.path.splitext(rel)[1].lower() in PROSE_EXT):
                per_rule[rep] += len(r.findall(text))
            if apply:
                open(full, "wb").write(new.encode("utf-8"))

    # ---- path renames ----
    # Pass 1: dirs shallow-first (children move with parent).
    # Pass 2: re-scan; rename any file whose *basename* still needs changing.
    def apply_renames():
        moved = 0
        dirs = sorted(
            {os.path.dirname(p) for p in tracked_files() if os.path.dirname(p)},
            key=lambda d: (d.count("/"), d),
        )
        for d in dirs:
            nd = new_path(d)
            if nd == d or not os.path.exists(os.path.join(ROOT, d)):
                continue  # already moved with an ancestor
            os.makedirs(os.path.dirname(os.path.join(ROOT, nd)), exist_ok=True)
            subprocess.run(["git", "mv", "-f", d, nd], cwd=ROOT, check=True)
            moved += 1
        for f in tracked_files():
            base, d = os.path.basename(f), os.path.dirname(f)
            nb = new_path(base)
            if nb == base:
                continue
            subprocess.run(
                ["git", "mv", "-f", f, os.path.join(d, nb) if d else nb],
                cwd=ROOT,
                check=True,
            )
            moved += 1
        return moved

    if apply:
        stats["renames"] = apply_renames()
    else:
        dir_changes = sorted(
            {
                (d, new_path(d))
                for d in {os.path.dirname(p) for p in files if os.path.dirname(p)}
                if new_path(d) != d
            }
        )
        file_changes = sorted(
            {
                (f, new_path(f))
                for f in files
                if new_path(os.path.basename(f)) != os.path.basename(f)
            }
        )
        stats["renames"] = len(dir_changes) + len(file_changes)
        print("--- sample renames ---")
        for a, b in (dir_changes + file_changes)[:10]:
            print(f"  {a}  ->  {b}")

    print("=== Rebrand %s ===" % ("APPLIED" if apply else "DRY RUN"))
    print("files with changes :", stats["changed"])
    print("binary skipped     :", stats["skipped_bin"])
    print("path renames       :", stats["renames"])
    print("skipped files      :", stats["skipped_files"])
    print("--- occurrences per rule (approx) ---")
    for rep, n in sorted(per_rule.items(), key=lambda x: -x[1]):
        print(f"  -> {rep:<12} {n}")
    print("OK")


if __name__ == "__main__":
    main()
