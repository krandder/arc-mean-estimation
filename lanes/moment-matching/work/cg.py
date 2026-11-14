"""Moment-matching LP gap by column generation over the continuum. MEASURED (exploratory).

Primal (for s = +1 max, s = -1 min):  opt_s = max_q  s * sum_j q_j f(x_j)
    q >= 0, sum_j q_j He_alpha(x_j) = [alpha == 0] for |alpha| <= d  (orthonormal Hermite; alpha=0 row: sum q = 1)
We solve the HiGHS LP as a minimisation of c = -s f over a growing finite set of points, and price
new points over the continuum using positive homogeneity: f(r u) = r f(u), so for a direction u
the reduced cost  rc(r u) = -s r f(u) - y . He(r u)  is (degree-1 term) - (polynomial of degree d in r);
we interpolate the polynomial exactly at d+1 Chebyshev radii and minimise over a fine radius grid.

Bounds:  LP value on the current points is attained by a real measure -> inner bound.
         Weak duality: for every moment-matching probability measure mu,
         E_mu c >= y.b + min_x rc(x) = LP + min rc   -> outer bound, with min rc taken over a
         large sampled pool of directions x radius grid (r <= Rmax) [sampled, not certified].
gap_lo = (max_inner - min_inner)/sd,  gap_hi = (max_outer - min_outer)/sd.
"""
import argparse, json, math, time, zlib
import numpy as np
from numpy.polynomial import chebyshev as C
from scipy.optimize._highspy import _core as hc
from mm import multi_indices, make_net, net_f, linear_f, parity_f, sample_points


class Herm:
    def __init__(self, n, d):
        self.n, self.d = n, d
        self.idx = multi_indices(n, d)
        self.M = len(self.idx)
        self.nz = [[(i, a) for i, a in enumerate(al) if a] for al in self.idx]

    def uni(self, X):
        d = self.d
        H = np.empty((d + 1,) + X.shape)
        H[0] = 1.0
        if d >= 1:
            H[1] = X
        for k in range(1, d):
            H[k + 1] = X * H[k] - k * H[k - 1]
        for k in range(d + 1):
            H[k] /= math.sqrt(math.factorial(k))
        return H

    def matrix(self, X):  # M x N
        H = self.uni(X)
        A = np.empty((self.M, X.shape[0]))
        for r, nz in enumerate(self.nz):
            v = np.ones(X.shape[0])
            for i, a in nz:
                v = v * H[a, :, i]
            A[r] = v
        return A

    def ydot(self, y, X):  # y . He(x) for each row of X, without storing the matrix
        H = self.uni(X)
        out = np.zeros(X.shape[0])
        for r, nz in enumerate(self.nz):
            if y[r] == 0.0:
                continue
            v = np.full(X.shape[0], y[r])
            for i, a in nz:
                v = v * H[a, :, i]
            out += v
        return out


class Pricer:
    def __init__(self, herm, Rmax, ngrid=512):
        d = herm.d
        self.herm, self.Rmax = herm, Rmax
        k = np.arange(d + 1)
        t = np.cos(np.pi * (k + 0.5) / (d + 1))           # Chebyshev nodes in [-1,1]
        self.rn = (t + 1) * Rmax / 2
        self.rg = np.linspace(0, Rmax, ngrid)
        Vn = C.chebvander(t, d)
        Vg = C.chebvander(2 * self.rg / Rmax - 1, d)
        self.E = Vg @ np.linalg.inv(Vn)                     # grid values from node values

    def best(self, y, U, gU, s, chunk=2048):
        """For directions U (B x n) with f(U)=gU: return best radius and reduced cost."""
        B = U.shape[0]
        r_best = np.empty(B); rc_best = np.empty(B)
        for a in range(0, B, chunk):
            u = U[a:a + chunk]; g = gU[a:a + chunk]; b = u.shape[0]
            pts = (self.rn[:, None, None] * u[None]).reshape(-1, u.shape[1])
            Pn = self.herm.ydot(y, pts).reshape(len(self.rn), b)  # nodes x b
            Pg = self.E @ Pn                                       # grid x b
            rc = -s * self.rg[:, None] * g[None] - Pg
            j = np.argmin(rc, axis=0)
            r_best[a:a + b] = self.rg[j]
            rc_best[a:a + b] = rc[j, np.arange(b)]
        return r_best, rc_best


def unit(X):
    nr = np.linalg.norm(X, axis=1, keepdims=True)
    return X[nr[:, 0] > 0] / nr[nr[:, 0] > 0]


