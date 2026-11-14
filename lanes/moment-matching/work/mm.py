"""Moment-matching LP gap for random bias-free He-ReLU nets. MEASURED (exploratory).

For a finite point set X (N points in R^n) solve
    max / min  sum_j q_j f(x_j)
    s.t.       q >= 0,  sum_j q_j He_alpha(x_j) = E_gauss He_alpha = [alpha == 0]   for all |alpha| <= d
(He_alpha = product of orthonormal probabilists' Hermite polynomials; alpha = 0 row is sum q = 1).
gap = (max - min) / sd_gauss(f).  The finite-support gap is a LOWER bound on the gap over all
measures; we report it at several N to check convergence.

The constraint matrix depends only on (X, d), so all objectives (nets, depths, controls) for one
(n, d, N) share one HiGHS model and are solved by warm-started simplex (cost change only).
"""
import argparse, itertools, json, math, os, sys, time
import numpy as np
from scipy.optimize._highspy import _core as hc


def multi_indices(n, d):
    out = []
    for tot in range(d + 1):
        for c in itertools.combinations_with_replacement(range(n), tot):
            a = [0] * n
            for i in c:
                a[i] += 1
            out.append(tuple(a))
    return out


def hermite_matrix(X, d):
    """Return A (M x N), rows = orthonormal multivariate Hermite polys at points."""
    N, n = X.shape
    H = np.empty((d + 1, N, n))
    H[0] = 1.0
    if d >= 1:
        H[1] = X
    for k in range(1, d):  # He_{k+1} = x He_k - k He_{k-1}  (unnormalized)
        H[k + 1] = X * H[k] - k * H[k - 1]
    for k in range(d + 1):
        H[k] /= math.sqrt(math.factorial(k))
    idx = multi_indices(n, d)
    A = np.empty((len(idx), N))
    for r, a in enumerate(idx):
        v = np.ones(N)
        for i, ai in enumerate(a):
            if ai:
                v = v * H[ai, :, i]
        A[r] = v
    return A, idx


SCALES = np.array([0.5, 1.0, 1.5, 2.0])
FRACS = np.array([0.15, 0.5, 0.2, 0.15])


def sample_points(n, N, seed):
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((N, n))
    s = rng.choice(SCALES, size=N, p=FRACS)
    return Z * s[:, None]


def make_net(n, L, seed, Xtest):
    """Independent net per (n, L, seed). Rejects nets whose output is identically 0 on a
    2^16-point Gaussian test sample (dead narrow ReLU nets); returns number of rejections."""
    rej = 0
    for t in range(1000):
        rng = np.random.default_rng([n, L, seed, t])
        Ws = [rng.standard_normal((n, n)) * math.sqrt(2.0 / n) for _ in range(L)]
        a = rng.standard_normal(n) / math.sqrt(n)
        if np.any(net_f(Xtest, Ws, a, L) != 0):
            return Ws, a, rej
        rej += 1
    raise RuntimeError("all nets dead")


def net_f(X, Ws, a, L):
    h = X.T
    for l in range(L):
        h = np.maximum(Ws[l] @ h, 0.0)
    return a @ h


def linear_f(X, seed):
    rng = np.random.default_rng(5000 + seed)
    w = rng.standard_normal(X.shape[1])
    return X @ w


def parity_f(X):
    # relu( prod_i sign(x_i) * min_i |x_i| ) ; under Gauss E f = 1/2 E min|G|,
    # under the sign-parity law (all (n-1)-wise marginals Gaussian) E f = E min|G| or 0.
    s = np.prod(np.sign(X), axis=1)
    return np.maximum(s * np.min(np.abs(X), axis=1), 0.0)


def objectives(X, n, Lmax_list, nets):
    objs = {}
    for (L, k), (Ws, a, _) in nets.items():
        objs[f"relu_L{L}_net{k}"] = net_f(X, Ws, a, L)
    for k in range(3):
        objs[f"linear_net{k}"] = linear_f(X, k)
    objs["parity"] = parity_f(X)
    return objs


def gauss_stats(n, Lmax_list, nets, M=1 << 20, seed=777):
    X = np.random.default_rng(seed).standard_normal((M, n))
    o = objectives(X, n, Lmax_list, nets)
    return {k: (float(v.mean()), float(v.std())) for k, v in o.items()}


