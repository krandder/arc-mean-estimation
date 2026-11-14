"""Pattern map, chain (DP) estimator and structure search for a bias-free n x L ReLU net (Kelvin via main, 3 Nov).
MEASURED (exploratory); exact ingredients NUMERICAL where marked.

Paths: 2^log2 Gaussian inputs x = r theta (gates depend only on the direction theta; the radius enters only through
first moments, which carry E|x| exactly when the cell moments are exact).

1. Pattern map: per layer distinct gate patterns, how many cover 99% / 99.99% of the paths; joint cells vs the product
   of per-layer counts; nonzero transitions between consecutive layers; H(s_{l+1} | s_l) vs H(s_{l+1} | s_1..s_l)
   (plug-in entropies in bits; biased low when histories are nearly unique, so the number of distinct histories is
   reported too).
2. Chain estimator: state per layer pattern s: mass p_l(s) and internal mean m_l(s) = E[h_l 1{s_l = s}].
   m_1(s) from the cells; m_{l+1}(t) = D_t W_{l+1} sum_s T_l(t | s) m_l(s), T_l(t | s) = P(s_{l+1} = t | s_l = s).
   This is exact if (sufficient, not necessary) E[h_l 1{s_l = s, s_{l+1} = t}] = T_l(t | s) m_l(s) (the Markov / closure assumption), so the gap
   to the exact-cell sum sum_C A_C m_C, computed from the SAME ingredients, is the chain assumption's error alone.
   Two ingredient sets: (e) empirical (cell masses = path frequencies, cell moments = path averages; then the exact-cell
   sum is the paths' plain mean); (x) exact cell moments (cached from cone_tree.py, n <= 6) and exact cell masses
   (lib/cones.measure, n <= 5), else frequencies.
3. Structure: (a) per later-layer unit, how many earlier gate bits (greedy) bring H(g | chosen bits) within 0.05 bit
   of H(g | all earlier bits); (b) transition sparsity and mass-weighted effective rank (99% of Frobenius energy of
   sqrt(p(s)) T(t | s)); (c) total correlation sum_i H(g_i) - H(s_l) per layer and the largest pairwise mutual
   information (do units switch independently?); (d) units irrelevant to the output mean: freeze a unit's gate on or
   off (common random numbers) and measure the change of the output mean in nMSE; irrelevant if below MC's 1/N.
Usage: pattern_chain.py SEED n [L=4] [--log2 20]
"""
import argparse, json, math, os, sys, time
import numpy as np
from scipy.stats import qmc
from scipy.special import ndtri
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
import cones  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int, nargs='?', default=4)
ap.add_argument('--log2', type=int, default=20)
ap.add_argument('--log2truth', type=int, default=26)
ap.add_argument('--exact_mass_max_n', type=int, default=5)
ap.add_argument('--skip_bits', action='store_true')
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
t0 = time.time()
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
W = [w.double().numpy() for w in ar.weights(seed, n, L)]
N = 1 << args.log2
X = np.random.RandomState(seed).standard_normal((N, n))          # same paths as cone_tree.py (cache alignment)


def forward(X, freeze=None):
    """Returns per-layer hidden states and gates; freeze = (layer, unit, value) forces one gate."""
    h = X; H = []; G = []
    for l in range(L):
        z = h @ W[l].T; g = z > 0
        if freeze is not None and freeze[0] == l:
            g = g.copy(); g[:, freeze[1]] = freeze[2]
        h = z * g; H.append(h); G.append(g)
    return H, G


H, G = forward(X)
F = H[-1]


def ids_of(bits):
    _, inv, cnt = np.unique(np.packbits(bits, axis=1), axis=0, return_inverse=True, return_counts=True)
    return inv.ravel(), cnt


def entropy(cnt):
    q = cnt[cnt > 0] / cnt.sum()
    return float(-(q * np.log2(q)).sum())


res = dict(seed=seed, n=n, L=L, paths=N, layers=[])
lid = []; lcnt = []
for l in range(L):
    ii, cc = ids_of(G[l]); lid.append(ii); lcnt.append(cc)
    srt = np.sort(cc)[::-1]; cum = np.cumsum(srt) / N
    res['layers'].append(dict(layer=l + 1, patterns=int(len(cc)), for99=int(np.searchsorted(cum, 0.99) + 1),
                              for9999=int(min(len(cc), np.searchsorted(cum, 0.9999) + 1)), H=entropy(cc)))
