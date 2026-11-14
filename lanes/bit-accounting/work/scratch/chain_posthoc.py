"""Post-hoc analysis of the saved S2 chains (review round 1, findings 8 and 9). CPU, float32, 2 threads.
For each chain (runs/S_chain/C_*.pt), code size b and transition i, on 2^17 fresh inputs split into halves A and B:
  - trivial: accuracy of the best constant predictor of each next-code bit (weighted by the code law), output entropy;
  - bayes: held-out accuracy of the per-code majority map fitted on A (the best any map can do from c_i, up to
    estimation), per bit and for the whole next code (whole-code accuracy is invariant under all relabellings);
  - ptf_d (d = 1, 2): held-out per-bit accuracy on B of a degree-d threshold function fitted on A (logistic
    regression on monomials, fitted lower bound);
  - junta_s (s = 1, 2, 3; b <= 12): best s-junta by exhaustive subset enumeration (lookup table fitted on A, held-out
    on B);
  - matched-output null: the same statistics after the next codes are reassigned among input codes by a random
    permutation of the reachable input codes (the output law is kept, the structure is destroyed).
Whitening frames are recomputed on CPU from a fresh pilot (statistically equivalent to the GPU frames; a small
fraction of codes near bit boundaries can differ).
-> results/S2_posthoc.json"""
import glob
import itertools
import json
import os
import sys

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gpu_src', 'lib'))
import smallnets as sn  # noqa: E402

torch.set_num_threads(2)
BS = [4, 8, 12, 16]
K, M = 16, 4


class Chain(nn.Module):
    def __init__(self, n, layers, cls):
        super().__init__()
        mk = lambda d_in: (sn.BMLP(M, d_in, K, n, 1, act='relu') if cls == 'local' else  # noqa: E731
                           sn.BMLP(M, d_in, K, 256, 3))
        self.enc = nn.ModuleList([mk(n if cls == 'local' else 2 * n) for _ in layers])
        self.dec = nn.ModuleList([sn.BMLP(M, K, n, 256, 3, last_scale=0.0) for _ in layers])
        self.T = nn.ModuleList([sn.BMLP(M, K, K, 256, 2) for _ in layers[:-1]])
        self.register_buffer('mask', torch.zeros(M, 1, K))


def codes_of(ch, i, H, A, frames, fr_a, cls):
    fr = frames[i]
    x = (H - fr['m']) @ fr['Sm12']
    if cls == 'unres':
        x = torch.cat([x, (A - fr_a['m']) @ fr_a['Sm12']], -1)
    with torch.no_grad():
        z = ch.enc[i](x.unsqueeze(0).expand(M, *x.shape))
    return torch.where(z > 0, 1.0, -1.0)


def idx(C):
    b = C.shape[1]
    return ((C < 0).long() * (1 << torch.arange(b))).sum(1)


def majority_table(ci, Y, b):
    """Majority of each output bit given the input code index (dict as tensors over 2^b, NaN where unseen)."""
    N = 2 ** b
    s = torch.zeros(N, Y.shape[1]).index_add_(0, ci, Y)
    cnt = torch.bincount(ci, minlength=N).float()
    return torch.where(s >= 0, 1.0, -1.0), cnt


def whole_code_bayes(ci_A, cj_A, ci_B, cj_B, b):
    """Held-out accuracy of predicting the whole next code by the most frequent next code given the current code."""
    key = ci_A * (2 ** b) + cj_A
    u, cnt = torch.unique(key, return_counts=True)
    src, dst = u // (2 ** b), u % (2 ** b)
    order = torch.argsort(cnt, descending=True)
    best = {}
    for s_, d_ in zip(src[order].tolist(), dst[order].tolist()):
        if s_ not in best:
            best[s_] = d_
    pred = torch.tensor([best.get(int(c), -1) for c in ci_B.tolist()])
    return float((pred == cj_B).float().mean())


def monomials(C, deg):
    b = C.shape[1]
    f = [torch.ones(C.shape[0], 1)]
    for d in range(1, deg + 1):
        for S in itertools.combinations(range(b), d):
            f.append(C[:, list(S)].prod(1, keepdim=True))
    return torch.cat(f, 1)


def ptf_heldout(CA, YA, CB, YB, deg, steps=300):
    XA, XB = monomials(CA, deg), monomials(CB, deg)
    W = torch.zeros(XA.shape[1], YA.shape[1], requires_grad=True)
    opt = torch.optim.Adam([W], lr=0.05)
    tA = (YA > 0).float()
    for _ in range(steps):
        loss = nn.functional.binary_cross_entropy_with_logits(XA @ W, tA)
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        return (((XB @ W) > 0).float() == (YB > 0).float()).float().mean(0).numpy()


