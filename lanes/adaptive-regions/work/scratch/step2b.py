"""Step 2b of the certified-linear backward probe: one-shot CROWN certificates with pinned gates ("splits").

Domain at state layer l for output j: D = B(tau) cap {pins} cap {slice}, where B(tau) is the PCA box of step 2a, pins
fix the gate sign of the p units of layer l+1 with the largest first-order effect on z_j (linear constraints in h_l:
s_i w_i . h >= 0), each to its majority sign on the training cloud, and the slice keeps the CROWN linear-bound
conditions of step 2a (zero: upper_j(h) <= eps; linear: lower_j(h) >= -eps/2 and gap_j(h) <= eps). Pinned units enter
CROWN with their intervals clipped to the pinned side (sound on D). Effect of unit i: E|dz_j/dh_{l+1,i}| x sd(z_{l+1,i})
on the training cloud (VJPs). Units of layers l+2..L-1 cannot be pinned by linear constraints in h_l and stay relaxed.
Reports, per back = L-1-l, p and eps, the held-out coverage and variance share. MEASURED (exploratory).
Usage: step2b.py SEED n L [--backs 1,2,3] [--per_class 4]
"""
import argparse, json, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--log2N', type=int, default=13)
ap.add_argument('--per_class', type=int, default=4)
ap.add_argument('--backs', default='1,2,3')
ap.add_argument('--pins', default='0,4,16,64,all')
ap.add_argument('--eps', default='0,1e-3,1e-2,1e-1')
ap.add_argument('--taus', default='1,0.5')
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
N = 1 << args.log2N
EPS = [float(e) for e in args.eps.split(',')]
TAUS = np.array([float(t) for t in args.taus.split(',')])
BACKS = [int(b) for b in args.backs.split(',')]
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step2b_n{n}_L{L}_s{seed}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
W64 = [w.double() for w in W]
LAYERS = [L - 1 - b for b in BACKS if L - 1 - b >= 0]
keep = set(LAYERS) | set(l + 1 for l in LAYERS)


@torch.no_grad()
def sample(gen_seed, M, chunk=1 << 12):
    gen = torch.Generator().manual_seed(gen_seed)
    H = {l: np.zeros((M, n), dtype=np.float32) for l in keep}
    Z = np.zeros((M, n), dtype=np.float32)
    X = np.zeros((M, n), dtype=np.float32)
    done = 0
    while done < M:
        k = min(chunk, M - done)
        h = torch.randn(k, n, generator=gen)
        X[done:done + k] = h.numpy()
        if 0 in H:
            H[0][done:done + k] = h.numpy()
        for l in range(L):
            z = h @ W[l].T
            h = torch.relu(z)
            if (l + 1) in H:
                H[l + 1][done:done + k] = h.numpy()
        Z[done:done + k] = z.numpy()
        done += k
    return H, Z, X


H_tr, Z_tr, X_tr = sample(7_000_000 + seed, N)
H_te, Z_te, X_te = sample(8_000_000 + seed, N)
F_te = np.maximum(Z_te, 0).astype(np.float64); F_tr = np.maximum(Z_tr, 0)
pz = ((F_tr == 0).mean(0) + (F_te == 0).mean(0)) / 2
cls = np.where(pz >= 0.999, 'zero', np.where(pz <= 0.001, 'on', 'switching'))
rms = np.sqrt((F_te ** 2).mean(0)); var = F_te.var(0)
picked = []
for c in ('zero', 'on', 'switching'):
    idx = np.where(cls == c)[0]
    if len(idx):
        idx = idx[np.argsort(var[idx])]
        sel = idx[np.linspace(0, len(idx) - 1, min(args.per_class, len(idx))).round().astype(int)]
        picked += sorted(set(sel.tolist()))
picked = np.array(picked)
dev2 = (F_te - F_te.mean(0)) ** 2
print(f'sampled in {time.time() - t0:.0f}s; picked', picked.tolist(), flush=True)


@torch.no_grad()
def vjp_from(l1, Hl1, v):
    """Gradient of v . z_L wrt h_{l1} (pre-activation z_L of the last layer) at states Hl1 (float32 torch)."""
    hs = [Hl1]; masks = []
    h = Hl1
    for k in range(l1, L - 1):
        z = h @ W[k].T
        masks.append(z > 0)
        h = torch.relu(z)
    g = v[None, :].expand(Hl1.shape[0], -1) @ W[L - 1]          # d z_L / d h_{L-1}
    for idx, k in enumerate(range(L - 2, l1 - 1, -1)):
        g = (g * masks[k - l1]) @ W[k]
    return g


res = dict(n=n, L=L, seed=seed, N=N, eps=EPS, picked=picked.tolist(), cls=[str(cls[j]) for j in picked],
           results=[])