cid, ccnt = ids_of(np.concatenate(G, 1))
res['cells'] = int(len(ccnt)); res['prod_layer_patterns'] = int(np.prod([len(c) for c in lcnt]))
hist = [lid[0]]
for l in range(1, L):
    hist.append(ids_of(np.concatenate(G[:l + 1], 1))[0])
res['transitions'] = []
for l in range(L - 1):
    pair = lid[l].astype(np.int64) * (lid[l + 1].max() + 1) + lid[l + 1]
    _, pc = np.unique(pair, return_counts=True)
    hp = hist[l].astype(np.int64) * (lid[l + 1].max() + 1) + lid[l + 1]
    _, hpc = np.unique(hp, return_counts=True)
    _, hc = np.unique(hist[l], return_counts=True)
    H_markov = entropy(pc) - res['layers'][l]['H']
    H_full = entropy(hpc) - entropy(hc)
    # (b) sparsity and effective rank of the mass-weighted transition matrix
    a, b = lid[l], lid[l + 1]
    na, nb = a.max() + 1, b.max() + 1
    rank99 = None
    if na * nb <= 4e7:
        M = np.zeros((na, nb)); np.add.at(M, (a, b), 1.0 / N)
        pa = M.sum(1, keepdims=True); Tm = np.sqrt(pa) * (M / np.maximum(pa, 1e-300))
        sv = np.linalg.svd(Tm, compute_uv=False); e = np.cumsum(sv ** 2) / (sv ** 2).sum()
        rank99 = int(np.searchsorted(e, 0.99) + 1)
    res['transitions'].append(dict(frm=l + 1, to=l + 2, nonzero=int(len(pc)), dense=int(na * nb), H_markov=H_markov,
                                   H_full=H_full, histories=int(len(hc)), eff_rank99=rank99))
print(f'[{time.time() - t0:.0f}s] map done: cells {res["cells"]}, product of layer counts {res["prod_layer_patterns"]}', flush=True)

# ---------------- truth, VF, RQMC with the same number of paths
reps = []
for r_ in range(4):
    eng = qmc.Sobol(d=n, scramble=True, seed=seed * 1009 + 77 + r_); acc = np.zeros(n); NR = 1 << (args.log2truth - 2)
    for _ in range(max(1, NR >> 22)):
        acc += forward(ndtri(np.clip(eng.random(min(NR, 1 << 22)), 1e-15, 1 - 1e-15)))[0][-1].sum(0)
    reps.append(acc / NR)
reps = np.array(reps); m0 = reps.mean(0)
VF = float(F.var(0).sum()); truth_noise = float(reps.var(0, ddof=1).sum() / 4 / VF)
rq = []
for r_ in range(4):
    eng = qmc.Sobol(d=n, scramble=True, seed=seed * 31 + r_)
    rq.append(float(((forward(ndtri(np.clip(eng.random(N), 1e-15, 1 - 1e-15)))[0][-1].mean(0) - m0) ** 2).sum() / VF))
nm = lambda e: float(((e - m0) ** 2).sum() / VF)
res.update(truth_noise=truth_noise, mc=1.0 / N, rqmc=float(np.mean(rq)))


# ---------------- chain estimator
def chain(m1, T):
    """m1: dict s -> E[h_1 1{s_1 = s}] (n-vector); T[l]: dict s -> list of (t, prob)."""
    m = m1
    for l in range(L - 1):
        nxt = {}
        for s, vec in m.items():
            for t, pr in T[l].get(s, ()):
                nxt[t] = nxt.get(t, 0) + pr * vec
        m = {t: (gpat[l + 1][t] * (W[l + 1] @ v)) for t, v in nxt.items()}
    return sum(m.values())


# representative gate vector per layer pattern
gpat = []
for l in range(L):
    first = np.zeros(lid[l].max() + 1, dtype=np.int64); first[lid[l][::-1]] = np.arange(N)[::-1]
    gpat.append(G[l][first].astype(float))


def transitions_from(mass_of_pair):
    T = []
    for l in range(L - 1):
        d = {}
        for (s, t), w in mass_of_pair[l].items():
            d.setdefault(s, []).append((t, w))
        for s in d:
            tot = sum(w for _, w in d[s]); d[s] = [(t, w / tot) for t, w in d[s]]
        T.append(d)
    return T


