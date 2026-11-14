"""Score PREREG Amendment 1 (A1-A3) from runs/ml_*.json. Medians over nets per configuration."""
import os
import json
import glob
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), '..')


def main():
    nets = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, 'runs', 'ml_n*_L*_s*.json')))]
    nets = [r for r in nets if not r.get('dead')]
    cfg = {}
    for r in nets:
        cfg.setdefault((r['n'], r['L']), []).append(r)
    out = {'medians': {}, 'A1': {}}
    for c, rs in sorted(cfg.items()):
        g = float(np.median([1 / r['variants']['rand']['best'] for r in rs]))
        row = {'nets': len(rs), 'rand_gain_best': g,
               'rand_gain_full': float(np.median([1 / r['variants']['rand']['full_dyadic'] for r in rs]))}
        for M in [4, 16, 64, 256]:
            row[f'traj{M}_gain_best'] = float(np.median([1 / r['variants'][f'traj{M}']['best'] for r in rs]))
            row[f'traj{M}_gain_full'] = float(np.median([1 / r['variants'][f'traj{M}']['full_dyadic'] for r in rs]))
        out['medians'][f'{c[0]}x{c[1]}'] = row
        if c[1] == c[0]:
            out['A1'][f'{c[0]}x{c[1]}'] = bool(1.1 <= g <= 3)
        elif c[1] == 4 * c[0]:
            out['A1'][f'{c[0]}x{c[1]}'] = bool(1.5 <= g <= 8)
        elif c == (256, 32):
            out['A1'][f'{c[0]}x{c[1]}'] = bool(0.8 <= g <= 1.3)
    m = out['medians']
    out['A2'] = None
    if '32x32' in m and '256x256' in m:
        f = m['256x256']['rand_gain_best'] / m['32x32']['rand_gain_best']
        out['A2'] = {'factor': f, 'pass': bool(1.0 <= f <= 2.0)}
    a, b = [], []
    for r in nets:
        rr = r['variants']['rand']
        a.append(all(r['variants'][f'traj{M}']['best'] / rr['best'] >= 0.8 for M in [4, 16, 64, 256]))
        b.append(all(r['variants'][f'traj{M}']['full_dyadic'] > rr['full_dyadic'] for M in [4, 16, 64, 256]))
    out['A3'] = {'best_not_beaten': float(np.mean(a)), 'full_worse': float(np.mean(b)), 'n': len(a),
                 'pass': bool(float(np.mean(a)) >= 0.75 and float(np.mean(b)) >= 0.75)}
    os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, 'results', 'ml_scores.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
