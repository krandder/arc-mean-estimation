#!/usr/bin/env python3
"""Snapshot the ARC lanes into the repo tree.

Read-only on the sources. Copies a filtered snapshot of each lane work dir to
<repo>/lanes/<lane>/work/, the lane's report(s) to <repo>/lanes/<lane>/report/,
and writes <repo>/lanes/<lane>/PROVENANCE.md. Every exclusion is counted by
reason and written to <out>/exclusions.json.

Usage: collect.py --repo DIR --out DIR [--dry-run]
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys

WORK = "/srv/agent-data/home/workspaces/mats/work"
OUTBOX = "/srv/agent-data/home/workspaces/mats/outbox"
GH = "/srv/agent-data/home/workspaces/metaculus/work/arc-repo/src-inconsistency-search/mats"

# lane -> (work dir name or None, [outbox reports], [extra (src_abs, dest_rel)])
LANES = {
    "arc-noisy": ("arc-noisy", ["arc-noisy-deep-2026-10-29.md"], [
        (GH + "/reports/arc-noisy-review-2026-10-29", "review-from-github/arc-noisy-review-2026-10-29"),
        (GH + "/reports/arc-noisy-review2-2026-10-29", "review-from-github/arc-noisy-review2-2026-10-29"),
    ]),
    "arc-update": ("arc-update", ["arc-update-2026-11-02.md"], []),
    "algzoo-noisy": ("algzoo-noisy", ["algzoo-noisy-2026-10-29.md", "lit-width-sparsity-2026-10-29.md"], []),
    "boundary-family": ("boundary-family", ["boundary-family-2026-10-29.md"], []),
    "nongauss-family": ("nongauss-family", ["nongauss-family-2026-10-29.md"], []),
    "sparse-codes": ("sparse-codes", ["sparse-codes-2026-10-29.md"], []),
    "narrow-deep": ("narrow-deep", ["narrow-deep-2026-10-29.md"], [
        (GH + "/interp/narrow-deep", "only-in-github"),
    ]),
    "narrow-deep-m1": ("narrow-deep-m1", ["narrow-deep-m1-2026-10-30.md"], [
        (GH + "/interp/narrow-deep-m1", "only-in-github"),
    ]),
    "nd-exact": ("nd-exact", ["nd-exact-2026-11-02.md"], []),
    "unrestricted": ("unrestricted", ["unrestricted-estimators-2026-10-31.md"], []),
    "hardness": ("hardness", ["hardness-mean-estimation-2026-10-29.md"], [
        (GH + "/interp/hardness", "only-in-github"),
    ]),
    "lyapunov-dimension": ("lyapunov-dimension", ["lyapunov-dimension-2026-10-29.md"], []),
    "random-phases": ("random-phases", ["random-net-phases-2026-10-29.md"], []),
    "gate-entropy": ("gate-entropy", ["gate-entropy-2026-10-29.md"], []),
    "cut-rank": ("cut-rank", ["cut-rank-lower-bound-2026-10-30.md"], []),
    "cut-rank-ext": ("cut-rank-ext", ["cut-rank-ext-2026-10-31.md"], []),
    "kstar-frames": ("kstar-frames", ["kstar-frames-2026-10-30.md"], []),
    "tractable-gates": ("tractable-gates", ["tractable-gates-2026-10-31.md"], []),
    "stationary": ("stationary", ["stationary-regime-2026-10-31.md"], []),
    "stationary-numerics": ("stationary-numerics", ["stationary-numerics-2026-10-31.md"], []),
    "input-bits": ("input-bits", ["input-bits-2026-10-31.md"], []),
    "gram-chain": ("gram-chain", ["gram-chain-2026-11-01.md", "gram-chain-explainer-2026-11-01.md"], [
        (WORK + "/explainers/gram-chain-explainer.html", "report/gram-chain-explainer.html"),
    ]),
    "relevance": ("relevance", ["relevance-accounting-2026-11-01.md"], []),
    "bits-bounds": ("bits-bounds", ["bits-bounds-2026-11-01.md"], []),
    "bit-accounting": ("bit-accounting", ["bit-accounting-2026-11-02.md"], []),
    "bit-accounting-arc": ("bit-accounting-arc", ["bit-accounting-arc-2026-11-02.md"], []),
    "backward-bits": ("backward-bits", ["backward-bits-2026-11-02.md"], []),
    "preint": ("preint", ["preint-2026-11-02.md"], []),
    "randomness": ("randomness", ["randomness-2026-11-02.md"], []),
    "future-aware": ("future-aware", ["future-aware-2026-11-02.md"], []),
    "scale-mode": ("scale-mode", ["scale-mode-2026-11-02.md"], []),
    "adaptive-regions": ("adaptive-regions", ["adaptive-regions-2026-11-03.md"], []),
    "phase1-board": ("phase1-board", [], []),
    "moment-matching": ("moment-matching", ["moment-matching-2026-11-03.md"], []),
    "cumulant-ambiguity": ("cumulant-ambiguity", ["cumulant-ambiguity-2026-11-03.md"], []),
    "cm-interp-R": ("cm-interp-R", ["cm-interp-random-2026-10-28.md"], []),
    "estimability": ("estimability", ["estimability-penalty-2026-10-27.md"], []),
}

HARD_MAX = 5 * 1024 * 1024       # rule: nothing over 5 MB
SOFT_MAX = 1 * 1024 * 1024       # machine output (json/log/...) over 1 MB is not a "small result file"
SOFT_EXT = {"json", "jsonl", "log", "out", "err", "txt", "csv", "tsv", "html", "xml"}

DIR_RULES = {
    ".git": "vendored third-party git repository",
    "__pycache__": "cache",
    ".pytest_cache": "cache",
    ".mypy_cache": "cache",
    ".cache": "cache",
    ".ipynb_checkpoints": "cache",
    ".venv": "virtualenv",
    "venv": "virtualenv",
    "node_modules": "virtualenv",
    "wandb": "cache",
    "infra": "GPU infra state (holds an SSH private key)",
    "downloads": "third-party downloads (forum pages, other people's code and data)",
    "thirdparty": "third-party code",
    "papers": "third-party papers (PDF/text of published papers)",
    "tp": "third-party code",
    "arcnotes": "third-party papers (PDF/text of published papers)",
    "mlp_cumulant_propagation": "vendored third-party git repository",
    "alg-zoo": "vendored third-party git repository",
    "whest-starterkit": "vendored third-party git repository",
    "whestbench": "vendored third-party git repository",
    "flopscope": "vendored third-party git repository",
    "scale-separation": "vendored third-party git repository",
    "checkpoints": "checkpoints",
    "ckpt": "checkpoints",
    "ckpts": "checkpoints",
}
BIN_EXT = {"pt", "pth", "npz", "npy", "parquet", "pyc", "pyo", "pack", "idx", "rev", "bin", "safetensors",
           "ckpt", "h5", "hdf5", "db", "sqlite", "pkl", "pickle", "joblib", "zip", "tar", "gz", "tgz", "xz",
           "bz2", "so", "o", "whl"}
STATE_EXT = {"lock", "pid", "started", "done", "claimed", "promisor"}
SECRET_NAME = re.compile(r"(^\.env|\.pem$|\.key$|\.pub$|^id_(rsa|dsa|ecdsa|ed25519)|ed25519|credential|\.token$|secret)", re.I)
TRANSCRIPT_HEAD = re.compile(rb"(Reading additional input from stdin|OpenAI Codex v\d|\"parentUuid\"|\"sessionId\"|\"tool_use_id\")")


RECALL_HEAD = re.compile(rb"^recall: (querying|session hits)", re.M)
TOOLCALL = re.compile(r"^(hook: PreToolUse|exec)$", re.M)


def is_transcript(path, h):
    """A model session dump: Codex/Claude header, or tool-call traces anywhere in a text file."""
    if TRANSCRIPT_HEAD.search(h):
        return True
    ext = path.rsplit(".", 1)[-1].lower()
    if ext not in {"md", "txt", "raw", "out", "err", "log"}:
        return False
    try:
        if os.path.getsize(path) > HARD_MAX:
            return False
        text = open(path, "r", errors="replace").read()
    except OSError:
        return False
    return bool(TOOLCALL.search(text)) and ("/bin/bash -lc" in text or "hook: PreToolUse" in text)


def is_git_repo(path):
    return os.path.exists(os.path.join(path, ".git"))


def head(path, n=600):
    try:
        with open(path, "rb") as f:
            return f.read(n)
    except OSError:
        return b""


def extract_codex_final(path):
    """Return the reviewer's final message from a Codex CLI session dump, or None."""
    try:
        text = open(path, "r", errors="replace").read()
    except OSError:
        return None
    lines = text.split("\n")
    last = None
    for i, ln in enumerate(lines):
        if ln.strip() == "codex":
            last = i
    if last is None:
        return None
    end = len(lines)
    for i in range(last + 1, len(lines)):
        if lines[i].strip() == "tokens used":
            end = i
            break
    body = "\n".join(lines[last + 1:end]).strip()
    return body or None


