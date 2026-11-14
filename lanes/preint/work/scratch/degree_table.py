"""Per-net angular degree energies (runs/deg_*.json, degrees.py v2) and the per-net heuristic barrier of FORMAL E3:
for a rotation-randomised rule with N points, N x nMSE >~ (1 - radial share) x (even >= 4 share) x (1 - N / N(d, 2))
(test kernel P_2^2 treated as sitting on degree 4; leakage 1.5-11% at d = 256-32), compared with RQMC's measured
N x nMSE at N = 2^12..2^14 on the same net (runs/s3_arc_*). Writes results/degree_table.md."""
import glob
import json
import math
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def N2(d):
    return (d + 2) * (d - 1) // 2


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'runs', 'deg_n*_L*_s*.json')),
                    key=lambda p: (json.load(open(p))['n'], json.load(open(p))['seed'])):
        d = json.load(open(f))
        sh = d['shares']
        n, L, s = d['n'], d['L'], d['seed']
        c_bar = (1 - d['radial_share']) * sh['even_ge4']
        rq = os.path.join(ROOT, 'runs', 's3_arc_n%d_L%d_s%d.json' % (n, L, s))
        meas = ''
        if os.path.exists(rq):
            r = json.load(open(rq))['methods'].get('RQMC', [])
            meas = ', '.join('%.2f' % (x['N'] * x['nmse_rep']) for x in r[-3:])
        rows.append('| %dx%d s%d | %.3f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f (N << %d) | %s |' % (
            n, L, s, d['radial_share'], sh['deg1'], sh['odd_ge3'], sh['deg2'], sh['even_ge4'], sh['odd'],
            c_bar, N2(n), meas or '-'))
    head = ['| net | radial share of plain variance | degree 1 | odd >= 3 | degree 2 | even >= 4 | all odd | barrier c ~ (1 - radial) x even>=4, for N << N(d,2) | RQMC N x nMSE at N = 2^12, 2^13, 2^14 |',
            '|' + '---|' * 9]
    out = '\n'.join(head + rows) + '\n'
    open(os.path.join(ROOT, 'results', 'degree_table.md'), 'w').write(out)
    print(out)


if __name__ == '__main__':
    main()
