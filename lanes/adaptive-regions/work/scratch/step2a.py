"""Step 2a of the certified-linear backward probe: one-shot CROWN certificates from state layer l.

Domains at state layer l (all explicit in layer-l coordinates):
- box:   D = B(tau) = {c + P a : |a_k| <= tau r_k}, a PCA box around the training cloud (c = train mean, P = principal
         axes, r_k = 1.02 x max_train |a_k|);
- slice: D = B(tau) cap {one or two halfspaces given by the CROWN linear bounds themselves} (below).
Own CROWN (lib/ar.py; full CROWN intermediate bounds intersected with IBP) bounds the output PRE-activation
z_j = w_j . h_{L-1} through layers l+1..L-1 over B(tau): lower_j(h) = Ll h + bl <= z_j(h) <= Lu h + bu = upper_j(h)
for every h in B(tau) (exact, lower = upper = w_j . h, at l = L-1). Since f_j = relu(z_j):
- zero certificate (A = 0): f_j <= eps on {h in B : upper_j(h) <= eps};
- linear certificate (A = (Ll + Lu)/2, c = (bl + bu)/2): |f_j - A h - c| <= eps on
  {h in B : lower_j(h) >= -eps/2 and (upper_j(h) - lower_j(h))/2 <= eps/2}.
"box" requires the condition on the whole box (concretised bounds); "slice" keeps the halfspace(s) in the domain.
Coverage at level e (eps = e x RMS_j; e = 0 means 1e-9 x RMS_j) is the best held-out fraction over tau. One-shot bounds
from layer l are at least as tight as any layer-by-layer composition over the same layer-l set. MEASURED (exploratory).
Usage: step2a.py SEED n L [--log2N 14] [--per_class 6]
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--log2N', type=int, default=14)
ap.add_argument('--per_class', type=int, default=6)
ap.add_argument('--layers', default=None)
ap.add_argument('--eps', default='0,1e-3,1e-2,1e-1')
ap.add_argument('--taus', default='1,0.5,0.25,0.1,0.05,0.02,0.01,0.005,0.002,0.001,1e-4')
ap.add_argument('--stop_after_dead', type=int, default=2)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
N = 1 << args.log2N
EPS = [float(e) for e in args.eps.split(',')]
TAUS = np.array([float(t) for t in args.taus.split(',')])
if args.layers:
    LAYERS = [int(x) for x in args.layers.split(',')]
else:
    LAYERS = sorted(set([L - 1 - b for b in (0, 1, 2, 3, 4, 5, 7, 11, 15, 23, 31) if L - 1 - b >= 0]), reverse=True)
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step2a_n{n}_L{L}_s{seed}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
W64 = [w.double() for w in W]


@torch.no_grad()
def sample(gen_seed, M, keep, chunk=1 << 12):
    gen = torch.Generator().manual_seed(gen_seed)
    H = {l: np.zeros((M, n), dtype=np.float32) for l in keep}
    Z = np.zeros((M, n), dtype=np.float32)
    done = 0
    while done < M:
        k = min(chunk, M - done)
        h = torch.randn(k, n, generator=gen)
        if 0 in H:
            H[0][done:done + k] = h.numpy()
        for l in range(L):
            z = h @ W[l].T
            h = torch.relu(z)
            if (l + 1) in H:
                H[l + 1][done:done + k] = h.numpy()
        Z[done:done + k] = z.numpy()
        done += k
    return H, Z


H_tr, Z_tr = sample(5_000_000 + seed, N, set(LAYERS))
H_te, Z_te = sample(6_000_000 + seed, N, set(LAYERS))
F_tr = np.maximum(Z_tr, 0); F_te = np.maximum(Z_te, 0).astype(np.float64)
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
m = len(picked)
print(f'sampled in {time.time() - t0:.0f}s; classes', {c: int((cls == c).sum()) for c in ('zero', 'on', 'switching')},
      'picked', picked.tolist(), flush=True)
dev2 = (F_te - F_te.mean(0)) ** 2
rows_out = W64[L - 1][torch.from_numpy(picked)]            # z_j = w_j . h_{L-1}
res = dict(n=n, L=L, seed=seed, N=N, eps=EPS, taus=TAUS.tolist(), picked=picked.tolist(),
           cls=[str(cls[j]) for j in picked], rms=[float(rms[j]) for j in picked],
           classes={c: int((cls == c).sum()) for c in ('zero', 'on', 'switching')}, layers=[])
dead_run = 0
for l in LAYERS:
    t1 = time.time()
    Htr = H_tr[l].astype(np.float64); Hte = H_te[l].astype(np.float64)
    c = Htr.mean(0)
    _, sv, Vt = np.linalg.svd(Htr - c, full_matrices=False)
    P = Vt.T
    Atr = (Htr - c) @ P; Ate = (Hte - c) @ P
    r = np.abs(Atr).max(0) * 1.02 + 1e-12
    inside = [np.all(np.abs(Ate) <= tau * r[None, :], axis=1) for tau in TAUS]
    cov_box = np.array([float(x.mean()) for x in inside])
    B = len(TAUS)
    Hte_t = torch.from_numpy(Hte)
    if l == L - 1:
        # exact: z_j = w_j . h
        zt = (Hte_t @ rows_out.T).numpy()
        LO = np.broadcast_to(zt, (B,) + zt.shape); UP = LO
        conc_lo = np.array([[float((rows_out[i].numpy() @ c) - np.abs(rows_out[i].numpy() @ P) @ (tau * r))
                             for i in range(m)] for tau in TAUS])
        conc_up = np.array([[float((rows_out[i].numpy() @ c) + np.abs(rows_out[i].numpy() @ P) @ (tau * r))
                             for i in range(m)] for tau in TAUS])
        gap_max = np.zeros((B, m))
        unst = np.zeros((B, 0), dtype=int)
    else:
        cc = torch.from_numpy(np.tile(c, (B, 1)))
        rr = torch.from_numpy(TAUS[:, None] * r[None, :])
        pre, (lo, up), (Ll, bl, Lu, bu) = ar.crown(W64[:L - 1], l, cc, torch.from_numpy(P), rr, out_rows=rows_out,
                                                   return_linear=True)
        conc_lo, conc_up = lo.numpy(), up.numpy()
        UP = (torch.einsum('bmn,sn->bsm', Lu, Hte_t) + bu[:, None, :]).numpy()
        LO = (torch.einsum('bmn,sn->bsm', Ll, Hte_t) + bl[:, None, :]).numpy()
        Dg = (Lu - Ll).numpy(); db = (bu - bl).numpy()
        gap_max = db + np.einsum('bmn,n->bm', Dg, c) + (np.abs(np.einsum('bmn,nk->bmk', Dg, P)) * (TAUS[:, None] * r[None, :])[:, None, :]).sum(-1)
        unst = np.array([[int(((zlo[b] < 0) & (zhi[b] > 0)).sum()) for (zlo, zhi) in pre] for b in range(B)])
    per = []
    for i, j in enumerate(picked):
        d = dict(j=int(j), cls=str(cls[j]), rms=float(rms[j]))
        for e in EPS:
            eps = max(e, 1e-9) * max(rms[j], 1e-300)
            best = dict(box=(0.0, None, None, None), slice=(0.0, None, None, None))
            for b in range(B):
                ins = inside[b]
                if not ins.any():
                    continue
                # whole-box certificates
                if conc_up[b, i] <= eps and cov_box[b] > best['box'][0]:
                    best['box'] = (cov_box[b], b, 'zero', ins)
                if conc_lo[b, i] >= -eps / 2 and gap_max[b, i] / 2 <= eps / 2 and cov_box[b] > best['box'][0]:
                    best['box'] = (cov_box[b], b, 'lin', ins)
                # sliced domains
                zero_ok = ins & (UP[b, :, i] <= eps)
                lin_ok = ins & (LO[b, :, i] >= -eps / 2) & ((UP[b, :, i] - LO[b, :, i]) / 2 <= eps / 2)
                for kind, mk in (('zero', zero_ok), ('lin', lin_ok)):
                    cv = float(mk.mean())
                    if cv > best['slice'][0]:
                        best['slice'] = (cv, b, kind, mk)
            for fam in ('box', 'slice'):
                cv, b, kind, mk = best[fam]
                d[f'{fam}_cov_e{e:g}'] = cv
                d[f'{fam}_tau_e{e:g}'] = float(TAUS[b]) if b is not None else None
                d[f'{fam}_kind_e{e:g}'] = kind
                d[f'{fam}_vshare_e{e:g}'] = float(dev2[mk, j].sum() / max(dev2[:, j].sum(), 1e-300)) if mk is not None else 0.0
                d[f'{fam}_unstable_e{e:g}'] = (unst[b].tolist() if b is not None else None)
        per.append(d)
    summ = {}
    for cl in ('zero', 'on', 'switching'):
        ii = [k for k, d in enumerate(per) if d['cls'] == cl]
        if ii:
            summ[cl] = {}
            for fam in ('box', 'slice'):
                for e in EPS:
                    summ[cl][f'{fam}_cov_e{e:g}_median'] = float(np.median([per[k][f'{fam}_cov_e{e:g}'] for k in ii]))
                    summ[cl][f'{fam}_vshare_e{e:g}_median'] = float(np.median([per[k][f'{fam}_vshare_e{e:g}'] for k in ii]))
    row = dict(l=l, back=L - 1 - l, cov_box_by_tau=cov_box.tolist(), unstable_by_tau=unst.tolist(), sv=sv[:16].tolist(),
               per_output=per, class_summary=summ, secs=time.time() - t1)
    res['layers'].append(row)
    print(f"l={l:2d} back={L - 1 - l:2d} | " + ' | '.join(
        f"{cl}: box " + ' '.join(f"{summ[cl][f'box_cov_e{e:g}_median']:.3f}" for e in EPS) + ' slice ' +
        ' '.join(f"{summ[cl][f'slice_cov_e{e:g}_median']:.3f}" for e in EPS) for cl in summ) +
        f"  ({time.time() - t1:.0f}s)", flush=True)
    mx = max(max(summ[cl][f'box_cov_e{EPS[-1]:g}_median'], summ[cl][f'slice_cov_e{EPS[-1]:g}_median']) for cl in summ)
    dead_run = dead_run + 1 if mx == 0 else 0
    json.dump(res, open(out, 'w'))
    if dead_run >= args.stop_after_dead:
        break
json.dump(res, open(out, 'w'))
print('wrote', out, 'total', time.time() - t0)
