"""Closure ambiguity of order-d moment propagation through random He-ReLU nets.  MEASURED (exploratory).

Point set X (N0 Gaussian base points, uniform weights = P0; N1 extra points from a scale mixture).
Layer maps h_l(x) as in lw.py; features of layer l = orthonormal (under P0) polynomials of degree 1..d
in the whitened coordinates of h_l (lw.constraint_matrix).

(1) per-step ("step"): over laws Q on X with E_Q p(h_l) = E_P0 p(h_l) for all deg p <= d (layer l
    only), the spread max - min of each next-layer statistic: means E h_{l+1,i} and second moments
    E h_{l+1,i} h_{l+1,j}, in units of their sd under P0.  This is the closure error per step that no
    order-d closure rule can avoid (for some law consistent with the true layer-l moments).
(2) propagated ("prop"): the sequential adversary.  Variables q^(0), ..., q^(L-1), each a probability
    vector on X;  m_0(q^(0)) = m_0(P0);  m_l(q^(l)) = m_l(q^(l-1)) for l = 1..L-1 (the layer-l moments
    handed on by step l-1 are realised by some law, which is then re-chosen).  Objective E_{q^(L-1)} f.
    Every consistent order-d closure path is feasible; P0 itself is one.  Spread = max - min.
    For comparison: "input" (one block, layer 0 matched, i.e. one law propagated exactly) and "all"
    (one block, every layer 0..L-1 matched).  PROVEN ordering: all <= input <= prop.
"""
import argparse, json, math, time
import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog
from lw import constraint_matrix, make_net, forward, sample_extra


