"""Layer-wise moment-matched ambiguity of the output mean of random bias-free He-ReLU nets.
MEASURED (exploratory).

Two input laws on a common finite point set X (rows x_j in R^n):
  base world P0 : uniform on the first N0 points (an N0-sample of N(0, I_n));
  alt  world Q  : any probability vector q >= 0 on all N0 + N1 points (N1 extra points
                  drawn from a Gaussian scale mixture, so Q can put mass outside the sample).
Constraint ("cumulants up to order d agree at layer l"): for every polynomial p of degree <= d
in the n coordinates of the post-activation h_l,  E_Q p(h_l) = E_P0 p(h_l).
(Equal moments up to order d <=> equal cumulants up to order d.)
Layers matched (mode):
  input : h_0 = x only                          (the sibling lane's question, finite-support version)
  last  : h_{L-1} only                          (the last hidden layer, which fixes all moments of
                                                 the output pre-activation z_L = W_L h_{L-1})
  all   : h_0, h_1, ..., h_{L-1}                (every layer below the output)
Output f(x) = a . relu(W_L h_{L-1}).  Matching h_L itself at order >= 1 would fix E f trivially
(E f = a . E h_L), so "every layer up to the output" means up to the last hidden layer.
Reported: gap = (max_Q E_Q f - min_Q E_Q f) / sd_P0(f).  Both extremal Q are explicit laws whose
layer-wise moments up to order d equal P0's at every matched layer, so gap is an exact statement
about two (three) explicit discrete laws; it lower-bounds the ambiguity over all laws matching P0.
"""
import argparse, itertools, json, math, os, sys, time
import numpy as np
from scipy.optimize import linprog
from oned_bound import gamma_d


def multi_indices(k, d):
    out = []
    for tot in range(1, d + 1):
        for c in itertools.combinations_with_replacement(range(k), tot):
            a = [0] * k
            for i in c:
                a[i] += 1
            out.append(tuple(a))
    return out


def herm_feats(Y, d):
    """Products of orthonormal probabilists' Hermite polys of the columns of Y, degree 1..d."""
    N, k = Y.shape
    H = np.empty((d + 1, N, k))
    H[0] = 1.0
    if d >= 1:
        H[1] = Y
    for j in range(1, d):
        H[j + 1] = Y * H[j] - j * H[j - 1]
    for j in range(d + 1):
        H[j] /= math.sqrt(math.factorial(j))
    idx = multi_indices(k, d)
    F = np.empty((N, len(idx)))
    for r, a in enumerate(idx):
        v = np.ones(N)
        for i, ai in enumerate(a):
            if ai:
                v = v * H[ai, :, i]
        F[:, r] = v
    return F


def null_ok(P, w0):
    """Points whose projections on directions that are (near-)null under the base stay within the
    base's own range there.  Laws on such points satisfy the dropped constraints up to the base's
    own (near-zero) spread; other points are excluded from the support (co-prover r1 fix)."""
    if P.shape[1] == 0:
        return np.ones(P.shape[0], bool)
    base = w0 > 0
    m = np.abs(P[base]).max(0)
    scale = max(np.abs(P).max(), 1e-300)
    return np.all(np.abs(P) <= 1.01 * m + 1e-9 * scale, axis=1)


def whiten(Hl, w0, tol=1e-9, return_valid=False):
    """Center/whiten layer activations under base weights w0; drop near-null directions."""
    mu = w0 @ Hl
    C = (Hl - mu).T @ ((Hl - mu) * w0[:, None])
    ev, V = np.linalg.eigh(C)
    keep = ev > tol * max(ev.max(), 1e-300)
    Y = (Hl - mu) @ (V[:, keep] / np.sqrt(ev[keep]))
    if return_valid:
        return Y, null_ok((Hl - mu) @ V[:, ~keep], w0)
    return Y


def make_net(n, L, seed, Xtest, act="relu"):
    """Same seeding as work/moment-matching/mm.py so nets are comparable across lanes."""
    rej = 0
    for t in range(1000):
        rng = np.random.default_rng([n, L, seed, t])
        Ws = [rng.standard_normal((n, n)) * math.sqrt(2.0 / n) for _ in range(L)]
        a = rng.standard_normal(n) / math.sqrt(n)
        if act != "relu" or np.any(forward(Xtest, Ws, a)[1] != 0):
            return Ws, a, rej
        rej += 1
    raise RuntimeError("all nets dead")


def forward(X, Ws, a, act="relu"):
    """Returns ([h_0, ..., h_{L-1}], f)."""
    hs = [X]
    h = X
    for l, W in enumerate(Ws):
        z = h @ W.T
        h = np.maximum(z, 0.0) if act == "relu" else z
        if l < len(Ws) - 1:
            hs.append(h)
    return hs, h @ a


