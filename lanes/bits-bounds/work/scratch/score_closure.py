"""Score PREREG Amendment 3 (B1, B2) from runs/closure_*.json."""
import os
import json
import glob
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), '..')


def main():
    rows = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, 'runs', 'closure_n*_L*_s*.json')))]
    rows = [r for r in rows if r.get('nMSE_closure') is not None and r['V'] > 0]
    out = {'by_config': {}, 'B1': {}, 'B2': {}}
    for alpha in [0.5, 1.0]:
        ns, meds, gains = [], [], []
        for n in [16, 32, 64, 128]:
            L = int(round(alpha * n))
            rs = [r for r in rows if r['n'] == n and r['L'] == L]
            if not rs:
                continue
            m = float(np.median([r['nMSE_closure'] for r in rs]))
            g = float(np.median([(1.0 / r['cost_passes_matmul']) / max(r['nMSE_closure'], 1e-300) for r in rs]))
            out['by_config'][f'{n}x{L}'] = {'nets': len(rs), 'median_nMSE': m, 'median_gain_matmul_cost': g,
                                            'median_gain_impl_cost': float(np.median(
                                                [(1.0 / r['cost_passes_impl']) / max(r['nMSE_closure'], 1e-300)
                                                 for r in rs]))}
            ns.append(n)
            meds.append(m)
            gains.append(g)
        if len(ns) >= 2 and all(m > 0 for m in meds):
            slope = float(np.polyfit(np.log(ns), np.log(meds), 1)[0])
            out['B1'][str(alpha)] = {'slope': slope, 'pass': bool(-1.0 <= slope <= 0.0)}
        if gains:
            ok_max = all(g <= 10 for g in gains)
            growth = gains[-1] / gains[0] if gains[0] > 0 else float('inf')
            out['B2'][str(alpha)] = {'gains': gains, 'growth_16_to_128': growth,
                                     'pass': bool(ok_max and growth <= 2.0)}
    os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, 'results', 'closure_scores.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
