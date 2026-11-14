"""Tables for the typical-closure section (runs/me1d*.jsonl, runs/tc*.jsonl).  MEASURED."""
import json, collections
import numpy as np


def load(fn):
    try:
        return [json.loads(l) for l in open(fn)]
    except FileNotFoundError:
        return []


me = load("runs/me1d.jsonl")
rules = ["gauss", "edge3", "edge4", "maxent4"]
print("### Per-step closure error of next-layer means, 1D reduction (nMSE per step, mean over steps l>=1, median over nets)\n")
print("| n x L | exkurt(z) first / last layer | gauss (K=2) | edge3 (K=3) | edge4 (K=4) | maxent4 | e3/e2 | e4/e3 | sum over steps K=2 / 3 / 4 |")
print("|---|---|---|---|---|---|---|---|---|")
by = collections.defaultdict(list)
for r in me:
    by[(r["n"], r["L"])].append(r)
for (n, L) in sorted(by):
    rs = by[(n, L)]
    m = {k: np.median([np.mean(r["step"][k][1:]) for r in rs]) for k in rules}
    s = {k: np.median([np.sum(r["step"][k][1:]) for r in rs]) for k in rules}
    ek1 = np.median([r["exkurt"][1] for r in rs]); ekL = np.median([r["exkurt"][-1] for r in rs])
    print(f"| {n} x {L} | {ek1:.2f} / {ekL:.2f} | {m['gauss']:.1e} | {m['edge3']:.1e} | {m['edge4']:.1e} | {m['maxent4']:.1e} | "
          f"{m['edge3']/m['gauss']:.2f} | {m['edge4']/m['edge3']:.2f} | {s['gauss']:.1e} / {s['edge3']:.1e} / {s['edge4']:.1e} |")

print("\n### Per-step error vs layer (1D, K=2 / K=3 / K=4, median over nets) and excess kurtosis of z_l\n")
for (n, L) in sorted(by):
    rs = by[(n, L)]
    idx = sorted(set([1, 2, L // 4, L // 2, 3 * L // 4, L - 1]) - {0})
    idx = [i for i in idx if i < L]
    cells = []
    for i in idx:
        e = [np.median([r["step"][k][i] for r in rs]) for k in ("gauss", "edge3", "edge4")]
        ek = np.median([r["exkurt"][i] for r in rs])
        cells.append(f"l={i}: {e[0]:.1e}/{e[1]:.1e}/{e[2]:.1e} (ek {ek:.2f})")
    print(f"- {n} x {L}: " + "; ".join(cells))

tc = load("runs/tc.jsonl")
if tc:
    print("\n### ARC's own tensor step (tc.py) vs ARC's full recursion: final-layer nMSE and sum of per-step nMSE (median over nets)\n")
    print("| n x L | M | K | sum of per-step errors | recursion error at last layer | ratio rec/sum |")
    print("|---|---|---|---|---|---|")
    bt = collections.defaultdict(list)
    for r in tc:
        bt[(r["n"], r["L"], r["M"])].append(r)
    for key in sorted(bt):
        rs = bt[key]
        for k in rs[0]["Ks"]:
            ss = np.median([np.sum(r["step"][str(k)]) for r in rs])
            rc = np.median([r["rec"][str(k)][-1] for r in rs])
            print(f"| {key[0]} x {key[1]} | 2^{int(np.log2(key[2]))} | {k} | {ss:.1e} | {rc:.1e} | {rc/ss:.1f} |")

tcc = [r for r in tc if "cut" in r]
if tcc:
    print("\n### Cut experiment (ARC recursion started from TRUE cumulants at layer c; final-layer nMSE; median over nets)\\n")
    print("| n x L | K | e(c=0) = full recursion | e(c=1) | e(c=L/2) | e(c=L-1) = last step | sum_c |Delta_c|^2 | share of sum from first half of steps |")
    print("|---|---|---|---|---|---|---|---|")
    bc = collections.defaultdict(list)
    for r in tcc:
        bc[(r["n"], r["L"])].append(r)
    for (n, L) in sorted(bc):
        rs = bc[(n, L)]
        for k in rs[0]["Ks"]:
            k = str(k)
            c = lambda i: np.median([r["cut"][k][i] for r in rs])
            sd = np.median([np.sum(r["delta"][k]) for r in rs])
            sh = np.median([np.sum(r["delta"][k][:L // 2]) / np.sum(r["delta"][k]) for r in rs])
            print(f"| {n} x {L} | {k} | {c(0):.1e} | {c(1):.1e} | {c(L // 2):.1e} | {c(L - 1):.1e} | {sd:.1e} | {sh:.2f} |")