def build(A, cost):
    M, N = A.shape
    lp = hc.HighsLp()
    lp.num_col_ = N; lp.num_row_ = M
    lp.col_cost_ = cost.astype(np.float64)
    lp.col_lower_ = np.zeros(N); lp.col_upper_ = np.full(N, hc.kHighsInf)
    b = np.zeros(M); b[0] = 1.0
    lp.row_lower_ = b; lp.row_upper_ = b.copy()
    am = lp.a_matrix_
    am.format_ = hc.MatrixFormat.kColwise
    am.num_col_ = N; am.num_row_ = M
    am.start_ = np.arange(0, M * N + 1, M, dtype=np.int32)
    am.index_ = np.tile(np.arange(M, dtype=np.int32), N)
    am.value_ = np.ascontiguousarray(A.T).ravel()
    lp.a_matrix_ = am
    h = hc._Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    h.setOptionValue("presolve", "off")
    h.setOptionValue("time_limit", 7200.0)
    h.passModel(lp)
    return h


def add_cols(h, A, cost):
    M, K = A.shape
    h.addCols(K, cost.astype(np.float64), np.zeros(K), np.full(K, hc.kHighsInf), M * K,
              np.arange(0, M * K, M, dtype=np.int32), np.tile(np.arange(M, dtype=np.int32), K),
              np.ascontiguousarray(A.T).ravel())


