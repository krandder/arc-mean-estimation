"""Region codes with free exact integration (an optimistic bound for any region-by-region exact method).

Region at depth d = activation pattern of layers 1..d. A code of R regions integrates those R regions exactly and drops
the rest. Two versions, from two independent samples A and B of 2^m Gaussian inputs each:
  IN-SAMPLE: regions ranked by their contribution in A, residual also from A. Optimistic (selection bias makes the
             covered part look larger), and it collapses near R = (regions seen in A): reported only as a lower estimate.
  HELD-OUT:  regions ranked by A, residual = the contribution of everything outside the top R, estimated on B
             (unbiased for that region set; includes regions A never saw).
Cost charged: 9 mv per region (8 for its linear map, 1 for its moments), a lower bound; discovering the regions
(sample A, 2^m x 32 mv) is not charged.
Usage: region_code.py SEED LOG2M OUT.json
"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import ndx  # noqa: E402

DEPTHS = [4, 8, 16, 32]


def sample(Ws, rng, N, chunk=1 << 17):
    keys = {d: [] for d in DEPTHS}
    A = []
    for _ in range(N // chunk):
        X = rng.standard_normal((chunk, 8))
        h32, pat = ndx.fwd_patterns(Ws, X, 0, 32)
        A.append(ndx.fwd(Ws, h32, 32, 256))
        for d in DEPTHS:
            keys[d].append(ndx.hash2(pat[:, :d]))
    return {d: ndx.void_keys(np.concatenate(v)) for d, v in keys.items()}, np.concatenate(A)


def main():
    seed, m, outp = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    N = 1 << m
    Ws = ndx.make_weights(seed)
    t0 = time.time()
    kA, aA = sample(Ws, np.random.default_rng([5151, seed]), N)
    kB, aB = sample(Ws, np.random.default_rng([5152, seed]), N)
    a_all = np.concatenate([aA, aB])
    mu = a_all.mean(0)
    trV = float(a_all.var(0, ddof=1).sum())
    out = dict(seed=seed, N=N, trV=trV, curves={})
    for d in DEPTHS:
        uq, inv, cnt = np.unique(kA[d], return_inverse=True, return_counts=True)
        G = len(uq)
        S = np.stack([np.bincount(inv, weights=aA[:, j], minlength=G) for j in range(8)], 1)
        order = np.argsort(-np.linalg.norm(S, axis=1))
        rank = np.empty(G, dtype=np.int64)
        rank[order] = np.arange(G)
        # in-sample residual
        Ssorted = S[order]
        tailA = np.cumsum(Ssorted[::-1], axis=0)[::-1]           # tailA[R] = sum over ranks >= R
        S2 = np.bincount(inv, weights=(aA * aA).sum(1), minlength=G)[order]
        tail2A = np.cumsum(S2[::-1])[::-1]
        # held-out: rank of each B sample's region (G if unseen in A)
        pos = np.searchsorted(uq, kB[d])
        pos = np.minimum(pos, G - 1)
        found = uq[pos] == kB[d]
        rB = np.where(found, rank[pos], G)
        SB = np.stack([np.bincount(rB, weights=aB[:, j], minlength=G + 1) for j in range(8)], 1)
        tailB = np.cumsum(SB[::-1], axis=0)[::-1]
        S2B = np.bincount(rB, weights=(aB * aB).sum(1), minlength=G + 1)
        tail2B = np.cumsum(S2B[::-1])[::-1]
        Rs = sorted(set([1 << j for j in range(0, 24) if (1 << j) <= G] + [G]))
        cur = []
        for R in Rs:
            ins = tailA[R] / N if R < G else np.zeros(8)
            ho = tailB[R] / N
            cur.append(dict(R=int(R), cost_mv=9.0 * R,
                            nmse_in=float(np.sum(ins ** 2) / trV),
                            noise_in=float((tail2A[R] if R < G else 0.0) / N / N / trV),
                            nmse_ho=float(np.sum(ho ** 2) / trV), noise_ho=float(tail2B[R] / N / N / trV),
                            prob_covered_ho=float(1.0 - (rB >= R).mean())))
        out['curves'][str(d)] = dict(regions_seen_A=int(G), unseen_prob_B=float((~found).mean()), curve=cur)
        print(seed, 'd', d, 'G', G, 'B unseen %.4f' % (~found).mean(),
              ' '.join('R=%d:ho %.2e in %.2e' % (c['R'], c['nmse_ho'], c['nmse_in'])
                       for c in cur if c['R'] in (16, 1024, 16384, 65536, 131072, 262144) or c['R'] == G), flush=True)
    out['seconds'] = time.time() - t0
    json.dump(out, open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