for l in LAYERS:
    Htr = H_tr[l].astype(np.float64); Hte = H_te[l].astype(np.float64)
    c = Htr.mean(0)
    _, sv, Vt = np.linalg.svd(Htr - c, full_matrices=False)
    P = Vt.T
    Atr = (Htr - c) @ P; Ate = (Hte - c) @ P
    r = np.abs(Atr).max(0) * 1.02 + 1e-12
    inside = [np.all(np.abs(Ate) <= tau * r[None, :], axis=1) for tau in TAUS]
    Zl1_tr = Htr @ W64[l].numpy().T                                # pre-activations of layer l+1
    Zl1_te = Hte @ W64[l].numpy().T
    sd = Zl1_tr.std(0)
    maj = (Zl1_tr > 0).mean(0) >= 0.5
    # exact range of z_{l+1} over the PCA box (zonotope): c' +- |W P| r tau
    WP = np.abs(W64[l].numpy() @ P)
    for i, j in enumerate(picked):
        t1 = time.time()
        e_j = np.zeros(L); e_j[0] = 0
        v = torch.zeros(n); v[j] = 1.0
        if l + 1 <= L - 1:
            G = vjp_from(l + 1, torch.from_numpy(H_tr[l + 1][:2048]), v).double().numpy()   # d z_j / d h_{l+1}
            # effect on z_j of unit i of layer l+1: E|d z_j/d h_{l+1,i}| x sd(z_{l+1,i})
            eff = np.abs(G).mean(0) * sd
        else:
            eff = np.abs(W64[L - 1].numpy()[j]) * sd
        order = np.argsort(-eff)
        rows_out = W64[L - 1][j:j + 1]
        for tb, tau in enumerate(TAUS):
            zc = W64[l].numpy() @ c
            zr = WP @ (tau * r)
            unstable_units = np.where((zc - zr < 0) & (zc + zr > 0))[0]
            # units fixed on the training cloud (one sign on >= 99.9%) are always pinned (cheap in coverage);
            # the switching units are pinned in order of effect
            frac_on = (Zl1_tr > 0).mean(0)
            cloud_fixed = set(np.where((frac_on >= 0.999) | (frac_on <= 0.001))[0].tolist())
            unst_set = set(unstable_units.tolist())
            base_pins = [u for u in order if u in unst_set and u in cloud_fixed]
            unst_ordered = [u for u in order if u in unst_set and u not in cloud_fixed]
            for pspec in args.pins.split(','):
                p = len(unst_ordered) if pspec == 'all' else min(int(pspec), len(unst_ordered))
                pins = np.array(base_pins + unst_ordered[:p], dtype=int)
                lo1 = zc - zr; hi1 = zc + zr
                lo1c, hi1c = lo1.copy(), hi1.copy()
                if len(pins):
                    on = maj[pins]
                    lo1c[pins[on]] = np.maximum(lo1c[pins[on]], 0.0)
                    hi1c[pins[~on]] = np.minimum(hi1c[pins[~on]], 0.0)
                inter = [(torch.from_numpy(lo1c[None]), torch.from_numpy(hi1c[None]))]
                if l == L - 1:
                    continue
                pre, (lo, up), (Ll, bl, Lu, bu) = ar.crown(W64[:L - 1], l, torch.from_numpy(c[None]), torch.from_numpy(P),
                                                           torch.from_numpy((tau * r)[None]), out_rows=rows_out,
                                                           inter=inter, return_linear=True)
                UP = (torch.from_numpy(Hte) @ Lu[0].T + bu[0]).numpy()[:, 0]
                LO = (torch.from_numpy(Hte) @ Ll[0].T + bl[0]).numpy()[:, 0]
                pin_ok = np.ones(N, dtype=bool)
                if len(pins):
                    sgn = Zl1_te[:, pins] > 0
                    pin_ok = np.all(sgn == maj[pins][None, :], axis=1)
                dom = inside[tb] & pin_ok
                unst_after = [int(((a[0] < 0) & (b[0] > 0)).sum()) for (a, b) in pre]
                for e in EPS:
                    eps = max(e, 1e-9) * max(rms[j], 1e-300)
                    zero_ok = dom & (UP <= eps)
                    lin_ok = dom & (LO >= -eps / 2) & ((UP - LO) / 2 <= eps / 2)
                    best = max((zero_ok.mean(), 'zero', zero_ok), (lin_ok.mean(), 'lin', lin_ok), key=lambda t: t[0])
                    res['results'].append(dict(l=l, back=L - 1 - l, j=int(j), cls=str(cls[j]), tau=float(tau), p=int(p),
                                               n_cloud_fixed_pins=len(base_pins), n_switching_unpinned=len(unst_ordered) - p,
                                               p_spec=pspec, eps=e, cov=float(best[0]), kind=best[1],
                                               vshare=float(dev2[best[2], j].sum() / max(dev2[:, j].sum(), 1e-300)),
                                               dom_cov=float(dom.mean()), unstable_after=unst_after,
                                               n_unstable_l1=int(len(unstable_units))))
        rr = [x for x in res['results'] if x['l'] == l and x['j'] == int(j) and x['eps'] == EPS[-1]]
        bestp = max(rr, key=lambda x: x['cov']) if rr else None
        print(f"l={l} back={L - 1 - l} j={j} ({cls[j]}): unstable l+1 at tau=1: {len(unst_ordered) if TAUS[-1] else ''}; "
              f"best cov at eps={EPS[-1]:g}: {bestp['cov']:.3f} (p={bestp['p']}, tau={bestp['tau']}, {bestp['kind']}) "
              f"({time.time() - t1:.0f}s)" if bestp else '', flush=True)
    json.dump(res, open(out, 'w'))
json.dump(res, open(out, 'w'))
print('wrote', out, 'total', time.time() - t0)
