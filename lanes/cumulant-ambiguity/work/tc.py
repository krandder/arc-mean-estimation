"""Typical-case per-step closure error of ARC's order-K cumulant propagation on TRUE layer laws.
MEASURED (exploratory).  Run with /home/agent/.venvs/arc-noisy/bin/python.

Net: ARC family via arc-update's lib (au.weights(seed, n, L): W_l iid N(0, 2/n), no bias), h_0 = x ~ N(0, I).
For each layer l = 0..L-1:
  true cumulants of h_l up to order K (Monte Carlo, M samples, stream A; exact at l = 0),
  ONE step of ARC's kprop (KH.linear_kprop with W_{l+1}, metric 2.0, then KH.nonlin_kprop for relu, as
  au.arc_kprop does) gives the order-K estimate of E h_{l+1};
  truth E h_{l+1} and Var h_{l+1} from an independent stream B (M samples).
  step_nmse_K(l) = |est - truth|^2 / tr Var h_{l+1}  - 1/M  (the -1/M removes the truth's own MC noise;
  cumulant-estimation noise in est is NOT removed: see the M-doubling check in the report).
Also: excess kurtosis of the next pre-activations z_{l+1,i} (median over i), and ARC's full recursion
(au.arc_kprop) error per layer, to compare per-step errors with accumulated ones.
"""
import argparse, json, math, sys, time
import numpy as np
import torch
sys.path.insert(0, "/home/agent/workspaces/mats/work/arc-update/lib")
import au  # noqa: E402
KH = au.KH


def layer_stream(W, M, seed, chunk, upto):
    """Yield chunks of [h_0, ..., h_upto] (float64) for M Gaussian inputs."""
    n = W[0].shape[0]
    gen = torch.Generator().manual_seed(int(seed))
    done = 0
    while done < M:
        k = min(chunk, M - done)
        h = torch.randn(k, n, generator=gen, dtype=torch.float64)
        hs = [h]
        for l in range(upto):
            h = torch.relu(h @ W[l].T)
            hs.append(h)
        yield hs
        done += k


def true_cumulants(W, L, Kmax, M, seed, chunk):
    n = W[0].shape[0]
    S1 = [torch.zeros(n, dtype=torch.float64) for _ in range(L)]
    for hs in layer_stream(W, M, seed, chunk, L - 1):
        for l in range(L):
            S1[l] += hs[l].sum(0)
    mu = [s / M for s in S1]
    C = {k: [torch.zeros((n,) * k, dtype=torch.float64) for _ in range(L)] for k in range(2, Kmax + 1)}
    for hs in layer_stream(W, M, seed, chunk, L - 1):
        for l in range(1, L):
            c = hs[l] - mu[l]
            if Kmax >= 2:
                C[2][l] += c.T @ c
            if Kmax >= 3:
                C[3][l] += torch.einsum("bi,bj,bk->ijk", c, c, c)
            if Kmax >= 4:
                cc = torch.einsum("bi,bj->bij", c, c).reshape(c.shape[0], -1)
                C[4][l] += (cc.T @ cc).reshape(n, n, n, n)
    out = []
    for l in range(L):
        if l == 0:
            K = {1: torch.zeros(n, dtype=torch.float64), 2: torch.eye(n, dtype=torch.float64)}
            if Kmax >= 3:
                K[3] = torch.zeros((n,) * 3, dtype=torch.float64)
            if Kmax >= 4:
                K[4] = torch.zeros((n,) * 4, dtype=torch.float64)
        else:
            K = {1: mu[l]}
            m2 = C[2][l] / M
            K[2] = m2
            if Kmax >= 3:
                K[3] = C[3][l] / M
            if Kmax >= 4:
                m4 = C[4][l] / M
                K[4] = m4 - (torch.einsum("ij,kl->ijkl", m2, m2) + torch.einsum("ik,jl->ijkl", m2, m2)
                             + torch.einsum("il,jk->ijkl", m2, m2))
        out.append(K)
    return out


