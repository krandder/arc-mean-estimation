"""DEV exploration (seeds >= 9000; calibration only, not evidence): cubic law of the frozen-gate residual,
angular cloud spectrum, and the M-reference residual D_l(M). Output: logs/dev_explore.log (printed)."""
import os
import sys
import math
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import bb


def cubic_probe(W, l, rng, deltas, per=48):
    n = W[0].shape[0]
    L = len(W)
    u0 = bb.sphere(rng, 1, n)[0]
    c = bb.forward(W, u0[None, :], 0, l)[0]
    masks = bb.gate_path(W, c, l)
    gc = bb.frozen_apply(W, l, masks, c[None, :])[0]
    rows = []
    for d in deltas:
        xi = rng.standard_normal((per, n))
        xi -= np.outer(xi @ u0, u0)
        xi /= np.linalg.norm(xi, axis=1, keepdims=True)
        U = math.cos(d) * u0[None, :] + math.sin(d) * xi
        H = bb.forward(W, U, 0, l)
        phi = bb.angles_to(H, c)
        G = bb.forward(W, H, l)
        F = bb.frozen_apply(W, l, masks, H)
        R = G - F
        # gate disagreements along the future
        dis = np.zeros(per)
        hh = H.copy()
        for j, m in zip(range(l, L), masks):
            z = hh @ W[j].T
            dis += np.sum((z > 0) != m[None, :], axis=1)
            hh = np.maximum(z, 0.0)
        rel = np.sum(R * R, axis=1) / max(gc @ gc, 1e-300)
        relh = np.sum(R * R, axis=1) / np.sum(G * G, axis=1).clip(1e-300)
        rows.append((d, float(np.median(phi)), float(np.mean(rel)), float(np.median(relh)), float(np.mean(dis))))
    return rows


def main():
    os.environ.setdefault('OMP_NUM_THREADS', '1')
    t0 = time.time()
    for (n, L, seed) in [(64, 64, 9001), (128, 64, 9002)]:
        W = bb.make_weights(seed, n, L)
        rng = np.random.default_rng([seed, 1])
        print(f"=== net n={n} L={L} seed={seed}", flush=True)
        # output variance (per net) from samples
        X = rng.standard_normal((4096, n))
        keep = [L // 8, L // 4, L // 2, 3 * L // 4, L]
        Hs = bb.forward_keep(W, X, keep)
        A = Hs[L]
        V = float(np.sum(A.var(axis=0)))
        mu = A.mean(axis=0)
        print(f"V = {V:.4g}, |mu|^2 = {mu @ mu:.4g}, V/|mu|^2 = {V / (mu @ mu):.4g}", flush=True)
        for l in [L // 4, L // 2, 3 * L // 4]:
            Lp = L - l
            ev = bb.cloud_angular_spectrum(Hs[l])
            tot = ev.sum()
            pr = bb.participation_ratio(ev)
            # fit geometric decay over k = 1..10
            k = np.arange(1, 11)
            sl = np.polyfit(k, np.log(ev[:10]), 1)[0]
            print(f"-- l={l} L'={Lp}: angular var tot={tot:.3g} PR={pr:.2f} top5 frac={ev[:5] / tot} "
                  f"log-slope(k=1..10)={sl:.3f} (Lyapunov guess -2l/n={-2 * l / n:.3f})", flush=True)
            deltas = [1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0]
            rows = cubic_probe(W, l, rng, deltas)
            for (d, phi, rel, relh, dis) in rows:
                pred = (2 / (3 * math.pi)) * Lp * phi ** 3
                print(f"   delta={d:.0e} phi={phi:.3e} |R|^2/|g(c)|^2={rel:.3e} med|R|^2/|g(h)|^2={relh:.3e} "
                      f"cubic-pred={pred:.3e} ratio={rel / max(pred, 1e-300):.3g} gate-dis={dis:.1f} "
                      f"(pred n/pi L' phi={n / math.pi * Lp * phi:.1f})", flush=True)
            # M-reference residual on the actual cloud (k-means on directions at layer l)
            H = Hs[l][:2048]
            G = A[:2048]
            U = H / np.linalg.norm(H, axis=1, keepdims=True)
            for M in [1, 4, 16, 64, 256]:
                C, assign = bb.kmeans_dirs(U, M, rng)
                res = 0.0
                for kk in range(M):
                    sel = np.where(assign == kk)[0]
                    if sel.size == 0:
                        continue
                    # reference state: the cloud point closest to the centre (a genuine cloud state)
                    idx = sel[np.argmax(U[sel] @ C[kk])]
                    masks = bb.gate_path(W, H[idx], l)
                    F = bb.frozen_apply(W, l, masks, H[sel])
                    R = G[sel] - F
                    res += float(np.sum(R * R))
                D = res / H.shape[0]
                print(f"   M={M:4d}: D_l(M)/V = {D / V:.4g}", flush=True)
    print(f"done in {time.time() - t0:.0f}s", flush=True)


if __name__ == '__main__':
    main()