def junta_heldout(ciA_bits, YA, ciB_bits, YB, s):
    """Best s-junta per output bit by exhaustive enumeration (table fitted on A), held-out accuracy on B."""
    b = ciA_bits.shape[1]
    best = np.zeros(YA.shape[1])
    yA, yB = (YA > 0).long(), (YB > 0).long()
    for S in itertools.combinations(range(b), s):
        kA = sum(ciA_bits[:, k] << t for t, k in enumerate(S))
        kB = sum(ciB_bits[:, k] << t for t, k in enumerate(S))
        for j in range(YA.shape[1]):
            p1 = torch.bincount(kA, weights=yA[:, j].float(), minlength=2 ** s)
            p0 = torch.bincount(kA, weights=(1 - yA[:, j]).float(), minlength=2 ** s)
            tab = (p1 >= p0).long()
            acc = float((tab[kB] == yB[:, j]).float().mean())
            best[j] = max(best[j], acc)
    return best


def stats(ciA, CA, YA, ciB, CB, YB, b, rng):
    out = {}
    pA = (YA > 0).float().mean(0)
    pB = (YB > 0).float().mean(0)
    out['trivial'] = float(torch.where(pA >= 0.5, pB, 1 - pB).mean())
    q = pB.clamp(1e-9, 1 - 1e-9)
    out['out_entropy_bits'] = float((-(q * torch.log2(q) + (1 - q) * torch.log2(1 - q))).sum())
    tab, cnt = majority_table(ciA, YA, b)
    seen = cnt[ciB] > 0
    pred = tab[ciB]
    out['bayes_bit'] = float(((pred == YB).float()[seen]).mean()) if bool(seen.any()) else None
    out['bayes_seen_frac'] = float(seen.float().mean())
    out['bayes_whole_code'] = whole_code_bayes(ciA, idx(YA), ciB, idx(YB), b)
    for d in (1, 2):
        if b <= 16 and not (d == 2 and b > 16):
            out[f'ptf{d}'] = float(np.mean(ptf_heldout(CA, YA, CB, YB, d)))
    if b <= 12:
        bitsA, bitsB = (CA < 0).long(), (CB < 0).long()
        for s in (1, 2, 3):
            out[f'junta{s}'] = float(np.mean(junta_heldout(bitsA, YA, bitsB, YB, s)))
    return out


if __name__ == '__main__':
    CDIR = os.environ.get('CHAIN_DIR', 'runs/S_chain')
    NK = os.environ.get('NETKIND', 'relu')
    OUTF = os.environ.get('POSTHOC_OUT', 'results/S2_posthoc.json')
    res = json.load(open(OUTF)) if os.path.exists(OUTF) else {}
    files = sorted(glob.glob(f'{CDIR}/C_*.pt'))
    for p in files:
        tag = os.path.basename(p)[:-3]
        parts = tag.split('_')
        n, L, seed, cls = int(parts[1][1:]), int(parts[2][1:]), int(parts[3][1:]), parts[4]
        if tag in res:
            continue
        layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
        net = sn.Net(seed, n, L, kind=NK)
        g = torch.Generator().manual_seed(123 + seed)
        Hp, Ap = net.sample(65536, set(layers), g)
        frames = [sn.frame(Hp[l]) for l in layers]
        fr_a = sn.frame(Ap)
        ch = Chain(n, layers, cls)
        sd = torch.load(p, map_location='cpu')
        sd = {k: v for k, v in sd.items() if not k.startswith('dec')}
        ch.load_state_dict(sd, strict=False)
        H, A = net.sample(131072, set(layers), g)
        codes = [codes_of(ch, i, H[l], A, frames, fr_a, cls) for i, l in enumerate(layers)]
        rng = np.random.default_rng(seed)
        ent = {}
        for mi, b in enumerate(BS):
            trs = []
            for i in range(len(layers) - 1):
                C = codes[i][mi][:, :b]
                Y = codes[i + 1][mi][:, :b]
                half = C.shape[0] // 2
                ci = idx(C)
                CA, CB, YA, YB = C[:half], C[half:], Y[:half], Y[half:]
                ciA, ciB = ci[:half], ci[half:]
                real = stats(ciA, CA, YA, ciB, CB, YB, b, rng)
                # matched null: relabel the reachable input codes by a random bijection (the joint law of (code, next
                # code) is kept up to the relabelling, so H(next | code) and whole-code Bayes accuracy are unchanged;
                # the geometry linking input bits to output bits is destroyed)
                u = torch.unique(ci)
                perm = u[torch.tensor(rng.permutation(len(u)))]
                remap = torch.full((2 ** b,), -1, dtype=torch.long)
                remap[u] = perm
                cin = remap[ci]
                Cn = 1.0 - 2.0 * ((cin[:, None] >> torch.arange(b)[None, :]) & 1).float()
                null = stats(cin[:half], Cn[:half], YA, cin[half:], Cn[half:], YB, b, rng)
                trs.append(dict(real=real, null=null))
            ent[str(b)] = trs
        res[tag] = ent
        print(tag, {b: [(round(t['real'].get('ptf1', 0), 3), round(t['real']['trivial'], 3), round(t['null'].get('ptf1', 0), 3),
                        round(t['real']['bayes_whole_code'], 3), round(t['null']['bayes_whole_code'], 3)) for t in v]
                    for b, v in ent.items()}, flush=True)
        os.makedirs('results', exist_ok=True)
        json.dump(res, open(OUTF, 'w'))
