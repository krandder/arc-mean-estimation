"""Registered evaluation runs E1 (merge residual profiles), E2 (pair laws), E3 (two-level merge samplers).
See PREREG.md. Usage: python scratch/run_eval.py N L SEED [--quick]. Writes runs/eval_n{N}_L{L}_s{SEED}.json and
runs/pairs_n{N}_L{L}_s{SEED}.npz. Unit input directions throughout (radius exact by homogeneity): outputs are
A(U) = h_L(U); V_ang = tr Var_U A (per net). Residuals are reported relative to V_ang.
"""
import os
import sys
import json
import math
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import bb
import chain3


def unit(X):
    return X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-300)


def ref_paths(W, l, C):
    """Gate masks and future outputs g_l(c) for reference states C (M, n)."""
    masks = [[] for _ in range(C.shape[0])]
    H = C.copy()
    for j in range(l, len(W)):
        Z = H @ W[j].T
        Mk = Z > 0
        for k in range(C.shape[0]):
            masks[k].append(Mk[k])
        H = np.where(Mk, Z, 0.0)
    return masks, H


def merges(W, l, Hl, assign, Cref, masks, gC):
    """Frozen and radial merges of states Hl (N, n) with assigned references (index into Cref)."""
    N, n = Hl.shape
    GF = np.zeros((N, n))
    for k in np.unique(assign):
        sel = np.where(assign == k)[0]
        GF[sel] = bb.frozen_apply(W, l, masks[k], Hl[sel])
    ratio = np.linalg.norm(Hl, axis=1) / np.maximum(np.linalg.norm(Cref[assign], axis=1), 1e-300)
    GR = ratio[:, None] * gC[assign]
    return GF, GR


def nearest_members(Ufit, centres, labels):
    """Index (into Ufit) of the fit point closest to each centre within its cluster (genuine reference states)."""
    idx = np.zeros(centres.shape[0], dtype=int)
    for k in range(centres.shape[0]):
        sel = np.where(labels == k)[0]
        if sel.size == 0:
            idx[k] = int(np.argmax(Ufit @ centres[k]))
        else:
            idx[k] = int(sel[np.argmax(Ufit[sel] @ centres[k])])
    return idx


def cell_spread(Uf, labels, centres):
    """Per-cell RMS angle of fit points to their centre (radians)."""
    out = np.zeros(centres.shape[0])
    for k in range(centres.shape[0]):
        sel = np.where(labels == k)[0]
        if sel.size:
            cos = np.clip(Uf[sel] @ centres[k], -1, 1)
            out[k] = math.sqrt(float(np.mean(np.arccos(cos) ** 2)))
    return out