import hashlib
import subprocess

TP_HASHES = set()
TP_REPOS = {}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_third_party(reason):
    return reason and ("third-party" in reason)


def prepass(lane, src):
    """Hash every file inside third-party dirs so that copies elsewhere in the lanes are left out too."""
    for root, dirs, files in os.walk(src, topdown=True):
        keep = []
        for d in sorted(dirs):
            p = os.path.join(root, d)
            if os.path.islink(p):
                continue
            reason = DIR_RULES.get(d)
            if reason is None and is_git_repo(p):
                reason = "vendored third-party git repository"
            if is_third_party(reason):
                for r2, d2, f2 in os.walk(p):
                    if ".git" in d2 or ".git" in f2:
                        try:
                            url = subprocess.run(["git", "-C", r2, "config", "--get", "remote.origin.url"],
                                                 capture_output=True, text=True).stdout.strip()
                            rev = subprocess.run(["git", "-C", r2, "rev-parse", "--short", "HEAD"],
                                                 capture_output=True, text=True).stdout.strip()
                            TP_REPOS.setdefault(lane, []).append((os.path.relpath(r2, src), url, rev))
                        except OSError:
                            pass
                    d2[:] = [x for x in d2 if x != ".git"]
                    for f in f2:
                        q = os.path.join(r2, f)
                        try:
                            if not os.path.islink(q) and 200 < os.path.getsize(q) <= HARD_MAX:
                                TP_HASHES.add(sha(q))
                        except OSError:
                            pass
                continue
            if reason:
                continue
            keep.append(d)
        dirs[:] = keep