# (e) empirical ingredients
m1e = {}
S = np.zeros((lid[0].max() + 1, n)); np.add.at(S, lid[0], H[0]); m1e = {s: S[s] / N for s in range(len(S))}
pairs_e = []
for l in range(L - 1):
    pr = lid[l].astype(np.int64) * (lid[l + 1].max() + 1) + lid[l + 1]
    u, c = np.unique(pr, return_counts=True)
    pairs_e.append({(int(k // (lid[l + 1].max() + 1)), int(k % (lid[l + 1].max() + 1))): v / N for k, v in zip(u, c)})
t1 = time.time(); est_chain_e = chain(m1e, transitions_from(pairs_e)); t_chain = time.time() - t1
est_cells_e = F.mean(0)
res['empirical'] = dict(chain_vs_cells=float(((est_chain_e - est_cells_e) ** 2).sum() / VF), chain_err=nm(est_chain_e),
                        cells_err=nm(est_cells_e), chain_secs=t_chain)
print(f'[{time.time() - t0:.0f}s] empirical: chain vs cells {res["empirical"]["chain_vs_cells"]:.2e}, chain err {res["empirical"]["chain_err"]:.2e}, '
      f'cells (= MC) err {res["empirical"]["cells_err"]:.2e}', flush=True)

# order-k chains (empirical ingredients): state at layer l = patterns of layers max(1, l-k+1)..l; order L-1 = cells
def chain_order(k):
    st = [ids_of(np.concatenate(G[max(0, l - k + 1):l + 1], 1))[0] for l in range(L)]
    S0 = np.zeros((st[0].max() + 1, n)); np.add.at(S0, st[0], H[0]); m = S0 / N
    for l in range(L - 1):
        a, b = st[l], st[l + 1]; nb = b.max() + 1
        key = a.astype(np.int64) * nb + b
        u, inv_, c = np.unique(key, return_inverse=True, return_counts=True)
        ua, ub = u // nb, u % nb
        pa = np.bincount(a, minlength=m.shape[0]).astype(float)
        T = c / pa[ua]
        first = np.zeros(nb, dtype=np.int64); first[b[::-1]] = np.arange(N)[::-1]
        gate = G[l + 1][first].astype(float)                               # layer-(l+1) gates of each new state
        nxt = np.zeros((nb, n)); np.add.at(nxt, ub, T[:, None] * m[ua])
        m = gate * (nxt @ W[l + 1].T)
    return m.sum(0), int(sum(x.max() + 1 for x in st))


res['orders'] = []
for k in range(1, L + 1):
    e_k, ns = chain_order(k)
    res['orders'].append(dict(order=k, states=ns, chain_vs_cells=float(((e_k - est_cells_e) ** 2).sum() / VF), err=nm(e_k)))
print('order-k chains (states, chain vs cells):', [(o['order'], o['states'], '%.2e' % o['chain_vs_cells']) for o in res['orders']], flush=True)

# (x) exact ingredients where cached
cache = os.path.join(RUNS, f'cell_moments_n{n}_L{L}_s{seed}.npz')
keys, first, inv = np.unique(np.packbits(np.concatenate(G, 1), axis=1), axis=0, return_index=True, return_inverse=True)[:3]
zc = np.load(cache) if os.path.exists(cache) else None
if zc is not None and len(keys) == len(zc['m']) and (keys == zc['keys']).all():
    Ac = zc['A']; mc = zc['m']
    NC = len(keys); pc_freq = np.bincount(inv.ravel(), minlength=NC) / N
    mass_kind = 'path frequencies'
    pc = pc_freq
    if n <= args.exact_mass_max_n:
        pcx = np.zeros(NC); t2 = time.time()
        for c in range(NC):
            x = X[first[c]]; M = np.eye(n); rows = []
            for l in range(L):
                Gl = W[l] @ M; on = (Gl @ x) > 0; rows.append(np.where(on[:, None], Gl, -Gl)); M = on[:, None] * Gl
            pcx[c] = cones.measure(np.concatenate(rows))
        pc = pcx; mass_kind = f'exact (cones.measure, {time.time() - t2:.0f}s; sum over seen cells {pcx.sum():.8f})'
    cl = [lid[l][first] for l in range(L)]                              # per-cell layer pattern ids
    A1 = np.stack([gpat[0][cl[0][c]][:, None] * W[0] for c in range(NC)])
    S1 = {}
    for c in range(NC):
        S1[cl[0][c]] = S1.get(cl[0][c], 0) + A1[c] @ mc[c]
    pairs_x = []
    for l in range(L - 1):
        d = {}
        for c in range(NC):
            k = (int(cl[l][c]), int(cl[l + 1][c])); d[k] = d.get(k, 0) + pc[c]
        pairs_x.append(d)
    est_chain_x = chain(S1, transitions_from(pairs_x))
    est_cells_x = np.einsum('cij,cj->i', Ac, mc)
    res['exact'] = dict(mass=mass_kind, chain_vs_cells=float(((est_chain_x - est_cells_x) ** 2).sum() / VF),
                        chain_err=nm(est_chain_x), cells_err=nm(est_cells_x))
    print(f'[{time.time() - t0:.0f}s] exact moments ({mass_kind}): chain vs cells {res["exact"]["chain_vs_cells"]:.2e}, chain err '
          f'{res["exact"]["chain_err"]:.2e}, exact-cell err {res["exact"]["cells_err"]:.2e}', flush=True)
res['chain_states'] = int(sum(len(c) for c in lcnt)); res['chain_transitions'] = int(sum(t['nonzero'] for t in res['transitions']))

# ---------------- structure
# (a) past bits needed per unit
Gall = np.concatenate(G, 1).astype(np.uint8)
sub = slice(0, min(N, 1 << 18))


def cond_H(target, cols):
    if not cols:
        return entropy(np.bincount(target, minlength=2))
    key = ids_of(Gall[sub][:, cols].astype(bool))[0].astype(np.int64) * 2 + target
    _, kc = np.unique(key, return_counts=True); _, cc = np.unique(key // 2, return_counts=True)
    return entropy(kc) - entropy(cc)


sub = slice(0, min(N, 1 << 18))
bits_needed = []
for l in (range(1, L) if not args.skip_bits else []):
    past = list(range(l * n))
    for i in range(n):
        tgt = Gall[sub, l * n + i]
        h_all = cond_H(tgt, past) if len(past) <= 64 else None
        chosen = []; hcur = cond_H(tgt, [])
        while hcur > h_all + 0.05 and len(chosen) < len(past):
            best = min((c for c in past if c not in chosen), key=lambda c: cond_H(tgt, chosen + [c]))
            chosen.append(best); hcur = cond_H(tgt, chosen)
        bits_needed.append(dict(layer=l + 1, unit=i, H_marg=cond_H(tgt, []), H_given_all_past=h_all, bits=len(chosen),
                                from_prev_layer=sum(1 for c in chosen if c // n == l - 1)))
res['bits_needed'] = bits_needed
# (c) independence within layers
tc = []
for l in range(L):
    hm = sum(entropy(np.bincount(G[l][:, i], minlength=2)) for i in range(n))
    mi = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            hij = entropy(np.bincount(G[l][:, i] * 2 + G[l][:, j], minlength=4))
            mi = max(mi, entropy(np.bincount(G[l][:, i], minlength=2)) + entropy(np.bincount(G[l][:, j], minlength=2)) - hij)
    tc.append(dict(layer=l + 1, sum_unit_H=hm, H_pattern=res['layers'][l]['H'], total_corr=hm - res['layers'][l]['H'], max_pair_MI=mi))
res['independence'] = tc
# (d) units irrelevant to the output mean (common random numbers)
rel = []
Xs = X[:1 << 18]; Fs = forward(Xs)[0][-1].mean(0)
for l in range(L):
    for i in range(n):
        d_on = forward(Xs, (l, i, True))[0][-1].mean(0); d_off = forward(Xs, (l, i, False))[0][-1].mean(0)
        e = min(((d_on - Fs) ** 2).sum(), ((d_off - Fs) ** 2).sum()) / VF
        rel.append(dict(layer=l + 1, unit=i, frac_on=float(G[l][:, i].mean()), freeze_nmse=float(e)))
res['irrelevant_units'] = int(sum(r['freeze_nmse'] < 1.0 / N for r in rel)); res['relevance'] = rel
res['secs'] = time.time() - t0
out = args.out or os.path.join(RUNS, f'pattern_chain_n{n}_L{L}_s{seed}.json')
json.dump(res, open(out, 'w'), default=float)
print(json.dumps({k: res[k] for k in ('seed', 'n', 'cells', 'prod_layer_patterns', 'chain_states', 'chain_transitions', 'mc', 'rqmc', 'truth_noise', 'irrelevant_units', 'secs')}))
print('layers', [(d['patterns'], d['for99'], d['for9999']) for d in res['layers']])
print('transitions', [(t['nonzero'], t['dense'], round(t['H_markov'], 3), round(t['H_full'], 3), t['histories'], t['eff_rank99']) for t in res['transitions']])
print('bits needed per unit (layer 2..L)', [b['bits'] for b in bits_needed], 'from prev layer', [b['from_prev_layer'] for b in bits_needed])
print('total correlation per layer', [round(t['total_corr'], 3) for t in tc], 'max pair MI', [round(t['max_pair_MI'], 3) for t in tc])
