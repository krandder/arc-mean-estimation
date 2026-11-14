"""Score PREREG Amendment 2 (G1) from runs/gain_*.json."""
import os
import json
import glob
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), '..')


def main():
    by_n = {}
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'runs', 'gain_n*_L*_s*.json'))):
        r = json.load(open(f))
        for l, d in r['layers'].items():
            for b in d['bins']:
                rows.append((r['n'], r['L'], r['seed'], int(l), b['Lp_phi'], b['ratio']))
                if b['Lp_phi'] >= 3 and b['ratio'] is not None:
                    by_n.setdefault(r['n'], []).append(b['ratio'])
    med = {n: float(np.median(v)) for n, v in sorted(by_n.items())}
    ok_each = {n: bool(1 / 3 <= m <= 3) for n, m in med.items()}
    change = None
    if 64 in med and 256 in med:
        change = max(med[256] / med[64], med[64] / med[256])
    out = {'median_ratio_by_width': med, 'cells_by_width': {n: len(v) for n, v in by_n.items()},
           'in_band': ok_each, 'change_64_to_256': change,
           'pass': all(ok_each.values()) and change is not None and change < 2}
    json.dump(out, open(os.path.join(ROOT, 'results', 'gain_scores.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))
    for row in rows:
        print('n=%d L=%d s=%d l=%d Lphi=%.2f ratio=%s' % (row[0], row[1], row[2], row[3], row[4],
                                                          'nan' if row[5] is None else '%.3f' % row[5]))


if __name__ == '__main__':
    main()
