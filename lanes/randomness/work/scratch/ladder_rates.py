"""Descriptive: RQMC exponents along the ladder from the E1 sizes 2^10, 2^12, 2^14 (16 replicates each), per width,
same weighted fit as rate_fit.py; and deterministic centred-Sobol exponents from E4 (2^8..2^16)."""
import json, math, os, numpy as np
rng = np.random.default_rng(7)
def wls(x, y, w):
    x, y, w = map(np.asarray, (x, y, w)); W = w.sum(); xm = (w * x).sum() / W; ym = (w * y).sum() / W
    return float(((w * (x - xm) * (y - ym)).sum()) / ((w * (x - xm) ** 2).sum()))
def boot(v):
    v = np.asarray(v); m = [np.median(rng.choice(v, len(v))) for _ in range(2000)]
    return float(np.median(v)), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
out = {}
for n, L, seeds in ((32, 4, range(300, 308)), (64, 8, range(300, 308)), (128, 16, range(300, 308)), (256, 32, range(200, 205))):
    for fr in ('std', 'polar', 'svd'):
        ps = []
        for s in seeds:
            r = json.load(open(f'runs/struct_n{n}_L{L}_s{s}.json'))
            pts = [(r['rqmc'][f'rqmc_rb_{fr}_m{m}']['m'], r['rqmc'][f'rqmc_rb_{fr}_m{m}']['inv_gain_mc'], 16) for m in (10, 12, 14)]
            ps.append(-wls([math.log(p[0]) for p in pts], [math.log(p[1] / p[0]) for p in pts], [7.5] * 3))
        out[f'{n}_{fr}'] = boot(ps)
    ps = []
    for s in seeds:
        p = f'runs/det_n{n}_L{L}_s{s}.json'
        if os.path.exists(p):
            v = json.load(open(p)).get('rate_p', {}).get('sobol_rb')
            if v: ps.append(v)
    if ps: out[f'{n}_detsobol'] = boot(ps)
for k, v in out.items():
    print(f'{k:16s} median p {v[0]:.3f}  95% CI [{v[1]:.3f}, {v[2]:.3f}]')
json.dump(out, open('results/ladder_rates.json', 'w'), indent=1)
