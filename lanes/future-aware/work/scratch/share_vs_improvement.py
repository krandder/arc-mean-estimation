"""POST HOC (not registered): does the captured share s of the future's whitened NONLINEAR relevance (Jacobian energy,
E[J^T J] - E[J]^T E[J] whitened by the cloud covariance) predict the single-cut improvement b2(gauss)/b2(cond_<kind>k)
of the "k features exact" projection, across kinds (futnl, pca, rand), k, cuts and widths? Model (FORMAL H-overlap,
astra r1 Q3 in a linear model): improvement ~ (1 - s)^-1. Writes results/share_vs_improvement.json and prints a fit.
Cells with b2(gauss) below 10x the variant's resolution are dropped; b2 floored at 2e-6 (the 2^18-push noise scale)."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, '..', 'runs'); RES = os.path.join(HERE, '..', 'results')
CONF = [(64, 8, range(300, 308)), (128, 16, range(300, 308)), (256, 32, range(200, 205))]
out = {}
allpts = []
for n, L, seeds in CONF:
    pts = []
    for s in seeds:
        p = os.path.join(RUNS, f'cut_n{n}_L{L}_s{s}.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for c, cr in d['cuts'].items():
            g = cr['variants']['gauss']['b2']
            floor = max(2e-6, 2 * abs(cr['variants']['true']['b2']))
            if g < 10 * floor:
                continue
            for key, sv in cr['shares'].items():
                v = cr['variants'].get(f'cond_{key}')
                if v is None:
                    continue
                s_nl = sv['rel_nl']
                imp = g / max(v['b2'], floor)
                kind = ''.join(ch for ch in key if not ch.isdigit())
                pts.append(dict(n=n, seed=s, l=int(c), kind=kind, k=int(''.join(ch for ch in key if ch.isdigit())),
                                share=s_nl, improvement=imp, capped=bool(v['b2'] < floor), raw_b2=v['b2'], g=g))
    if not pts:
        continue
    x = np.array([-np.log(max(1e-6, 1 - q['share'])) for q in pts]); y = np.log([q['improvement'] for q in pts])
    slope, icpt = np.polyfit(x, y, 1)
    # unfloored convention (astra r3): drop cells whose variant b2 is not positive, no floor
    pu = [q for q in pts if q['raw_b2'] > 0]
    xu = np.array([-np.log(max(1e-6, 1 - q['share'])) for q in pu]); yu = np.log([q['g'] / q['raw_b2'] for q in pu])
    su, iu = np.polyfit(xu, yu, 1)
    out[n] = dict(n_points=len(pts), corr=float(np.corrcoef(x, y)[0, 1]), slope=float(slope), intercept=float(icpt),
                  unfloored=dict(n_points=len(pu), corr=float(np.corrcoef(xu, yu)[0, 1]), slope=float(su), intercept=float(iu),
                                 slope_origin=float((xu @ yu) / (xu @ xu))),
                  points=pts)
    print(f'   unfloored: {len(pu)} cells, corr {np.corrcoef(xu, yu)[0, 1]:.3f}, slope {su:.2f} (intercept {iu:.2f}), '
          f'through origin {(xu @ yu) / (xu @ xu):.2f}')
    allpts += pts
    print(f'n={n}: {len(pts)} cells, corr(log improvement, -log(1 - share)) = {np.corrcoef(x, y)[0, 1]:.3f}, '
          f'log-log slope {slope:.2f}, intercept {icpt:.2f}')
    for kind in ('futnl', 'fut', 'pca', 'rand'):
        for k in sorted({q['k'] for q in pts if q['kind'] == kind}):
            sel = [q for q in pts if q['kind'] == kind and q['k'] == k]
            if sel:
                print(f'   {kind:5s} k={k:3d}: median share {np.median([q["share"] for q in sel]):.3f}, median improvement '
                      f'{np.median([q["improvement"] for q in sel]):.1f} ({len(sel)} cells)')
json.dump(out, open(os.path.join(RES, 'share_vs_improvement.json'), 'w'), indent=1, default=float)