def e1_layer(W, l, Hf, Ht, Af, At, Vang, rng, Ms, Ms2):
    L = len(W)
    Lp = L - l
    res = {'l': l, 'Lp': Lp}
    # cloud geometry
    Hall = np.vstack([Hf[l], Ht[l]])
    ev = bb.cloud_angular_spectrum(Hall)
    res['ang_var'] = float(ev.sum())
    res['PR'] = bb.participation_ratio(ev)
    k = np.arange(1, 11)
    res['ev_logslope_1_10'] = float(np.polyfit(k, np.log(np.maximum(ev[:10], 1e-300)), 1)[0])
    res['ev_top10_frac'] = [float(x) for x in (ev[:10] / ev.sum())]
    i = rng.integers(0, Hall.shape[0], 4096)
    j = rng.integers(0, Hall.shape[0], 4096)
    cos = np.sum(unit(Hall[i]) * unit(Hall[j]), axis=1)
    res['theta_median'] = float(np.median(np.arccos(np.clip(cos, -1, 1))))
    # mean propagation (Jensen gap) from layer l, using the 4096-point cloud mean
    m = Hall.mean(axis=0)
    gm = bb.forward(W, m[None, :], l)[0]
    mu = np.vstack([Af, At]).mean(axis=0)
    res['meanprop_err'] = float(np.sum((mu - gm) ** 2) / Vang)
    Uf, Ut = unit(Hf[l]), unit(Ht[l])
    # forward-only references (k-means on the past cloud's directions)
    res['fwd'] = {}
    for M in Ms:
        C, lab = bb.kmeans_dirs(Uf, M, rng)
        idx = nearest_members(Uf, C, lab)
        Cref = Hf[l][idx]
        masks, gC = ref_paths(W, l, Cref)
        a_t = np.argmax(Ut @ C.T, axis=1)
        GF, GR = merges(W, l, Ht[l], a_t, Cref, masks, gC)
        GFf, GRf = merges(W, l, Hf[l], lab, Cref, masks, gC)
        # per-cell best (chosen on fit), and the past-measurable rule (frozen iff Lp * spread < 2)
        eF = np.sum((Af - GFf) ** 2, axis=1)
        eR = np.sum((Af - GRf) ** 2, axis=1)
        useF = np.zeros(M, dtype=bool)
        for kk in range(M):
            sel = lab == kk
            if np.any(sel):
                useF[kk] = eF[sel].sum() < eR[sel].sum()
        spread = cell_spread(Uf, lab, C)
        ruleF = Lp * spread < 2.0
        GB = np.where(useF[a_t][:, None], GF, GR)
        GU = np.where(ruleF[a_t][:, None], GF, GR)
        d = {}
        for name, G in [('F', GF), ('R', GR), ('best', GB), ('rule', GU)]:
            Rr = At - G
            d['D_' + name] = float(np.mean(np.sum(Rr * Rr, axis=1)) / Vang)
            d['bias_' + name] = float(np.sum(Rr.mean(axis=0) ** 2) / Vang)
        d['frac_frozen_best'] = float(np.mean(useF[a_t]))
        d['frac_frozen_rule'] = float(np.mean(ruleF[a_t]))
        d['median_cell_spread'] = float(np.median(spread[spread > 0])) if np.any(spread > 0) else 0.0
        res['fwd'][str(M)] = d
    # two-sided references (k-means on trajectory signatures through the actual future)
    lm = l + Lp // 2
    res['two'] = {}
    if Lp >= 2:
        Hfm = bb.forward(W, Hf[l], l, lm)
        Htm = bb.forward(W, Ht[l], l, lm)
        Sf = np.hstack([Uf, unit(Hfm), unit(Af)]) / math.sqrt(3.0)
        St = np.hstack([Ut, unit(Htm), unit(At)]) / math.sqrt(3.0)
        for M in Ms2:
            C, lab = bb.kmeans_dirs(Sf, M, rng)
            idx = nearest_members(Sf, C, lab)
            Cref = Hf[l][idx]
            masks, gC = ref_paths(W, l, Cref)
            a_t = np.argmax(St @ C.T, axis=1)
            GF, GR = merges(W, l, Ht[l], a_t, Cref, masks, gC)
            GFf, GRf = merges(W, l, Hf[l], lab, Cref, masks, gC)
            eF = np.sum((Af - GFf) ** 2, axis=1)
            eR = np.sum((Af - GRf) ** 2, axis=1)
            useF = np.zeros(M, dtype=bool)
            for kk in range(M):
                sel = lab == kk
                if np.any(sel):
                    useF[kk] = eF[sel].sum() < eR[sel].sum()
            GB = np.where(useF[a_t][:, None], GF, GR)
            d = {}
            for name, G in [('F', GF), ('R', GR), ('best', GB)]:
                Rr = At - G
                d['D_' + name] = float(np.mean(np.sum(Rr * Rr, axis=1)) / Vang)
            res['two'][str(M)] = d
    return res


def e2_layer(W, l, rng, nref=16, per=16, deltas=(1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1.0)):
    n = W[0].shape[0]
    L = len(W)
    U0 = bb.sphere(rng, nref, n)
    rows = []
    for r in range(nref):
        u0 = U0[r]
        c = bb.forward(W, u0[None, :], 0, l)[0]
        masks = bb.gate_path(W, c, l)
        gc = bb.frozen_apply(W, l, masks, c[None, :])[0]
        for dlt in deltas:
            xi = rng.standard_normal((per, n))
            xi -= np.outer(xi @ u0, u0)
            xi = unit(xi)
            U = math.cos(dlt) * u0[None, :] + math.sin(dlt) * xi
            H = bb.forward(W, U, 0, l)
            phi = bb.angles_to(H, c)
            G = bb.forward(W, H, l)
            F = bb.frozen_apply(W, l, masks, H)
            ratio = np.linalg.norm(H, axis=1) / max(np.linalg.norm(c), 1e-300)
            R = ratio[:, None] * gc[None, :]
            g2 = np.maximum(np.sum(G * G, axis=1), 1e-300)
            rF = np.sum((G - F) ** 2, axis=1) / g2
            rR = np.sum((G - R) ** 2, axis=1) / g2
            dis = np.zeros(per)
            hh = H.copy()
            for j, m in zip(range(l, L), masks):
                z = hh @ W[j].T
                dis += np.sum((z > 0) != m[None, :], axis=1)
                hh = np.maximum(z, 0.0)
            for q in range(per):
                rows.append((r, dlt, phi[q], rF[q], rR[q], dis[q]))
    return np.array(rows)