def truth(W, L, M, seed, chunk):
    n = W[0].shape[0]
    S1 = np.zeros((L + 1, n)); S2 = np.zeros((L + 1, n)); Z4 = np.zeros((L + 1, n)); Z2 = np.zeros((L + 1, n))
    Z1 = np.zeros((L + 1, n)); Z3 = np.zeros((L + 1, n))
    for hs in layer_stream(W, M, seed, chunk, L):
        for l in range(1, L + 1):
            h = hs[l].numpy()
            S1[l] += h.sum(0); S2[l] += (h * h).sum(0)
            z = (hs[l - 1] @ W[l - 1].T).numpy()
            Z1[l] += z.sum(0); Z2[l] += (z ** 2).sum(0); Z3[l] += (z ** 3).sum(0); Z4[l] += (z ** 4).sum(0)
    m = S1 / M; v = S2 / M - m ** 2
    zm = Z1 / M; m2 = Z2 / M - zm ** 2
    m4 = Z4 / M - 4 * zm * Z3 / M + 6 * zm ** 2 * Z2 / M - 3 * zm ** 4
    exk = m4 / np.maximum(m2, 1e-300) ** 2 - 3
    return m, v, exk


def one_step(K_true, Wl, k):
    Kin = {d: K_true[d] for d in K_true if d <= k}
    K = KH.coerce_input(Kin, k_max=k, kind=KH.SIMPLE)
    K = KH.linear_kprop(K, Wl, k_max=k, set_metric=2.0, bias=None)
    K = KH.nonlin_kprop(K, nonlin_wick_coef=au.WICK_COEF_D["relu"], k_max=k, kind=KH.SIMPLE,
                        use_pK=True, factor=False)
    return K[1].to_tensor().numpy()


def run_from(K_true, W, c, k):
    """ARC recursion started from the TRUE order-<=k cumulants of h_c; returns final mean estimate of h_L."""
    Kin = {d: K_true[d] for d in K_true if d <= k}
    K = KH.coerce_input(Kin, k_max=k, kind=KH.SIMPLE)
    for l in range(c, len(W)):
        K = KH.linear_kprop(K, W[l], k_max=k, set_metric=2.0, bias=None)
        K = KH.nonlin_kprop(K, nonlin_wick_coef=au.WICK_COEF_D["relu"], k_max=k, kind=KH.SIMPLE,
                            use_pK=True, factor=False)
    return K[1].to_tensor().numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--K", type=int, nargs="+", default=[2, 3])
    ap.add_argument("--M", type=int, default=1 << 20)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--chunk", type=int, default=1 << 13)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    n, L = args.n, args.L
    for seed in args.seeds:
        t0 = time.time()
        W = au.weights(seed, n, L)
        Kt = true_cumulants(W, L, max(args.K), args.M, 1000 + seed, args.chunk)
        m, v, exk = truth(W, L, args.M, 2000 + seed, args.chunk)
        rec = dict(n=n, L=L, seed=seed, M=args.M, Ks=args.K, exkurt=[float(np.nanmedian(exk[l])) for l in range(1, L + 1)],
                   step={}, rec={})
        for k in args.K:
            errs = []
            for l in range(L):
                est = one_step(Kt[l], W[l], k)
                errs.append(float(((est - m[l + 1]) ** 2).sum() / v[l + 1].sum()) - 1.0 / args.M)
            rec["step"][k] = errs
            r = au.arc_kprop(W, k, count_flops=False)
            rec["rec"][k] = [float(((r["means"][l] - m[l + 1]) ** 2).sum() / v[l + 1].sum()) - 1.0 / args.M
                             for l in range(L)]
            # cut experiment: final error when the recursion starts from TRUE cumulants at layer c.
            # e_c = est_c - truth_L; final error e_0 = sum_c (e_c - e_{c+1}), e_L = 0: Delta_c is step c's
            # closure error as it arrives at the output (propagated through the later K-order steps).
            E = [run_from(Kt[c], W, c, k) - m[L] for c in range(L)] + [np.zeros(n)]
            V = v[L].sum()
            rec.setdefault("cut", {})[k] = [float((E[c] ** 2).sum() / V) for c in range(L)]
            rec.setdefault("delta", {})[k] = [float(((E[c] - E[c + 1]) ** 2).sum() / V) for c in range(L)]
        rec["t"] = round(time.time() - t0, 1)
        with open(args.out, "a") as fo:
            fo.write(json.dumps(rec) + "\n")
        print(json.dumps({k: (rec[k] if k not in ("step", "rec") else {kk: [f"{x:.2e}" for x in vv] for kk, vv in rec[k].items()})
                          for k in rec}), flush=True)


if __name__ == "__main__":
    main()
