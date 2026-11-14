"""Tables for report.md from runs/cg_n*.jsonl. MEASURED (exploratory)."""
import json, glob, math, collections, sys
import numpy as np
recs = []
for fn in sorted(glob.glob("runs/cg_n*.jsonl")):
    for l in open(fn):
        r = json.loads(l)
        if r["type"] == "cg" and "gap_lo" in r:
            recs.append(r)
by = collections.defaultdict(dict)  # (n, name) -> d -> (lo, hi)
for r in recs:
    by[(r["n"], r["name"])][r["d"]] = (r["gap_lo"], r["gap_hi"])
ns = sorted({r["n"] for r in recs})
def fmt(t):
    lo, hi = t
    return f"{lo:.2f}-{hi:.2f}" if hi - lo > 0.005 else f"{lo:.2f}"
out = []
for n in ns:
    ds = sorted({r["d"] for r in recs if r["n"] == n})
    out.append(f"\n### n = {n}  (gap/sd, inner-outer bracket)\n")
    out.append("| net | " + " | ".join(f"d={d}" for d in ds) + " |")
    out.append("|---|" + "---|" * len(ds))
    names = ["linear_net0", "parity"] + [f"relu_L{L}_net{k}" for L in (1, 2, 4, 8) for k in range(3)]
    for nm in names:
        row = by.get((n, nm), {})
        out.append(f"| {nm} | " + " | ".join(fmt(row[d]) if d in row else "" for d in ds) + " |")
    out.append("\n| L | " + " | ".join(f"median d={d}" for d in ds) + " | ratio gap(dmax)/gap(2) (median) |")
    out.append("|---|" + "---|" * (len(ds) + 1))
    for L in (1, 2, 4, 8):
        meds = []
        for d in ds:
            v = [by[(n, f"relu_L{L}_net{k}")][d][0] for k in range(3) if d in by.get((n, f"relu_L{L}_net{k}"), {})]
            meds.append(np.median(v) if len(v) == 3 else None)
        rat = [by[(n, f"relu_L{L}_net{k}")][max(ds)][0] / by[(n, f"relu_L{L}_net{k}")][2][0]
               for k in range(3) if max(ds) in by.get((n, f"relu_L{L}_net{k}"), {})]
        tail = f" | {np.median(rat):.2f} |" if rat else " | |"
        out.append(f"| {L} | " + " | ".join(f"{m:.2f}" if m is not None else "" for m in meds) + tail)
print("\n".join(out))

# ---- degree needed for gap < 10% / 1% of sd: measured (<= dmax) or power-law extrapolation on even d >= 4
print("\n### Degree needed (gap_lo < 0.10 / 0.01 sd). 'fit' = extrapolation of gap ~ c d^-b over even d >= 4 (inner bounds)\n")
print("| n | net | dmax | gap_lo(dmax) | b (fit) | d@10% | d@1% |")
print("|---|---|---|---|---|---|---|")
fits = collections.defaultdict(list)
for n in ns:
    for L in (1, 2, 4, 8):
        for k in range(3):
            row = by.get((n, f"relu_L{L}_net{k}"), {})
            ev = sorted(d for d in row if d % 2 == 0 and d >= 4)
            dmax = max(row) if row else None
            meas10 = next((d for d in sorted(row) if row[d][0] < 0.10), None)
            meas1 = next((d for d in sorted(row) if row[d][0] < 0.01), None)
            if len(ev) >= 2:
                x = np.log(ev); y = np.log([row[d][0] for d in ev])
                b, a = np.polyfit(x, y, 1); b = -b
                d10 = math.exp((a - math.log(0.10)) / b) if b > 0 else float("inf")
                d1 = math.exp((a - math.log(0.01)) / b) if b > 0 else float("inf")
                fits[(n, L)].append((b, d10, d1))
                s10 = f"{meas10}" if meas10 else f"~{d10:.0f} (fit)"
                s1 = f"{meas1}" if meas1 else f"~{d1:.0f} (fit)"
                print(f"| {n} | L{L} net{k} | {dmax} | {row[dmax][0]:.3f} | {b:.2f} | {s10} | {s1} |")
            else:
                print(f"| {n} | L{L} net{k} | {dmax} | {row[dmax][0]:.3f} | - | >{dmax} | >{dmax} |")
print("\n| n | L | median b | median d@10% (fit) | median d@1% (fit) |")
print("|---|---|---|---|---|")
for (n, L), v in sorted(fits.items()):
    v = np.array(v)
    print(f"| {n} | {L} | {np.median(v[:,0]):.2f} | {np.median(v[:,1]):.0f} | {np.median(v[:,2]):.0f} |")
