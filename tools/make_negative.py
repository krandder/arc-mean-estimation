#!/usr/bin/env python3
"""Build NEGATIVE-RESULTS.md and records/lane-records.json from the per-lane extraction records.

Usage: make_negative.py NOTES_DIR REPO_DIR
"""
import json
import os
import re
import sys

notes, repo = sys.argv[1], sys.argv[2]
ORDER = ["arc-update", "scale-mode", "future-aware", "preint", "randomness", "adaptive-regions", "phase1-board",
         "cumulant-ambiguity", "moment-matching", "nd-exact", "unrestricted", "narrow-deep", "narrow-deep-m1",
         "arc-noisy", "algzoo-noisy", "boundary-family", "nongauss-family", "sparse-codes", "cm-interp-R",
         "estimability", "hardness", "lyapunov-dimension", "random-phases", "gate-entropy", "cut-rank", "cut-rank-ext",
         "kstar-frames", "tractable-gates", "stationary", "stationary-numerics", "input-bits", "gram-chain",
         "relevance", "bits-bounds", "bit-accounting", "bit-accounting-arc", "backward-bits",
         "arc-deep-networks-note", "synthesis-draft"]
PATH = {"arc-deep-networks-note": "reports/literature/arc-deep-networks-2026-10-29.md",
        "synthesis-draft": "reports/synthesis-draft-2026-11-02.md"}
recs = {}
for b in "ABCDE":
    for o in json.load(open(os.path.join(notes, "batch-%s.json" % b))):
        recs[o["lane"]] = o
assert set(recs) == set(ORDER), set(recs) ^ set(ORDER)


def clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().replace("|", "\\|")


L = [open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "negative_overview.md")).read().rstrip(), ""]
A = L.append
A("## Lane by lane")
A("")
A("Order: the 2-3 November lanes at the contest shape first, then exact and narrow-deep methods, the first week's")
A("families, theory, and bit accounting. Jump to a lane:")
A("")
A(" ".join("[`%s`](#%s)" % (l, l.lower()) for l in ORDER))
A("")
n_total = 0
for lane in ORDER:
    o = recs[lane]
    path = PATH.get(lane, "lanes/%s/" % lane)
    A("### %s" % lane)
    A("")
    A("Report: `%s` (%s). Final state: %s." % (o.get("report", ""), path, clean(o["date"])))
    A("")
    A("Headline: %s" % clean(o["claim"]))
    A("")
    A("Status: **%s**. %s" % (o["status"], clean(o["status_qualifier"])))
    A("")
    negs = o.get("negative_results", [])
    if negs:
        A("Failed approaches (%d):" % len(negs))
        A("")
    for i, e in enumerate(negs, 1):
        n_total += 1
        A("%d. **%s**" % (i, clean(e.get("approach"))))
        A("   - Tried: %s" % clean(e.get("tried")))
        A("   - Outcome: %s" % clean(e.get("outcome")))
        A("   - Why it failed: %s" % clean(e.get("why_failed")))
        A("   - Rules out: %s" % clean(e.get("rules_out")))
        A("   - Evidence: %s. Source: %s" % (clean(e.get("evidence_label")), clean(e.get("source"))))
    fp = o.get("failed_predictions", [])
    if fp:
        A("")
        A("Our own registered predictions that failed (%d):" % len(fp))
        A("")
        for x in fp:
            A("- %s" % clean(x))
    cor = [c for c in o.get("corrections", []) if c.get("direction") in ("corrected_by", "retracted", "superseded_by")]
    if cor:
        A("")
        A("Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (%d):" % len(cor))
        A("")
        for c in cor:
            A("- %s %s: %s (%s)" % ({"corrected_by": "Corrected by", "retracted": "Withdrawn;", "superseded_by": "Superseded by"}[c["direction"]],
                                    clean(c.get("other")), clean(c.get("what")), clean(c.get("source"))))
    for key, title in (("open_or_unfinished", "Not finished"), ("could_not_determine", "Could not be determined when extracting")):
        if clean(o.get(key)):
            A("")
            A("%s: %s" % (title, clean(o.get(key))))
    A("")
text = "\n".join(L) + "\n"
open(os.path.join(repo, "NEGATIVE-RESULTS.md"), "w").write(text)
os.makedirs(os.path.join(repo, "records"), exist_ok=True)
json.dump([recs[l] for l in ORDER], open(os.path.join(repo, "records", "lane-records.json"), "w"), indent=1, ensure_ascii=False)
print("entries", n_total, "bytes", len(text))