def constraint_matrix(hs, layers, d, w0, tol=1e-10):
    """Stack features of matched layers, orthonormalize under P0, return (A, b) with
    A rows = orthonormal (under P0) centered features, plus the sum-to-one row."""
    blocks = []
    valid = np.ones(len(w0), bool)
    for l in layers:
        Y, v = whiten(hs[l], w0, return_valid=True)
        valid &= v
        if Y.shape[1] == 0:
            continue
        blocks.append(herm_feats(Y, d))
    F = np.concatenate(blocks, axis=1) if blocks else np.zeros((len(w0), 0))
    F = F - w0 @ F
    G = F.T @ (F * w0[:, None])
    ev, V = np.linalg.eigh(G)
    keep = ev > tol * max(ev.max(), 1e-300)
    T = V[:, keep] / np.sqrt(ev[keep])
    valid &= null_ok(F @ V[:, ~keep], w0)
    A = (F @ T).T  # rank x N, zero mean under w0
    A = np.vstack([np.ones((1, F.shape[0])), A])
    b = np.zeros(A.shape[0]); b[0] = 1.0
    return A, b, int(keep.sum()), F.shape[1], valid


def lp_gap(A, b, f, sd, valid=None):
    vals, info = {}, {}
    for s, key in ((-1, "max"), (1, "min")):
        ub = None if valid is None else np.where(valid, np.inf, 0.0)
        bnd = (0, None) if ub is None else np.column_stack([np.zeros(len(f)), ub])
        r = linprog(s * f, A_eq=A, b_eq=b, bounds=bnd, method="highs-ds",
                    options={"presolve": False, "time_limit": 3000})
        if r.status != 0:
            return None, {"status": r.message}
        q = r.x
        vals[key] = float(f @ q)
        info[key + "_resid"] = float(np.max(np.abs(A @ q - b)))
        info[key + "_support"] = int((q > 1e-12).sum())
    return (vals["max"] - vals["min"]) / sd, {**vals, **info}


def sample_extra(n, N1, rng):
    s = rng.choice([0.5, 1.0, 1.5, 2.0, 3.0], size=N1, p=[0.15, 0.4, 0.2, 0.15, 0.1])
    return rng.standard_normal((N1, n)) * s[:, None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--L", type=int, nargs="+", default=[1, 2, 4, 8])
    ap.add_argument("--d", type=int, nargs="+", required=True)
    ap.add_argument("--N0", type=int, default=4000)
    ap.add_argument("--N1", type=int, default=4000)
    ap.add_argument("--nets", type=int, default=3)
    ap.add_argument("--modes", nargs="+", default=["input", "last", "all"])
    ap.add_argument("--act", default="relu")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--target", default="readout", choices=["readout", "unit"])
    ap.add_argument("--maxrank", type=int, default=10**9)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    n = args.n
    rng = np.random.default_rng([args.seed, n, args.N0, args.N1])
    X = np.vstack([rng.standard_normal((args.N0, n)), sample_extra(n, args.N1, rng)])
    w0 = np.zeros(len(X)); w0[:args.N0] = 1.0 / args.N0
    Xtest = np.random.default_rng(99).standard_normal((1 << 16, n))
    for L in args.L:
        for k in range(args.nets):
            Ws, a, rej = make_net(n, L, k, Xtest, args.act)
            hs, f = forward(X, Ws, a, args.act)
            if args.target == "unit":  # f = one last-layer unit (the one with largest sd)
                zz = np.maximum(hs[-1] @ Ws[-1].T, 0) if args.act == "relu" else hs[-1] @ Ws[-1].T
                i0 = int(np.argmax(zz.std(0)))
                a = np.zeros(n); a[i0] = 1.0
                f = zz[:, i0]
            mu = float(w0 @ f); sd = float(math.sqrt(w0 @ (f - mu) ** 2))
            zL = hs[-1] @ Ws[-1].T
            for d in args.d:
                ob = []
                for i in range(n):
                    g1, s1 = gamma_d(zL[:, i], w0, d)
                    ob.append(g1)
                bound = sum(abs(a[i]) * ob[i] for i in range(n)) / sd if None not in ob else None
                with open(args.out, "a") as fo:
                    fo.write(json.dumps(dict(type="bound1d", target=args.target, n=n, L=L, net=k, d=d, act=args.act,
                                             gamma=ob, a=a.tolist(), sd=sd, bound_sd=bound)) + "\n")
                for mode in args.modes:
                    layers = {"input": [0], "last": [L - 1], "all": list(range(L))}[mode]
                    if mode != "input" and L == 1:
                        continue  # identical to input
                    t0 = time.time()
                    A, b, rank, nf, valid = constraint_matrix(hs, layers, d, w0)
                    if rank > args.maxrank:
                        print(f"skip L={L} d={d} {mode} rank={rank}", flush=True)
                        continue
                    gap, info = lp_gap(A, b, f, sd, valid)
                    rec = dict(target=args.target, n=n, L=L, net=k, d=d, mode=mode, act=args.act, N0=args.N0,
                               N1=args.N1, rank=rank, nfeat=nf, nvalid=int(valid.sum()), mu=mu, sd=sd, gap_sd=gap,
                               t=round(time.time() - t0, 1), dead_rej=rej, **info)
                    with open(args.out, "a") as fo:
                        fo.write(json.dumps(rec) + "\n")
                    g = f"{gap:.4f}" if gap is not None else "FAIL"
                    print(f"n={n} L={L} net={k} d={d} {mode}: rank={rank} gap/sd={g} t={rec['t']}s",
                          flush=True)


if __name__ == "__main__":
    main()