class Tally:
    def __init__(self):
        self.d = {}
        self.big = []
        self.transcripts = []

    def add(self, lane, reason, nbytes, n=1):
        k = self.d.setdefault(lane, {}).setdefault(reason, [0, 0])
        k[0] += n
        k[1] += nbytes


def dir_size(path):
    n = b = 0
    for r, ds, fs in os.walk(path):
        for f in fs:
            p = os.path.join(r, f)
            if not os.path.islink(p):
                try:
                    b += os.path.getsize(p)
                    n += 1
                except OSError:
                    pass
    return n, b


def copy_tree(lane, src, dst, tally, dry, stats):
    for root, dirs, files in os.walk(src, topdown=True):
        keep = []
        for d in sorted(dirs):
            p = os.path.join(root, d)
            if os.path.islink(p):
                tally.add(lane, "symlink", 0)
                continue
            reason = DIR_RULES.get(d)
            if reason is None and is_git_repo(p):
                reason = "vendored third-party git repository"
            if reason:
                n, b = dir_size(p)
                tally.add(lane, reason, b, n)
                continue
            keep.append(d)
        dirs[:] = keep
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, src)
            if os.path.islink(p):
                tally.add(lane, "symlink", 0)
                continue
            try:
                size = os.path.getsize(p)
            except OSError:
                continue
            ext = f.rsplit(".", 1)[1].lower() if "." in f else ""
            if SECRET_NAME.search(f):
                tally.add(lane, "secret-like file name", size)
                continue
            if ext in BIN_EXT:
                tally.add(lane, "checkpoint / array / binary (" + ext + ")", size)
                if size > HARD_MAX:
                    tally.big.append((lane, rel, size))
                continue
            if ext in STATE_EXT:
                tally.add(lane, "job-queue state marker", size)
                continue
            if size > HARD_MAX:
                tally.add(lane, "over 5 MB", size)
                tally.big.append((lane, rel, size))
                continue
            h = head(p)
            if RECALL_HEAD.search(h):
                tally.add(lane, "fleet memory recall output (past conversation text)", size)
                continue
            if is_transcript(p, h):
                tally.add(lane, "agent/model session transcript", size)
                stem = p.rsplit(".", 1)[0]
                has_answer = any(os.path.exists(stem + sfx) and not is_transcript(stem + sfx, head(stem + sfx))
                                 for sfx in (".out", ".md", "_answer.md") if stem + sfx != p)
                final = None if has_answer else (extract_codex_final(p) if b"Codex" in h else None)
                tally.transcripts.append((lane, rel, size, "sibling-answer" if has_answer else (final is not None)))
                if final is not None and not dry:
                    out = os.path.join(dst, rel + ".final-message.md")
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    with open(out, "w") as g:
                        g.write("<!-- Extracted: the reviewer/co-prover model's final message only. The full session "
                                "dump (prompt echo, tool calls, intermediate output) is not in this repo. "
                                "Source file: work/%s/%s -->\n\n" % (lane, rel))
                        g.write(final + "\n")
                    stats["extracted"] += 1
                continue
            if ext in SOFT_EXT and size > SOFT_MAX:
                tally.add(lane, "machine output over 1 MB (" + ext + ")", size)
                continue
            if b"\0" in h and ext not in {"png", "gif", "jpg", "jpeg", "pdf", "svg"}:
                tally.add(lane, "binary without known research format", size)
                continue
            if size > 200 and sha(p) in TP_HASHES:
                tally.add(lane, "identical copy of a third-party file", size)
                continue
            stats["files"] += 1
            stats["bytes"] += size
            if not dry:
                out = os.path.join(dst, rel)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                shutil.copy2(p, out)


