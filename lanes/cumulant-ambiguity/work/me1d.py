"""Typical per-step closure error for next-layer MEANS, via the exact 1D reduction.  MEASURED.
Run with /home/agent/.venvs/arc-noisy/bin/python.

E h_{l+1,i} = E relu(z_i), z = W_{l+1} h_l.  The linear step is exact on cumulants, so an order-K
closure that is handed the TRUE order-<=K cumulants of h_l knows the true first K cumulants of each z_i,
and its estimate of E h_{l+1,i} is a function of those scalar cumulants only for the rules below:
  gauss  (K=2)  : E relu under N(mu, s^2)  [= ARC's order-2 step for the mean]
  edge3  (K=3)  : Gram-Charlier density phi(y)(1 + k3/6 He3(y))
  edge4  (K=4)  : phi(y)(1 + k3/6 He3 + k4/24 He4)            [Edgeworth/Wick truncation, ARC-like]
  maxent4 (K=4) : density prop. to exp(sum_{j<=4} lam_j y^j) matching the first 4 moments (grid on [-R, R])
Moments of z_i from stream A (M samples), truth E relu(z_i) and Var h_{l+1,i} from independent stream B.
step_nmse(rule, l) = sum_i (est_i - truth_i)^2 / sum_i Var h_{l+1,i}  - 1/M   (truth-noise corrected).
"""
import argparse, json, math, sys, time
import numpy as np
sys.path.insert(0, "/home/agent/workspaces/mats/work/arc-noisy")
from scipy.special import ndtr

SQ2PI = math.sqrt(2 * math.pi)


def weights(seed, n, L):
    import anet
    W = anet.make_weights(seed, n, L)
    return [np.asarray(w, dtype=np.float64) for w in W]


def stream_z(W, M, seed, chunk=1 << 14):
    """Accumulate per layer l=1..L: power sums of z_l up to 4 (stream used for moments) or relu sums."""
    n, L = W[0].shape[0], len(W)
    rng = np.random.default_rng(seed)
    P = np.zeros((L, 5, n)); R1 = np.zeros((L, n)); R2 = np.zeros((L, n))
    done = 0
    while done < M:
        k = min(chunk, M - done)
        h = rng.standard_normal((k, n))
        for l in range(L):
            z = h @ W[l].T
            zz = np.ones_like(z)
            for j in range(5):
                P[l, j] += zz.sum(0); zz = zz * z
            h = np.maximum(z, 0)
            R1[l] += h.sum(0); R2[l] += (h * h).sum(0)
        done += k
    return P / M, R1 / M, R2 / M - (R1 / M) ** 2


def cumulants(P):
    m1, m2, m3, m4 = P[1], P[2], P[3], P[4]
    v = m2 - m1 ** 2
    c3 = m3 - 3 * m1 * m2 + 2 * m1 ** 3
    c4 = m4 - 4 * m1 * m3 + 6 * m1 ** 2 * m2 - 3 * m1 ** 4
    s = np.sqrt(np.maximum(v, 1e-300))
    return m1, s, c3 / s ** 3, c4 / s ** 4 - 3


def gauss_relu(mu, s):
    a = mu / s
    return mu * ndtr(a) + s * np.exp(-a * a / 2) / SQ2PI


def edge_relu(mu, s, k3, k4, order):
    # E relu(mu + s y) under phi(y)(1 + k3/6 He3(y) [+ k4/24 He4(y)]).  With a = -mu/s (kink in y):
    # int_a^inf (mu + s y) He_k(y) phi(y) dy = [mu He_{k-1}(a) + s (He_k(a) + k He_{k-2}(a))] phi(a), k >= 2.
    a = -mu / s
    ph = np.exp(-a * a / 2) / SQ2PI
    He = {0: np.ones_like(a), 1: a, 2: a * a - 1, 3: a ** 3 - 3 * a, 4: a ** 4 - 6 * a * a + 3}
    base = gauss_relu(mu, s)
    t3 = (mu * He[2] + s * (He[3] + 3 * He[1])) * ph
    out = base + k3 / 6 * t3
    if order >= 4:
        t4 = (mu * He[3] + s * (He[4] + 4 * He[2])) * ph
        out = out + k4 / 24 * t4
    return out


def maxent_relu(mu, s, k3, k4, R=8.0, G=1601, iters=60):
    y = np.linspace(-R, R, G); dy = y[1] - y[0]
    T = np.vstack([y, y ** 2, y ** 3, y ** 4])
    out = np.empty_like(mu)
    for i in range(len(mu)):
        target = np.array([0.0, 1.0, k3[i], k4[i] + 3.0])
        lam = np.array([0.0, -0.5, 0.0, 0.0])
        for _ in range(iters):
            e = lam @ T; e -= e.max(); p = np.exp(e); p /= p.sum()
            mom = T @ p
            g = mom - target
            if np.max(np.abs(g)) < 1e-10:
                break
            C = (T * p) @ T.T - np.outer(mom, mom)
            step = np.linalg.solve(C + 1e-12 * np.eye(4), g)
            t = 1.0
            # damped Newton on the convex dual  log Z(lam) - lam.target
            def dual(l):
                e = l @ T; m = e.max(); return m + math.log(np.exp(e - m).sum()) - l @ target
            d0 = dual(lam)
            while t > 1e-6 and dual(lam - t * step) > d0:
                t /= 2
            lam = lam - t * step
        e = lam @ T; e -= e.max(); p = np.exp(e); p /= p.sum()
        out[i] = p @ np.maximum(mu[i] + s[i] * y, 0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--M", type=int, default=1 << 20)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--maxent", type=int, default=1)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    n, L = args.n, args.L
    for seed in args.seeds:
        t0 = time.time()
        W = weights(seed, n, L)
        PA, _, _ = stream_z(W, args.M, [seed, 1])
        PB, mB, vB = stream_z(W, args.M, [seed, 2])
        rec = dict(n=n, L=L, seed=seed, M=args.M, exkurt=[], skew=[], step={})
        rules = ["gauss", "edge3", "edge4"] + (["maxent4"] if args.maxent else [])
        for r in rules:
            rec["step"][r] = []
        for l in range(L):
            mu, s, k3, k4 = cumulants(PA[l])
            live = vB[l] > 1e-14
            rec["exkurt"].append(float(np.median(k4[live]))); rec["skew"].append(float(np.median(k3[live])))
            ests = {"gauss": gauss_relu(mu, s), "edge3": edge_relu(mu, s, k3, k4, 3),
                    "edge4": edge_relu(mu, s, k3, k4, 4)}
            if args.maxent:
                ests["maxent4"] = np.where(live, maxent_relu(mu, s, np.where(live, k3, 0), np.where(live, k4, 0)), 0.0)
            for r in rules:
                e = ests[r]
                rec["step"][r].append(float(((e - mB[l])[live] ** 2).sum() / vB[l].sum()) - 1.0 / args.M)
        rec["t"] = round(time.time() - t0, 1)
        with open(args.out, "a") as fo:
            fo.write(json.dumps(rec) + "\n")
        print(n, L, seed, {r: f"{np.mean(v):.2e}" for r, v in rec["step"].items()},
              "exkurt last", f"{rec['exkurt'][-1]:.3f}", flush=True)


if __name__ == "__main__":
    main()
