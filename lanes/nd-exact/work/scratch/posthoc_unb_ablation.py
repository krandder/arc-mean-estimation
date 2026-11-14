"""Post hoc ablation for the unbiased version (review finding 10): do the cells help? On the same scrambled-Sobol
points, compare UNB = D + mean(f - q) with NOCELL = mean(f) (no cells, same 32-layer net and certified tail with
full-forward fallback). Paired over R replicates. Reports nMSE (with standard errors) and costs: UNB pays D's cost
plus the lookup; NOCELL pays only the points. Usage: posthoc_unb_ablation.py SEED R"""
import json
import math
import sys

import numpy as np
from scipy.stats import norm, qmc

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/scratch')
import cs2tree  # noqa: E402
import ndx  # noqa: E402
from run_unbiased import f_exact, PPF_MV  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'


def main():
    seed, R = int(sys.argv[1]), int(sys.argv[2])
    Ws = ndx.make_weights(seed)
    tr = json.load(open(BASE + f'runs/truth_s{seed}.json'))
    mu, trV = np.array(tr['trunc_mean']), tr['trV']
    est = cs2tree.CS2(Ws, c0=32, Q=32, rule='surplus', floor=0.01)
    est.setup()
    while est.cost_mv() < 2.0 ** 20 and est.refine_one():
        pass
    D = est.estimate().copy()
    costD = est.cost_mv()
    rng = np.random.default_rng([6174, seed])
    out = dict(seed=seed, costD=costD, rows=[])
    for lm in (12, 14, 16):
        M = 1 << lm
        eu, en, cu, cn = [], [], [], []
        for _ in range(R):
            X = norm.ppf(np.clip(qmc.Sobol(d=8, scramble=True, seed=rng).random(M), 1e-300, 1 - 1e-16))
            F, extra = f_exact(est, X)
            Qv, op, lf = cs2tree.lookup(est, X)
            res = F - Qv
            res[~op] = 0.0
            eu.append(ndx.nmse(D + res.mean(0), mu, trV))
            en.append(ndx.nmse(F.mean(0), mu, trV))
            base = M * (PPF_MV + 1.0 + 2.0 + est.c0) + extra
            cu.append(costD + base + lf / 128.0)
            cn.append(base + float(est.K['flops']) / 128.0 + (len(Ws) - est.c0) * 8.0 * 0)
        eu, en = np.array(eu), np.array(en)
        dd = eu - en
        tcrit = 2.0395  # t quantile 0.975, 31 degrees of freedom (R = 32)
        row = dict(M=M, unb_reps=eu.tolist(), nocell_reps=en.tolist(),
                   paired_diff=float(dd.mean()), paired_ci=[float(dd.mean() - tcrit * dd.std(ddof=1) / math.sqrt(R)),
                                                            float(dd.mean() + tcrit * dd.std(ddof=1) / math.sqrt(R))],
                   unb=float(eu.mean()), unb_se=float(eu.std(ddof=1) / math.sqrt(R)), nocell=float(en.mean()),
                   nocell_se=float(en.std(ddof=1) / math.sqrt(R)), cost_unb=float(np.mean(cu)),
                   cost_nocell=float(np.mean(cn)), paired_logratio_mean=float(np.mean(np.log(en / eu))))
        out['rows'].append(row)
        print(seed, 'M 2^%d: UNB %.2e +- %.1e (cost %.2e) | no cells %.2e +- %.1e (cost %.2e) | mean log(no-cell/UNB) %.2f' % (
            lm, row['unb'], row['unb_se'], row['cost_unb'], row['nocell'], row['nocell_se'], row['cost_nocell'],
            row['paired_logratio_mean']), flush=True)
    json.dump(out, open(BASE + f'runs/posthoc_unb_ablation_s{seed}.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
