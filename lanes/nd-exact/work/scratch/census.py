"""Region census (step 2): how the input sphere's mass splits over the activation regions of layers 1..d.

Region of x at depth d = activation pattern of layers 1..d (a polyhedral cone in R^8; the net is linear on it).
Masses: probability (uniform on S^7 = Gaussian measure of the cone) and output mass |a(x)| (the region's share of
E|a|, which bounds its contribution to E[a]). Downstream classes at cut c = pattern of layers c+1..256.
Usage: census.py SEED LOG2N OUT.json
"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import ndx  # noqa: E402

PREFIX_D = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]
CUTS = [8, 12, 16, 20, 24, 32, 48, 64]
QS = [0.9, 0.99, 0.999, 0.9999]


def coverage(counts_or_mass, q):
    m = np.sort(np.asarray(counts_or_mass, dtype=float))[::-1]
    c = np.cumsum(m) / m.sum()
    return int(np.searchsorted(c, q) + 1)


def stats_for_keys(keys, wa, N):
    _, inv, cnt = np.unique(keys, return_inverse=True, return_counts=True)
    ma = np.bincount(inv, weights=wa)
    sing = cnt[inv] == 1
    out = dict(distinct=int(len(cnt)), n1=int((cnt == 1).sum()), n2=int((cnt == 2).sum()),
               gt_unseen_prob=float((cnt == 1).sum() / N),
               gt_unseen_amass=float(wa[sing].sum() / wa.sum()),
               top1_prob=float(cnt.max() / N), top1_amass=float(ma.max() / ma.sum()))
    for q in QS:
        out[f'k_prob_{q}'] = coverage(cnt, q)
        out[f'k_amass_{q}'] = coverage(ma, q)
    # rarefaction (distinct regions among the first N/4^j samples)
    rare = {}
    for j in range(0, 6):
        m = N >> (2 * j)
        if m < 1024:
            break
        rare[str(m)] = int(len(np.unique(keys[:m])))
    out['rarefaction'] = rare
    # entropy (bits): plug-in and Chao-Shen coverage-adjusted; Chao1 richness; amass-weighted plug-in entropy
    p = cnt / N
    out['H_plugin_bits'] = float(-(p * np.log2(p)).sum())
    C = 1.0 - out['n1'] / N
    pa = C * p
    out['H_chaoshen_bits'] = float(-(pa * np.log2(pa) / (1.0 - (1.0 - pa) ** N)).sum())
    out['chao1'] = float(len(cnt) + out['n1'] ** 2 / (2.0 * max(out['n2'], 1)))
    qa = ma / ma.sum()
    qa = qa[qa > 0]
    out['H_amass_plugin_bits'] = float(-(qa * np.log2(qa)).sum())
    # coverage curve at k = 2^j (empirical)
    cs = np.cumsum(np.sort(cnt)[::-1]) / N
    ca = np.cumsum(np.sort(ma)[::-1]) / ma.sum()
    ks = [1 << j for j in range(0, 24) if (1 << j) <= len(cnt)]
    out['cov_curve'] = dict(k=ks, prob=[float(cs[k - 1]) for k in ks], amass=[float(ca[k - 1]) for k in ks])
    return out


def main():
    seed, log2n, outp = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    N = 1 << log2n
    chunk = min(N, 1 << 17)
    Ws = ndx.make_weights(seed)
    rng = np.random.default_rng([4242, seed])
    t0 = time.time()
    pk = {d: [] for d in PREFIX_D}
    sk = {c: [] for c in CUTS}
    A, minact, dead_at = [], [], []
    for _ in range(N // chunk):
        X = rng.standard_normal((chunk, 8))
        a, pat = ndx.fwd_patterns(Ws, X)
        A.append(a)
        pc = np.unpackbits(pat[:, :, None], axis=2).sum(2)  # active count per layer (N, 256)
        minact.append(np.stack([pc[:, :d].min(1) for d in PREFIX_D], 1))
        alive = pc > 0
        da = np.where(alive.all(1), 10 ** 6, np.argmin(alive, axis=1) + 1)  # first all-off layer (1-indexed)
        dead_at.append(da)
        for d in PREFIX_D:
            pk[d].append(ndx.hash2(pat[:, :d]))
        for c in CUTS:
            sk[c].append(ndx.hash2(pat[:, c:]))
    A = np.concatenate(A)
    minact = np.concatenate(minact)
    dead_at = np.concatenate(dead_at)
    na = np.linalg.norm(A, axis=1)
    mean_a = A.mean(0)
    e = mean_a / np.linalg.norm(mean_a)
    trV = float(A.var(0).sum())
    res = dict(seed=seed, N=N, mean_a=mean_a.tolist(), trV=trV, E_norm_a=float(na.mean()),
               dead_frac_256=float((dead_at <= 256).mean()), prefix={}, cuts={})
    for i, d in enumerate(PREFIX_D):
        keys = ndx.void_keys(np.concatenate(pk[d]))
        st = stats_for_keys(keys, na, N)
        st['dead_frac'] = float((dead_at <= d).mean())
        st['dead_frac_amass'] = 0.0
        st['minact_hist'] = np.bincount(minact[:, i], minlength=9).tolist()
        st['rank1_amass'] = float(na[minact[:, i] == 1].sum() / na.sum())
        res['prefix'][str(d)] = st
    for c in CUTS:
        keys = ndx.void_keys(np.concatenate(sk[c]))
        _, inv, cnt = np.unique(keys, return_inverse=True, return_counts=True)
        ma = np.bincount(inv, weights=na)
        top = int(np.argmax(ma))
        intop = inv == top
        # E[a] restricted to the top downstream class and the rest (MC estimates)
        rest = A[~intop].sum(0) / N
        res['cuts'][str(c)] = dict(distinct=int(len(cnt)), top_amass=float(ma[top] / ma.sum()),
                                   top_prob=float(cnt[top] / N),
                                   rest_contrib_nmse=float(np.sum(rest ** 2) / trV),
                                   **{f'k_amass_{q}': coverage(ma, q) for q in QS})
    res['seconds'] = time.time() - t0
    json.dump(res, open(outp, 'w'), indent=1)
    print(seed, 'N', N, 'sec %.0f' % res['seconds'])
    for d in PREFIX_D:
        s = res['prefix'][str(d)]
        print(' d=%2d distinct %8d n1 %8d chao1 %.3g H %.1f/%.1f bits | GTunseen p %.3g a %.3g | k_prob %s | k_amass %s | dead %.4f rank1_amass %.3f' % (
            d, s['distinct'], s['n1'], s['chao1'], s['H_plugin_bits'], s['H_chaoshen_bits'], s['gt_unseen_prob'], s['gt_unseen_amass'],
            [s[f'k_prob_{q}'] for q in QS], [s[f'k_amass_{q}'] for q in QS], s['dead_frac'], s['rank1_amass']))
    for c in CUTS:
        s = res['cuts'][str(c)]
        print(' cut=%3d classes %7d top amass %.6f prob %.6f rest nMSE %.2e k_amass %s' % (
            c, s['distinct'], s['top_amass'], s['top_prob'], s['rest_contrib_nmse'], [s[f'k_amass_{q}'] for q in QS]))


if __name__ == '__main__':
    main()