def e3_r(W, r, Hf, Ht, Af, At, Vang, rng, Ms):
    """Two-level merge samplers at prefix depth r: level 1 = merge G (cost r/L per sample), level 2 = A - G."""
    L = len(W)
    Lp = L - r
    Uf, Ut = unit(Hf[r]), unit(Ht[r])
    out = {'r': r}
    # random-direction reference (as in the unrestricted lane), radial merge
    q = bb.sphere(rng, 1, W[0].shape[0])
    cq = bb.forward(W, q, 0, r)
    masks, gC = ref_paths(W, r, cq)
    a_t = np.zeros(Ht[r].shape[0], dtype=int)
    _, GR = merges(W, r, Ht[r], a_t, cq, masks, gC)
    out['randref_R'] = level_stats(At, GR, Vang, r, L, 0.0, 1, Lp)
    for M in Ms:
        C, lab = bb.kmeans_dirs(Uf, M, rng)
        idx = nearest_members(Uf, C, lab)
        Cref = Hf[r][idx]
        masks, gC = ref_paths(W, r, Cref)
        a_t = np.argmax(Ut @ C.T, axis=1)
        GF, GR = merges(W, r, Ht[r], a_t, Cref, masks, gC)
        spread = cell_spread(Uf, lab, C)
        ruleF = Lp * spread < 2.0
        GU = np.where(ruleF[a_t][:, None], GF, GR)
        fr = float(np.mean(ruleF[a_t]))
        out[f'M{M}_R'] = level_stats(At, GR, Vang, r, L, 0.0, M, Lp)
        out[f'M{M}_rule'] = level_stats(At, GU, Vang, r, L, fr, M, Lp)
    return out


def level_stats(A, G, Vang, r, L, frac_frozen, M, Lp):
    V1 = float(np.sum(G.var(axis=0)) / Vang)
    V2 = float(np.sum((A - G).var(axis=0)) / Vang)
    C1 = r / L
    C2 = 1.0 + frac_frozen * Lp / L
    ideal = (math.sqrt(V1 * C1) + math.sqrt(V2 * C2)) ** 2
    setup = 1.0 + 2.0 * M * Lp / L  # one reference-path pass at least; per reference: future pass + frozen apply
    return {'V1': V1, 'V2': V2, 'C1': C1, 'C2': C2, 'ideal': ideal, 'setup_passes': setup,
            'frac_frozen': frac_frozen}


def main():
    n, L, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    quick = '--quick' in sys.argv
    t0 = time.time()
    W = bb.make_weights(seed, n, L)
    rng = np.random.default_rng([seed, n, L, 7])
    Nfit = 512 if quick else 2048
    U = bb.sphere(rng, 2 * Nfit, n)
    fit, test = U[:Nfit], U[Nfit:]
    l1 = sorted(set([max(1, L // 4), L // 2, (3 * L) // 4, (7 * L) // 8]))
    l3 = sorted(set([max(1, L // 8), max(1, L // 4), L // 2]))
    keep = set(l1) | set(l3) | {L}
    Hf = bb.forward_keep(W, fit, keep)
    Ht = bb.forward_keep(W, test, keep)
    Af, At = Hf[L], Ht[L]
    Vang = float(np.sum(At.var(axis=0)))
    mu = At.mean(axis=0)
    res = {'n': n, 'L': L, 'seed': seed, 'Nfit': Nfit, 'Vang': Vang, 'mu2': float(mu @ mu),
           'dead': bool(Vang <= 1e-300)}
    if res['dead']:
        json.dump(res, open(f'runs/eval_n{n}_L{L}_s{seed}.json', 'w'), indent=1)
        print('dead net', flush=True)
        return
    Ms = [1, 4, 16, 64] if quick else [1, 4, 16, 64, 256]
    Ms2 = [4, 16] if quick else [4, 16, 64]
    res['E1'] = []
    for l in l1:
        res['E1'].append(e1_layer(W, l, Hf, Ht, Af, At, Vang, rng, Ms, Ms2))
        print(f'E1 l={l} done {time.time() - t0:.0f}s', flush=True)
    pairs = {}
    for l in l1:
        pairs[f'l{l}'] = e2_layer(W, l, rng, nref=4 if quick else 16, per=8 if quick else 16)
        print(f'E2 l={l} done {time.time() - t0:.0f}s', flush=True)
    np.savez_compressed(f'runs/pairs_n{n}_L{L}_s{seed}.npz', **pairs)
    res['E3'] = []
    for r in l3:
        res['E3'].append(e3_r(W, r, Hf, Ht, Af, At, Vang, rng, [1, 16, 64] if quick else [1, 16, 64, 256]))
        print(f'E3 r={r} done {time.time() - t0:.0f}s', flush=True)
    res['seconds'] = time.time() - t0
    json.dump(res, open(f'runs/eval_n{n}_L{L}_s{seed}.json', 'w'), indent=1)
    print(f'done {res["seconds"]:.0f}s', flush=True)


if __name__ == '__main__':
    main()