def lp(c, A, b, valid=None):
    out = []
    bnd = (0, None) if valid is None else np.column_stack([np.zeros(len(c)), np.where(valid, np.inf, 0.0)])
    for s in (-1, 1):
        r = linprog(s * c, A_eq=A, b_eq=b, bounds=bnd, method="highs-ds",
                    options={"presolve": True, "time_limit": 3000})
        if r.status != 0:
            return None
        out.append(float(c @ r.x))
    return out[0] - out[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--L", type=int, nargs="+", required=True)
    ap.add_argument("--d", type=int, nargs="+", required=True)
    ap.add_argument("--N0", type=int, default=3000)
    ap.add_argument("--N1", type=int, default=3000)
    ap.add_argument("--nets", type=int, default=3)
    ap.add_argument("--what", nargs="+", default=["step", "prop"])
    ap.add_argument("--maxrank", type=int, default=1500)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    n = args.n
    rng = np.random.default_rng([3, n, args.N0, args.N1])
    X = np.vstack([rng.standard_normal((args.N0, n)), sample_extra(n, args.N1, rng)])
    N = len(X)
    w0 = np.zeros(N); w0[:args.N0] = 1.0 / args.N0
    Xtest = np.random.default_rng(99).standard_normal((1 << 16, n))
    for L in args.L:
        for k in range(args.nets):
            Ws, a, rej = make_net(n, L, k, Xtest)
            hs, f = forward(X, Ws, a)
            hs_full = hs + [np.maximum(hs[-1] @ Ws[-1].T, 0)]  # h_0 .. h_L
            sdf = float(np.sqrt(w0 @ (f - w0 @ f) ** 2))
            # last-layer unit target (largest sd), as in lw.py --target unit
            iu = int(np.argmax(hs_full[L].std(0))); fu = hs_full[L][:, iu]
            sdu = float(np.sqrt(w0 @ (fu - w0 @ fu) ** 2))
            for d in args.d:
                feats, vals = {}, {}
                for l in range(L):
                    A, b, r, _, v = constraint_matrix(hs, [l], d, w0)
                    feats[l] = A; vals[l] = v
                ranks = [feats[l].shape[0] - 1 for l in range(L)]
                base = dict(n=n, L=L, net=k, d=d, N0=args.N0, N1=args.N1, ranks=ranks, dead_rej=rej,
                            nvalid=[int(vals[l].sum()) for l in range(L)])
                if "step" in args.what:
                    for l in range(L):
                        A = feats[l]; b = np.zeros(A.shape[0]); b[0] = 1; V = vals[l]
                        H = hs_full[l + 1]
                        res = {"mean": [], "sq": [], "cross": []}
                        live = [i for i in range(n) if np.std(H[:, i]) > 1e-12]
                        for i in live:
                            g = H[:, i]; s = math.sqrt(w0 @ (g - w0 @ g) ** 2)
                            v = lp(g, A, b, V); res["mean"].append(None if v is None else v / s)
                        for i in live[:2]:
                            g = H[:, i] ** 2; s = math.sqrt(w0 @ (g - w0 @ g) ** 2)
                            v = lp(g, A, b, V); res["sq"].append(None if v is None else v / s)
                        if len(live) >= 2:
                            g = H[:, live[0]] * H[:, live[1]]; s = math.sqrt(w0 @ (g - w0 @ g) ** 2)
                            if s > 1e-12:
                                v = lp(g, A, b, V); res["cross"].append(None if v is None else v / s)
                        rec = dict(type="step", layer=l, nlive=len(live), **base, **res)
                        with open(args.out, "a") as fo:
                            fo.write(json.dumps(rec) + "\n")
                        mm = [x for x in res["mean"] if x is not None]
                        print(f"step n={n} L={L} net={k} d={d} l={l}->{l+1}: mean spread/sd "
                              f"median={np.median(mm) if mm else float('nan'):.3f} max={max(mm) if mm else float('nan'):.3f}",
                              flush=True)
                if "prop" in args.what:
                    if sum(ranks) > args.maxrank:
                        print(f"skip prop L={L} d={d} rank={sum(ranks)}", flush=True)
                        continue
                    t0 = time.time()
                    out = {}
                    # input-only and all-layers single-block LPs
                    Ai = feats[0]; bi = np.zeros(Ai.shape[0]); bi[0] = 1
                    Aa, ba, _, _, va = constraint_matrix(hs, list(range(L)), d, w0)
                    # sequential block LP
                    blocks, rows_b = [], []
                    Z = sp.csr_matrix((1, N))
                    ones = sp.csr_matrix(np.ones((1, N)))
                    R = []
                    for l in range(L):  # sum-to-one rows
                        R.append(sp.hstack([ones if j == l else Z for j in range(L)]))
                        rows_b.append(1.0)
                    M0 = sp.csr_matrix(feats[0][1:])
                    R.append(sp.hstack([M0] + [sp.csr_matrix((M0.shape[0], N))] * (L - 1)))
                    rows_b += [0.0] * M0.shape[0]
                    for l in range(1, L):
                        Ml = sp.csr_matrix(feats[l][1:])
                        Zl = sp.csr_matrix((Ml.shape[0], N))
                        R.append(sp.hstack([(-Ml if j == l - 1 else (Ml if j == l else Zl)) for j in range(L)]))
                        rows_b += [0.0] * Ml.shape[0]
                    Ap = sp.vstack(R).tocsr(); bp = np.array(rows_b)
                    for name, g, s in (("readout", f, sdf), ("unit", fu, sdu)):
                        gi = lp(g, Ai, bi, vals[0])
                        if L == 1:  # all = input = prop when only layer 0 exists
                            ga = gp = gi
                        else:
                            ga = lp(g, Aa, ba, va)
                            cp = np.concatenate([np.zeros(N * (L - 1)), g])
                            gp = lp(cp, Ap, bp, np.concatenate([vals[l] & vals[l + 1] if l + 1 < L else vals[l] for l in range(L)]))
                        out[name] = dict(input=None if gi is None else gi / s, all=None if ga is None else ga / s,
                                         prop=None if gp is None else gp / s)
                    rec = dict(type="prop", **base, t=round(time.time() - t0, 1), **out)
                    with open(args.out, "a") as fo:
                        fo.write(json.dumps(rec) + "\n")
                    print(f"prop n={n} L={L} net={k} d={d}: " + " ".join(
                        f"{nm}: all={v['all']} input={v['input']} prop={v['prop']}" for nm, v in out.items()),
                        f"t={rec['t']}s", flush=True)


if __name__ == "__main__":
    main()
