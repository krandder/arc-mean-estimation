#!/usr/bin/env python3
"""Make the ARC extract of the dated log outbox/overnight-report-2026-10-29.md.

The log covers every lane of that period (ARC, the in-context-Bayes mechanism study, scale-free combination,
cooperation toys, admin). This keeps a top-level bullet, with its indented lines, only if it mentions an ARC lane or
method, and drops bullets about other lanes, people or admin. Nothing inside a kept bullet is changed.

Usage: extract_log.py SRC DST DROP_WORDS_FILE
"""
import re
import sys

ARC = re.compile(r"(\bARC\b|\bM1\b|algzoo|kprop|cumulant|rqmc|\bMC\b|sampler|256 ?x ?32|32 ?x ?256|8 ?x ?256|narrow-deep|"
                 r"width-8|nd-exact|hardness|lyapunov|gate[- ]entropy|gate census|cut-rank|k\*|kstar|tractable[- ]gates|"
                 r"stationary|input-bits|gram[- ]chain|relevance|bit[- ]accounting|bits-bounds|backward-bits|bitarc|preint|"
                 r"pre-integration|randomness|future-aware|scale[- ]mode|adaptive-regions|learned[- ]experts|cone tree|"
                 r"phase1-board|leaderboard|moment[- ]matching|boundary[- ]famil|nongauss|sparse-code|unrestricted|"
                 r"random-phases|random[- ]net|phase R\b|estimab|kerdock|multilevel|mlmc|synthesis|mean estimation|"
                 r"deductive|sample-free)", re.I)
OTHER_LEAD = re.compile(r"^(- \S+( \(approx\.\))?|\d+\.) \**(Phase B|Scale-free|L[oö]b|World |Toy |Prudent|Modal|Workflow |Site|Landing)", re.I)
# Words that mark an entry as being about people or admin. The list holds first names, so it is kept in a file
# outside the repository and passed as the third argument (one regex alternative per line).
PERSONAL = None


def main(src, dst, words_file):
    global PERSONAL
    words = [w.strip() for w in open(words_file) if w.strip()]
    PERSONAL = re.compile(r"\b(" + "|".join(words) + r")\b", re.I)
    lines = open(src).read().split("\n")
    out, kept, dropped, dropped_personal = [], 0, 0, 0
    i = 0
    # header up to the first section
    while i < len(lines) and not lines[i].startswith("## "):
        i += 1
    block = None
    blocks = []
    for ln in lines[i:]:
        if ln.startswith("## "):
            blocks.append(("h", [ln]))
            block = None
        elif re.match(r"^(- |\d+\. )", ln):
            block = ("b", [ln])
            blocks.append(block)
        elif block is not None and (ln.startswith(" ") or ln == ""):
            block[1].append(ln)
        else:
            block = ("b", [ln])
            blocks.append(block)
    for kind, body in blocks:
        text = "\n".join(body)
        if kind == "h":
            out.append("")
            out.extend(body)
            continue
        if not text.strip():
            continue
        if PERSONAL.search(text):
            dropped_personal += 1
            continue
        if OTHER_LEAD.search(body[0]) and not re.search(r"\bARC\b|\bM1\b", text):
            dropped += 1
            continue
        if ARC.search(text):
            out.extend(body)
            kept += 1
        else:
            dropped += 1
    head = [
        "# ARC extract of the dated log (source: outbox/overnight-report-2026-10-29.md, opus-mats, 29 Oct - 3 Nov 2026)",
        "",
        "This is an extract, not the source file. The source log covers every lane of the period. `tools/extract_log.py`",
        "kept a log entry only if it mentions an ARC lane or method, and dropped entries about other research lines,",
        "people or admin. Kept entries are verbatim. Kept: %d entries. Dropped as not ARC: %d. Dropped because they name" % (kept, dropped),
        "people or admin matters: %d. Times are UTC; the log runs past its title date, to 3 November." % dropped_personal,
        "Dollar figures in entries are GPU list-price spends recorded by the lanes at the time.",
    ]
    open(dst, "w").write("\n".join(head + out) + "\n")
    print(kept, dropped, dropped_personal)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
