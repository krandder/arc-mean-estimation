"""Where the 'scrambling' is: the downstream classes at layer k are few, but each class's preimage in input space is a
union of many activation regions of layers 1..k. For cuts k, counts (from 2^m inputs) the downstream classes
(pattern of layers k+1..256, live states) covering 99% of the output mass and the distinct upstream regions (pattern of
layers 1..k) inside each of them. Usage: preimage.py SEED LOG2N OUT.json"""
import json
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import ndx  # noqa: E402

CUTS = [2, 4, 8, 12, 16, 20, 24]


def main():
    seed, m, outp = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    N = 1 << m
    Ws = ndx.make_weights(seed)
    rng = np.random.default_rng([2718, seed])
    up = {k: [] for k in CUTS}
    dn = {k: [] for k in CUTS}
    na = []
    for _ in range(N // (1 << 17)):
        X = rng.standard_normal((1 << 17, 8))
        a, pat = ndx.fwd_patterns(Ws, X)
        na.append(np.linalg.norm(a, axis=1))
        for k in CUTS:
            up[k].append(ndx.hash2(pat[:, :k]))
            dn[k].append(ndx.hash2(pat[:, k:]))
    na = np.concatenate(na)
    out = dict(seed=seed, N=N, cuts={})
    for k in CUTS:
        U = ndx.void_keys(np.concatenate(up[k]))
        Dk = ndx.void_keys(np.concatenate(dn[k]))
        live = na > 0
        _, dinv = np.unique(Dk[live], return_inverse=True)
        mass = np.bincount(dinv, weights=na[live])
        order = np.argsort(-mass)
        cum = np.cumsum(mass[order]) / mass.sum()
        n99 = int(np.searchsorted(cum, 0.99) + 1)
        _, uinv = np.unique(U[live], return_inverse=True)
        pairs = np.unique(np.stack([dinv, uinv], 1), axis=0)
        per_class = np.bincount(pairs[:, 0], minlength=len(mass))
        top = order[:n99]
        out['cuts'][str(k)] = dict(classes_99=n99, classes_live=int(len(mass)),
                                   regions_in_top_classes=[int(per_class[c]) for c in top[:20]],
                                   mass_top_classes=[float(mass[c] / mass.sum()) for c in top[:20]],
                                   upstream_regions_seen=int(uinv.max() + 1))
        print(seed, 'cut', k, 'classes for 99%%: %d of %d live; upstream regions seen %d; regions inside the top classes:'
              % (n99, len(mass), uinv.max() + 1), [int(per_class[c]) for c in top[:8]], flush=True)
    json.dump(out, open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