def run_objective(herm, pricer, X0, fun, s, sd, mu, args, rng, log):
    """Column generation for one objective/sense. Returns dict."""
    X = X0.copy()
    fX = fun(X)
    A = herm.matrix(X)
    h = build(A, -s * fX)
    t0 = time.time(); hist = []
    for rnd in range(args.rounds):
        h.run()
        st = h.modelStatusToString(h.getModelStatus())
        if st != "Optimal":  # numerical trouble: rebuild cold and retry once with primal simplex
            h = build(herm.matrix(X), -s * fun(X))
            h.setOptionValue("simplex_strategy", 4)
            h.run()
            st = h.modelStatusToString(h.getModelStatus())
            if st != "Optimal":
                return {"status": st, "round": rnd}
        sol = h.getSolution()
        y = np.asarray(sol.row_dual); q = np.asarray(sol.col_value)
        lpval = -s * h.getObjectiveValue()          # value of s*E f ... converted below
        # pricing pool: fresh random directions + perturbations of the current support
        sup = X[q > 1e-12]
        Ud = unit(rng.standard_normal((args.pool, herm.n)))
        if len(sup) and len(unit(sup)):
            us = unit(sup)
            pick = us[rng.integers(0, len(us), args.pool // 2)]
            sig = rng.choice([0.01, 0.05, 0.2], size=(len(pick), 1))
            Ud = np.vstack([Ud, unit(pick + sig * rng.standard_normal(pick.shape))])
        rb, rcb = pricer.best(y, Ud, fun(Ud), s)
        # local refinement of the best directions (hill-climb on the sphere, radius exact on grid)
        for sig in (0.03, 0.01, 0.003):
            top = np.argsort(rcb)[:256]
            for _ in range(2):
                Ut = unit(Ud[top] + sig * rng.standard_normal(Ud[top].shape))
                rt, rct = pricer.best(y, Ut, fun(Ut), s)
                better = rct < rcb[top]
                Ud[top[better]] = Ut[better]; rb[top[better]] = rt[better]; rcb[top[better]] = rct[better]
        minrc = float(rcb.min())
        # LP objective is min c = -s f ; LP value Lc = h.getObjectiveValue(); outer bound Lc + minrc
        Lc = h.getObjectiveValue()
        inner = -Lc * 1.0                 # = s * (best E f over current points)
        outer = -(Lc + minrc)             # >= s * E_mu f for every matching mu (sampled)
        best_outer = outer if rnd == 0 else min(best_outer, outer)
        hit = float(np.mean(rb[np.argsort(rcb)[:50]] >= pricer.Rmax - 1e-9))
        hist.append((rnd, X.shape[0], inner / sd, best_outer / sd, round(time.time() - t0, 1), hit))
        if args.verbose and rnd % 10 == 0:
            print("  ", s, hist[-1], f"minrc/sd={minrc/sd:.3g}", flush=True)
        # stop when the inner/outer bracket is tight: absolute tol or rtol of the one-sided deviation
        if (best_outer - inner) < max(args.tol * sd, args.rtol * abs(inner - s * mu)):
            break
        order = np.argsort(rcb)[: args.K]
        order = order[rcb[order] < -args.tol * sd * 0.1]
        Xn = rb[order, None] * Ud[order]
        if len(Xn) == 0:
            break
        # purge: keep positive-weight columns + the 3M non-basic columns with smallest reduced cost
        if X.shape[0] > 6 * herm.M + 4000:
            cd = np.asarray(sol.col_dual)
            keep = q > 1e-12
            cand = np.where(~keep)[0]
            keep[cand[np.argsort(cd[cand])[: 3 * herm.M + 2000]]] = True
            dele = np.where(~keep)[0].astype(np.int32)
            h.deleteCols(len(dele), dele)
            X = X[keep]
        fn = fun(Xn)
        add_cols(h, herm.matrix(Xn), -s * fn)
        X = np.vstack([X, Xn])
    resid = float(np.max(np.abs(herm.matrix(X) @ np.asarray(h.getSolution().col_value)
                                 - np.eye(herm.M)[0])))
    at_rmax = None
    return {"status": "Optimal", "inner": s * inner, "outer": s * best_outer, "rounds": len(hist),
            "ncols": int(X.shape[0]), "resid": resid, "minrc_sd": minrc / sd,
            "support": int((np.asarray(h.getSolution().col_value) > 1e-12).sum()),
            "t": round(time.time() - t0, 1), "hist": hist}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--d", type=int, nargs="+", required=True)
    ap.add_argument("--L", type=int, nargs="+", default=[1, 2, 4, 8])
    ap.add_argument("--nets", type=int, default=3)
    ap.add_argument("--N0", type=int, default=0, help="initial points (default max(4096, 4M))")
    ap.add_argument("--pool", type=int, default=16384)
    ap.add_argument("--K", type=int, default=0, help="cols per round (default min(M,400))")
    ap.add_argument("--rounds", type=int, default=60)
    ap.add_argument("--tol", type=float, default=2e-3)
    ap.add_argument("--rtol", type=float, default=0.03)
    ap.add_argument("--Rmax", type=float, default=0.0)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    n = args.n
    Xtest = np.random.default_rng(99).standard_normal((1 << 16, n))
    nets = {(L, k): make_net(n, L, k, Xtest) for L in args.L for k in range(args.nets)}
    funs = {"linear_net0": lambda X: linear_f(X, 0), "parity": parity_f}
    for (L, k), (Ws, a, rej) in sorted(nets.items(), key=lambda t: (t[0][1], t[0][0])):
        funs[f"relu_L{L}_net{k}"] = (lambda X, Ws=Ws, a=a, L=L: net_f(X, Ws, a, L))
    if args.only:
        funs = {k: v for k, v in funs.items() if k in args.only}
    G = np.random.default_rng(777).standard_normal((1 << 20, n))
    stats = {k: (float(f(G).mean()), float(f(G).std())) for k, f in funs.items()}
    del G
    with open(args.out, "a") as fo:
        fo.write(json.dumps({"type": "gauss", "n": n, "stats": stats,
                             "dead_rejections": {f"L{L}_net{k}": v[2] for (L, k), v in nets.items()}}) + "\n")
    Rmax0 = args.Rmax
    for d in args.d:
        herm = Herm(n, d)
        Rmax = Rmax0 or (math.sqrt(n) + math.sqrt(2 * d) + 4.0)
        pricer = Pricer(herm, Rmax)
        N0 = args.N0 or max(4096, 4 * herm.M)
        X0 = sample_points(n, N0, seed=d)
        # add a shell of points with radius uniform on [0, Rmax] so far-field duals are controlled early
        rs = np.random.default_rng(10 + d)
        Xs = unit(rs.standard_normal((N0 // 3, n))) * rs.uniform(0, Rmax, (N0 // 3, 1))
        X0 = np.vstack([X0, Xs])
        args.K = args.K or max(herm.M, 600)
        for name, fun in funs.items():
            mu, sd = stats[name]
            rec = {"type": "cg", "n": n, "d": d, "M": herm.M, "N0": N0, "name": name, "mu": mu, "sd": sd}
            for s, key in ((1, "max"), (-1, "min")):
                rng = np.random.default_rng([n, d, s + 1, zlib.crc32(name.encode())])
                # LP costs in units of sd(f) (tiny-sd nets otherwise hit HiGHS absolute tolerances)
                fs = (lambda X, fun=fun, sd=sd: fun(X) / sd)
                r = run_objective(herm, pricer, X0, fs, s, 1.0, mu / sd, args, rng, None)
                if r["status"] == "Optimal":
                    r["inner"] *= sd; r["outer"] *= sd
                rec[key] = r
            mx, mn = rec["max"], rec["min"]
            if mx["status"] == "Optimal" and mn["status"] == "Optimal":
                rec["gap_lo"] = (mx["inner"] - mn["inner"]) / sd
                rec["gap_hi"] = (mx["outer"] - mn["outer"]) / sd
                print(f"n={n} d={d} M={herm.M} {name}: gap/sd in [{rec['gap_lo']:.4f}, {rec['gap_hi']:.4f}] "
                      f"rounds={mx['rounds']},{mn['rounds']} t={mx['t']}+{mn['t']}s", flush=True)
            else:
                print(f"n={n} d={d} {name}: status {mx['status']} {mn['status']}", flush=True)
            with open(args.out, "a") as fo:
                fo.write(json.dumps(rec) + "\n")
        args.K = 0 if args.K == max(herm.M, 600) else args.K


if __name__ == "__main__":
    main()
