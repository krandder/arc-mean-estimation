"""Tables for report.md from runs/ps_n*.jsonl (fixed code) and runs/gsweep.jsonl.  MEASURED."""
import json, glob, collections, sys
import numpy as np


def med(v):
    v = [x for x in v if x is not None]
    return f"{np.median(v):.2f}" if v else ""


recs = []
for fn in sorted(glob.glob("runs/ps_n[0-9].jsonl")) + sorted(glob.glob("runs/ps_n[0-9][0-9].jsonl")):
    recs += [json.loads(l) for l in open(fn)]
steps = [r for r in recs if r["type"] == "step"]
props = [r for r in recs if r["type"] == "prop"]

print("### Per-step closure spread of next-layer means (spread / sd, median over units and nets)\n")
by = collections.defaultdict(list)
for r in steps:
    by[(r["n"], r["layer"], r["d"])] += r["mean"]
ns = sorted({k[0] for k in by}); ds = sorted({k[2] for k in by})
print("| n | step l -> l+1 | " + " | ".join(f"d={d}" for d in ds) + " |")
print("|---|---|" + "---|" * len(ds))
for n in ns:
    for l in sorted({k[1] for k in by if k[0] == n}):
        print(f"| {n} | {l}->{l+1} | " + " | ".join(med(by.get((n, l, d), [])) for d in ds) + " |")

print("\n### Per-step spread of next-layer second moments E h_i^2 and E h_i h_j (median)\n")
by2 = collections.defaultdict(list)
for r in steps:
    by2[(r["n"], r["layer"], r["d"])] += r["sq"] + r["cross"]
print("| n | step | " + " | ".join(f"d={d}" for d in ds) + " |")
print("|---|---|" + "---|" * len(ds))
for n in ns:
    for l in sorted({k[1] for k in by2 if k[0] == n}):
        print(f"| {n} | {l}->{l+1} | " + " | ".join(med(by2.get((n, l, d), [])) for d in ds) + " |")

for tgt in ("unit", "readout"):
    print(f"\n### Output-mean ambiguity, target = {tgt} (spread / sd(f), median over nets): all / input / prop\n")
    bp = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in props:
        for k in ("all", "input", "prop"):
            bp[(r["n"], r["L"], r["d"])][k].append(r[tgt][k])
    Ls = sorted({k[1] for k in bp})
    print("| n | L | " + " | ".join(f"d={d}" for d in ds) + " |")
    print("|---|---|" + "---|" * len(ds))
    for n in ns:
        for L in Ls:
            cells = []
            for d in ds:
                c = bp.get((n, L, d))
                cells.append(f"{med(c['all'])} / {med(c['input'])} / {med(c['prop'])}" if c else "")
            if any(cells):
                print(f"| {n} | {L} | " + " | ".join(cells) + " |")

try:
    g = [json.loads(l) for l in open("runs/gsweep.jsonl")]
except FileNotFoundError:
    g = []
if g:
    print("\n### 1D bound Gamma_d / sd(relu t) for single last-layer units (median over units, 3 nets); kurtosis of t\n")
    gd = sorted({int(d) for r in g for d in r["g"]})
    bg = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in g:
        for d, v in r["g"].items():
            bg[(r["n"], r["L"])][int(d)].append(v)
        bg[(r["n"], r["L"])]["kurt"].append(r["kurt"])
    print("| n | L | kurt(t) | " + " | ".join(f"d={d}" for d in gd) + " |")
    print("|---|---|---|" + "---|" * len(gd))
    for (n, L) in sorted(bg):
        c = bg[(n, L)]
        print(f"| {n} | {L} | {np.median(c['kurt']):.1f} | " + " | ".join(med(c[d]) for d in gd) + " |")