def build_highs(A, b, threads=1):
    M, N = A.shape
    lp = hc.HighsLp()
    lp.num_col_ = N
    lp.num_row_ = M
    lp.col_cost_ = np.zeros(N)
    lp.col_lower_ = np.zeros(N)
    lp.col_upper_ = np.full(N, hc.kHighsInf)
    lp.row_lower_ = b.copy()
    lp.row_upper_ = b.copy()
    am = lp.a_matrix_
    am.format_ = hc.MatrixFormat.kColwise
    am.num_col_ = N
    am.num_row_ = M
    am.start_ = np.arange(0, M * N + 1, M, dtype=np.int32)
    am.index_ = np.tile(np.arange(M, dtype=np.int32), N)
    am.value_ = np.ascontiguousarray(A.T).ravel()
    lp.a_matrix_ = am
    h = hc._Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", threads)
    h.setOptionValue("presolve", "off")
    h.setOptionValue("time_limit", 3600.0)
    h.passModel(lp)
    return h


def solve(h, c, sense):
    N = len(c)
    h.changeColsCost(N, np.arange(N, dtype=np.int32), np.ascontiguousarray(c, dtype=np.float64))
    h.changeObjectiveSense(hc.ObjSense.kMaximize if sense > 0 else hc.ObjSense.kMinimize)
    t = time.time()
    h.run()
    st = h.modelStatusToString(h.getModelStatus())
    sol = h.getSolution()
    q = np.asarray(sol.col_value)
    return st, h.getObjectiveValue(), q, time.time() - t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--d", type=int, nargs="+", required=True)
    ap.add_argument("--N", type=int, nargs="+", required=True)
    ap.add_argument("--nets", type=int, default=3)
    ap.add_argument("--L", type=int, nargs="+", default=[1, 2, 4, 8])
    ap.add_argument("--maxnnz", type=float, default=8e7)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    n = args.n
    Xtest = np.random.default_rng(99).standard_normal((1 << 16, n))
    nets = {(L, k): make_net(n, L, k, Xtest) for L in args.L for k in range(args.nets)}
    gs = gauss_stats(n, args.L, nets)
    with open(args.out, "a") as fo:
        fo.write(json.dumps({"type": "gauss", "n": n, "stats": gs,
                             "dead_rejections": {f"L{L}_net{k}": v[2] for (L, k), v in nets.items()}}) + "\n")
    Xall = sample_points(n, max(args.N), args.seed)  # nested samples: smaller N is a prefix
    for d in args.d:
        Mrows = math.comb(n + d, d)
        for N in args.N:
            if Mrows * N > args.maxnnz:
                print(f"skip n={n} d={d} N={N} rows={Mrows}", flush=True)
                continue
            X = Xall[:N]
            t0 = time.time()
            A, idx = hermite_matrix(X, d)
            b = np.zeros(len(idx)); b[0] = 1.0
            h = build_highs(A, b)
            objs = objectives(X, n, args.L, nets)
            rec = {"type": "lp", "n": n, "d": d, "N": N, "rows": Mrows, "res": {}}
            for name, fv in objs.items():
                mu, sd = gs[name]
                r = {}
                for sense, key in ((1, "max"), (-1, "min")):
                    st, val, q, dt = solve(h, fv, sense)
                    resid = float(np.max(np.abs(A @ q - b))) if st == "Optimal" else None
                    r[key] = val; r[key + "_status"] = st; r[key + "_t"] = round(dt, 2)
                    r[key + "_resid"] = resid
                    r[key + "_support"] = int((q > 1e-12).sum()) if st == "Optimal" else None
                r["gap_sd"] = (r["max"] - r["min"]) / sd
                r["max_dev_sd"] = (r["max"] - mu) / sd
                r["min_dev_sd"] = (mu - r["min"]) / sd
                rec["res"][name] = r
                print(f"n={n} d={d} N={N} {name}: gap/sd={r['gap_sd']:.4f} "
                      f"[{r['max_status']},{r['min_status']}] t={r['max_t']}+{r['min_t']}s", flush=True)
                if r["max_status"] != "Optimal":
                    break  # infeasible/limit: same for all objectives
            rec["wall"] = round(time.time() - t0, 1)
            with open(args.out, "a") as fo:
                fo.write(json.dumps(rec) + "\n")
            del A, h


if __name__ == "__main__":
    main()
