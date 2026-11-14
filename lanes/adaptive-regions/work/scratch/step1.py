"""Step 1 of the certified-linear backward probe: exact pieces (eps = 0).

For one net, N_tr + N_te Gaussian inputs are pushed through; every gate is recorded. At layer l (state h_l, l = L-1
down to 0) the exact linear pieces of the remaining net are gate-pattern cones:
- vector pieces (all n outputs at once): the suffix pattern of layers l+1..L, every unit (output gates included);
- per-output pieces for output j: the suffix pattern of layers l+1..L-1 together with j's own gate; the cones on
  which j's gate is off all carry the functional 0 and are merged into one zero piece ("merged"); the unmerged count
  ("cones") keeps every cone separate.
Pieces are ranked by their frequency on the training inputs; coverage is measured on held-out inputs (fraction of
held-out states in the top-K pieces), so a piece list never covers its own sample by construction. Also: the number of
pieces (and bits = log2) needed for 50 / 90 / 99% held-out coverage (None = not reached with the training pieces),
the variance share of covered cases per output, switching units per layer (gate not constant on >= 99.9% of inputs),
and a collision estimate of the effective number of vector pieces. MEASURED (exploratory).
Usage: step1.py SEED n L [--log2N 17] [--out runs/step1_n256_L32_s200.json]
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--log2N', type=int, default=17, help='log2 of each of train and held-out sizes')
ap.add_argument('--out', default=None)
ap.add_argument('--chunk', type=int, default=1 << 13)
ap.add_argument('--stop_after_zero', type=int, default=3,
                help='after this many consecutive layers with every per-output on/switching and vector coverage '
                     '(K = 1000) below 1e-4, skip the per-output analysis of earlier layers (vector stats continue)')
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
N = 1 << args.log2N
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step1_n{n}_L{L}_s{seed}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
words = (n + 63) // 64
rs = np.random.RandomState(777)
SALT = rs.randint(1, 2 ** 62, size=(L, words), dtype=np.int64).astype(np.uint64)


def mix(x):
    """splitmix64 finaliser (uint64 arrays, wrapping arithmetic): a bijective, well-mixing 64-bit hash."""
    x = x ^ (x >> np.uint64(30)); x = x * np.uint64(0xBF58476D1CE4E5B9)
    x = x ^ (x >> np.uint64(27)); x = x * np.uint64(0x94D049BB133111EB)
    return x ^ (x >> np.uint64(31))


@torch.no_grad()
def run(gen_seed, M):
    gen = torch.Generator().manual_seed(gen_seed)
    hl = np.zeros((L, M), dtype=np.uint64)          # per-layer pattern hash
    gates_out = np.zeros((M, n), dtype=bool)        # output-layer gates
    F = np.zeros((M, n), dtype=np.float32)
    sw_cnt = np.zeros((L, n), dtype=np.int64)       # count of 'on' per unit (for switching units)
    done = 0
    while done < M:
        k = min(args.chunk, M - done)
        h = torch.randn(k, n, generator=gen)
        for l in range(L):
            z = h @ W[l].T
            g = (z > 0).numpy()
            sw_cnt[l] += g.sum(0)
            pb = np.packbits(g, axis=1, bitorder='little')                      # (k, n/8)
            pad = words * 8 - pb.shape[1]
            if pad:
                pb = np.concatenate([pb, np.zeros((k, pad), dtype=np.uint8)], 1)
            w64 = pb.view(np.uint64)                                            # (k, words)
            hw = np.zeros(k, dtype=np.uint64)
            for wi in range(words):                       # sequential mixing: order-sensitive, nonlinear
                hw = mix(hw ^ mix(w64[:, wi] ^ SALT[l, wi]))
            hl[l, done:done + k] = hw
            h = torch.relu(z)
            if l == L - 1:
                gates_out[done:done + k] = g
        F[done:done + k] = h.numpy()
        done += k
    return hl, gates_out, F, sw_cnt


hl_tr, g_tr, F_tr, on_tr = run(1_000_000 + seed, N)
hl_te, g_te, F_te, on_te = run(2_000_000 + seed, N)
t_fwd = time.time() - t0


def suffix_hashes(hl, include_last):
    """S[l] = hash of the gates of layers l+1..L-1 (include_last: ..L). Index l = 0..L-1 (state h_l)."""
    M = hl.shape[1]
    S = np.zeros((L, M), dtype=np.uint64)
    acc = np.zeros(M, dtype=np.uint64)
    top = L if include_last else L - 1                                # layers (1-based) top..l+1 are folded in
    # state h_l is followed by layers l+1..L; hl[k] is layer k+1's pattern
    for l in range(L - 1, -1, -1):
        # fold layer l+1 (index l) if it is part of the suffix
        if (l + 1) <= top:
            acc = mix(acc ^ mix(hl[l] + np.uint64(l + 1)))
        S[l] = acc
    return S


Sv_tr, Sv_te = suffix_hashes(hl_tr, True), suffix_hashes(hl_te, True)        # vector pieces
Sp_tr, Sp_te = suffix_hashes(hl_tr, False), suffix_hashes(hl_te, False)      # per-output (layers l+1..L-1)


def ranks(train_keys, test_keys):
    """Rank (0 = most frequent on train) of each test key among train pieces; -1 if absent."""
    uniq, cnt = np.unique(train_keys, return_counts=True)
    order = np.argsort(-cnt, kind='stable')
    rank_of_uniq = np.empty(len(uniq), dtype=np.int64); rank_of_uniq[order] = np.arange(len(uniq))
    pos = np.searchsorted(uniq, test_keys)
    pos = np.clip(pos, 0, len(uniq) - 1)
    found = uniq[pos] == test_keys
    r = np.where(found, rank_of_uniq[pos], -1)
    return r, len(uniq), cnt[order]


KS = (1, 10, 100, 1000)
QS = (0.5, 0.9, 0.99)


def coverage_summary(r, n_train_pieces, weights=None):
    covered_rank = np.where(r >= 0, r, np.iinfo(np.int64).max)
    res = {}
    w = np.ones(len(r)) if weights is None else weights
    wsum = w.sum()
    for K in KS:
        res[f'cov_K{K}'] = float((w * (covered_rank < K)).sum() / wsum)
    srt = np.sort(covered_rank)
    for q in QS:
        idx = int(math.ceil(q * len(r))) - 1
        v = srt[idx]
        res[f'pieces_q{int(q * 100)}'] = (int(v) + 1) if v != np.iinfo(np.int64).max else None
    res['train_pieces'] = int(n_train_pieces)
    res['cov_all_train_pieces'] = float((r >= 0).mean())
    return res


# output classes
pz = 1.0 - (on_tr[L - 1] + on_te[L - 1]) / (2.0 * N)           # P(f_j = 0)
cls = np.where(pz >= 0.999, 'zero', np.where(pz <= 0.001, 'on', 'switching'))
var_j = F_te.astype(np.float64).var(0)
rms_j = np.sqrt((F_te.astype(np.float64) ** 2).mean(0))
mu_j = F_te.astype(np.float64).mean(0)
dev2 = (F_te.astype(np.float64) - mu_j[None, :]) ** 2           # per-sample squared deviation per output

# switching units per layer (gate constant on >= 99.9% of all inputs = fixed)
pon = (on_tr + on_te) / (2.0 * N)
fixed = (pon >= 0.999) | (pon <= 0.001)
switching_per_layer = (~fixed).sum(1).tolist()

def hbits(p):
    p = np.clip(p, 1e-15, 1 - 1e-15)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


H_layer = hbits(pon).sum(1)                              # sum of marginal gate entropies per layer (bits)
res = dict(n=n, L=L, seed=seed, N_train=N, N_test=N, t_forward=t_fwd, pon=pon.tolist(),
           H_marg_layer=H_layer.tolist(), classes={c: int((cls == c).sum()) for c in
           ('zero', 'on', 'switching')}, var_share_class={c: float(var_j[cls == c].sum() / var_j.sum()) for c in
           ('zero', 'on', 'switching')}, switching_units_per_layer=switching_per_layer,
           pz=pz.tolist(), cls=cls.tolist(), var_j=var_j.tolist(), rms_j=rms_j.tolist(), layers=[])
zero_run = 0
for l in range(L - 1, -1, -1):
    t1 = time.time()
    row = dict(l=l, back=L - 1 - l)
    # upper bound on the suffix-pattern entropy: sum of marginal gate entropies of layers l+1..L (vector) and
    # l+1..L-1 (per output, plus the output's own gate)
    row['H_marg_suffix_vector'] = float(H_layer[l:].sum())
    row['H_marg_suffix_hidden'] = float(H_layer[l:L - 1].sum())
    # vector pieces
    r, npieces, cnts = ranks(Sv_tr[l], Sv_te[l])
    row['vector'] = coverage_summary(r, npieces)
    # collisions among held-out (effective number of vector pieces)
    _, cc = np.unique(Sv_te[l], return_counts=True)
    C = float((cc * (cc - 1) / 2.0).sum()); P = N * (N - 1) / 2.0
    row['vector']['n_eff'] = (P / C) if C > 0 else None
    row['vector']['n_eff_lower95'] = (P / 3.0) if C == 0 else None
    row['vector']['distinct_test'] = int(len(cc))
    # per-output pieces
    per = []
    skip_per = zero_run >= args.stop_after_zero
    for j in (range(n) if not skip_per else []):
        on_tr_j = g_tr[:, j]; on_te_j = g_te[:, j]
        # merged: zero cells -> key 0; on cells -> 2*S + 1
        ktr = np.where(on_tr_j, Sp_tr[l] * np.uint64(2) + np.uint64(1), np.uint64(0))
        kte = np.where(on_te_j, Sp_te[l] * np.uint64(2) + np.uint64(1), np.uint64(0))
        rm, npm, _ = ranks(ktr, kte)
        sm = coverage_summary(rm, npm)
        # variance share of covered cases at each K
        for K in KS:
            cov = (rm >= 0) & (rm < K)
            sm[f'vshare_K{K}'] = float(dev2[cov, j].sum() / max(dev2[:, j].sum(), 1e-300))
        # unmerged cones: key = 2*S + gate
        ktr2 = Sp_tr[l] * np.uint64(2) + on_tr_j.astype(np.uint64)
        kte2 = Sp_te[l] * np.uint64(2) + on_te_j.astype(np.uint64)
        rc, npc, _ = ranks(ktr2, kte2)
        sc = coverage_summary(rc, npc)
        per.append(dict(merged=sm, cones=sc))
    row['per_output'] = per
    # class summaries (median over outputs in the class)
    summ = {}
    for c in ('zero', 'on', 'switching'):
        idx = np.where(cls == c)[0]
        if len(idx) == 0 or skip_per:
            continue
        d = {}
        for kind in ('merged', 'cones'):
            for K in KS:
                vals = [per[j][kind][f'cov_K{K}'] for j in idx]
                d[f'{kind}_cov_K{K}_median'] = float(np.median(vals))
                d[f'{kind}_cov_K{K}_vw'] = float(sum(per[j][kind][f'cov_K{K}'] * var_j[j] for j in idx) / max(var_j[idx].sum(), 1e-300))
            for q in QS:
                vals = [per[j][kind][f'pieces_q{int(q * 100)}'] for j in idx]
                vv = [v if v is not None else np.inf for v in vals]
                d[f'{kind}_pieces_q{int(q * 100)}_median'] = (float(np.median(vv)) if np.isfinite(np.median(vv)) else None)
        for K in KS:
            d[f'merged_vshare_K{K}_median'] = float(np.median([per[j]['merged'][f'vshare_K{K}'] for j in idx]))
        summ[c] = d
    row['class_summary'] = summ
    row['per_output_skipped'] = bool(skip_per)
    if not skip_per:
        mx = max([row['vector']['cov_K1000']] + [summ[c]['merged_cov_K1000_median'] for c in summ if c == 'on'] +
                 [summ[c]['cones_cov_K1000_median'] for c in summ])
        zero_run = zero_run + 1 if mx < 1e-4 else 0
    row['secs'] = time.time() - t1
    res['layers'].append(row)
    v = row['vector']
    if skip_per:
        print(f"l={l:2d} back={L - 1 - l:2d} vector: cov K1000 {v['cov_K1000']:.4f} distinct_test {v['distinct_test']} "
              f"H_marg_suffix {row['H_marg_suffix_vector']:.0f} bits (per-output skipped)", flush=True)
        continue
    print(f"l={l:2d} back={L - 1 - l:2d} vector: cov K1 {v['cov_K1']:.3f} K10 {v['cov_K10']:.3f} K100 {v['cov_K100']:.3f} "
          f"K1000 {v['cov_K1000']:.3f} pieces50 {v['pieces_q50']} distinct_test {v['distinct_test']} | " +
          ' | '.join(f"{c}: m.K1 {summ[c]['merged_cov_K1_median']:.3f} m.K1000 {summ[c]['merged_cov_K1000_median']:.3f} "
                     f"c.K1000 {summ[c]['cones_cov_K1000_median']:.3f}" for c in summ) + f"  ({row['secs']:.0f}s)", flush=True)

os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(res, open(out, 'w'))
print('wrote', out, 'total', time.time() - t0)