def iso(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    tally = Tally()
    now = dt.datetime.now(dt.timezone.utc)
    summary = {}
    for lane, (wd, reports, extra) in LANES.items():
        if wd and os.path.isdir(os.path.join(WORK, wd)):
            prepass(lane, os.path.join(WORK, wd))
    for lane, (wd, reports, extra) in LANES.items():
        dst = os.path.join(a.repo, "lanes", lane)
        stats = {"files": 0, "bytes": 0, "extracted": 0}
        src = os.path.join(WORK, wd) if wd else None
        all_mt = []
        if src and os.path.isdir(src):
            for r, ds, fs in os.walk(src):
                ds[:] = [d for d in ds if d not in (".git",)]
                for f in fs:
                    p = os.path.join(r, f)
                    if not os.path.islink(p):
                        try:
                            all_mt.append(os.path.getmtime(p))
                        except OSError:
                            pass
            copy_tree(lane, src, os.path.join(dst, "work"), tally, a.dry_run, stats)
        rep_rows = []
        for rp in reports:
            p = os.path.join(OUTBOX, rp)
            rep_rows.append((rp, os.path.getsize(p), os.path.getmtime(p)))
            if not a.dry_run:
                os.makedirs(os.path.join(dst, "report"), exist_ok=True)
                shutil.copy2(p, os.path.join(dst, "report", rp))
        for (s, d) in extra:
            if os.path.isdir(s):
                if d == "only-in-github":
                    for r, ds, fs in os.walk(s):
                        for f in fs:
                            p = os.path.join(r, f)
                            rel = os.path.relpath(p, s)
                            if not os.path.exists(os.path.join(src, rel)):
                                if not a.dry_run:
                                    out = os.path.join(dst, d, rel)
                                    os.makedirs(os.path.dirname(out), exist_ok=True)
                                    shutil.copy2(p, out)
                                stats["files"] += 1
                else:
                    copy_tree(lane, s, os.path.join(dst, d), tally, a.dry_run, stats)
            elif os.path.isfile(s) and not a.dry_run:
                out = os.path.join(dst, d)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                shutil.copy2(s, out)
        newest = max(all_mt) if all_mt else None
        oldest = min(all_mt) if all_mt else None
        in_progress = bool(newest and (now.timestamp() - newest) < 86400)
        summary[lane] = {
            "work_dir": src, "reports": [r[0] for r in rep_rows],
            "files_copied": stats["files"], "bytes_copied": stats["bytes"],
            "final_messages_extracted": stats["extracted"],
            "source_oldest": iso(oldest) if oldest else None, "source_newest": iso(newest) if newest else None,
            "in_progress_24h": in_progress,
            "excluded": tally.d.get(lane, {}),
            "third_party_repos": [(r, ("withheld" if not ("alignment-research-center" in u or "AIcrowd" in u) else u), v) for (r, u, v) in TP_REPOS.get(lane, [])],
        }
        if not a.dry_run:
            os.makedirs(dst, exist_ok=True)
            with open(os.path.join(dst, "PROVENANCE.md"), "w") as g:
                g.write("# Provenance: %s\n\n" % lane)
                g.write("Snapshot taken %s. The sources were copied, not moved or edited.\n\n" % now.strftime("%Y-%m-%d %H:%MZ"))
                if src:
                    g.write("- Original work dir: `%s/` (host General)\n" % src)
                    g.write("- Source file dates: %s to %s (mtime, UTC)\n" % (iso(oldest), iso(newest)))
                    g.write("- Modified in the 24 h before the snapshot: %s\n" % ("YES, the lane may be in progress" if in_progress else "no"))
                for (rp, sz, mt) in rep_rows:
                    g.write("- Report: `report/%s`, from `%s/%s` (last modified %s)\n" % (rp, OUTBOX, rp, iso(mt)))
                for (s, d) in extra:
                    g.write("- Also: `%s` from `%s`\n" % (d, s.replace(GH, "github futarchy-fi/inconsistency-search@647f3be:mats")))
                g.write("- Files copied into `work/`: %d (%.1f MB)\n" % (stats["files"], stats["bytes"] / 1048576))
                for (rel, url, rev) in TP_REPOS.get(lane, []):
                    if "alignment-research-center" in url or "AIcrowd" in url:
                        g.write("- Third-party code not copied: `%s` = %s at commit %s\n" % (rel, url, rev))
                    else:
                        g.write("- Third-party code not copied: `%s` = a contest participant's public repository at commit %s "
                                "(no licence file; its address is in the lane's own notes; see `OPEN-DECISIONS.md`)\n" % (rel, rev))
                if stats["extracted"]:
                    g.write("- `*.final-message.md` (%d files): the final message of a reviewer or co-prover model session, "
                            "extracted from a session dump that is itself excluded as a transcript. These files do not exist "
                            "at the source.\n" % stats["extracted"])
                ex = tally.d.get(lane, {})
                if ex:
                    g.write("\n## Left out of this snapshot\n\n| reason | files | MB |\n|---|---|---|\n")
                    for reason, (n, b) in sorted(ex.items(), key=lambda kv: -kv[1][1]):
                        g.write("| %s | %d | %.1f |\n" % (reason, n, b / 1048576))
                g.write("\nStatus, claim and corrections for this lane are in the top-level `README.md`; failed approaches are in "
                        "`NEGATIVE-RESULTS.md`.\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "exclusions.json"), "w") as g:
        json.dump({"summary": summary, "over_5mb": tally.big, "transcripts": tally.transcripts}, g, indent=1)
    tot_f = sum(v["files_copied"] for v in summary.values())
    tot_b = sum(v["bytes_copied"] for v in summary.values())
    for lane, v in summary.items():
        print("%-20s files=%5d MB=%7.1f newest=%s inprog=%s extracted=%d" % (
            lane, v["files_copied"], v["bytes_copied"] / 1048576, v["source_newest"], v["in_progress_24h"],
            v["final_messages_extracted"]))
    print("TOTAL files=%d MB=%.1f over5MB=%d transcripts=%d" % (tot_f, tot_b / 1048576, len(tally.big), len(tally.transcripts)))


if __name__ == "__main__":
    sys.exit(main())
