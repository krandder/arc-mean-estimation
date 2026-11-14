"""Markdown tables for the report, generated from runs/ and results/ (no hand transcription). Writes results/tables.md."""
import json
import math
import os
import sys
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(ROOT, 'lib'))
import rnd  # noqa: E402

R = lambda p: os.path.join(ROOT, p)
out = []
S256 = list(range(200, 205))
LAD = {32: 4, 64: 8, 128: 16}
LS = list(range(300, 308))


def load(kind, n, L, s):
    p = R(f'runs/{kind}_n{n}_L{L}_s{s}.json')
    return json.load(open(p)) if os.path.exists(p) else None


def med(v):
    v = [x for x in v if x is not None and np.isfinite(x)]
    return float(np.median(v)) if v else float('nan')


def fmt(v, d=2):
    return '-' if v is None or not np.isfinite(v) else f'{v:.{d}f}'


# T-A: per-net spectrum and design gains at 256 x 32
out.append('### Table A. 256 x 32, per net: harmonic shares of the radius-exact variance and Haar-randomised design gains '
           'over plain MC (E1)\n')
out.append('| net | V | V_rb/V | odd | even | deg 1 | deg 2 | even >= 4 | even >= 6 | ONB | simplex | cross | Kerdock | '
           'T4 ceiling (vs MC) |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for s in S256:
    r = load('struct', 256, 32, s)
    if r is None:
        continue
    V, Vrb = r['V'], r['V_rb']; d = r['designs']
    rel = lambda k: d[k]['inv_gain_mc'] / (Vrb / V)
    le2 = 1 - rel('simplex'); E2 = 1 - rel('onb'); ev6 = rel('kerdock') / 2
    out.append(f"| {s} | {V:.1f} | {Vrb / V:.3f} | {r['V_odd'] / Vrb:.3f} | {r['V_even'] / Vrb:.3f} | {le2 - E2:.2f} | "
               f"{E2:.2f} | {rel('cross') / 2:.3f} | {ev6:.3f} | {1 / d['onb']['inv_gain_mc']:.2f} | "
               f"{1 / d['simplex']['inv_gain_mc']:.2f} | {1 / d['cross']['inv_gain_mc']:.2f} | "
               f"{1 / d['kerdock']['inv_gain_mc']:.2f} | {2 / ev6 / (Vrb / V):.1f} |")
out.append('')

# T-B: ladder (medians [min, max])
lt = json.load(open(R('results/ladder_table.json')))
rows = [('rho_rb', 'V_rb / V'), ('odd', 'odd share'), ('E1', 'degree-1 share'), ('E2', 'degree-2 share'),
        ('ev4', 'even >= 4 share'), ('g_onb', 'gain: orthonormal basis'), ('g_simplex', 'gain: simplex (2-design)'),
        ('g_cross', 'gain: cross-polytope (antipodal 3-design)'), ('g_kerdock', 'gain: Kerdock (antipodal 5-design)'),
        ('rq_std_14', 'gain: scrambled Sobol, 2^14'), ('rq_polar_14', 'gain: scrambled Sobol, polar frame, 2^14'),
        ('rq_svd_14', 'gain: scrambled Sobol, SVD frame, 2^14'), ('anti_std_14', 'gain: antipodal Sobol, 2^14'),
        ('ml', 'multilevel prefix control, gain vs RB-MC')]
out.append('### Table B. Along L = n/8: medians over nets [min, max] (8 nets at n = 32, 64, 128; 5 at 256). Gains are '
           'over plain MC at equal points unless stated (E1)\n')
out.append('| quantity | n = 32, L = 4 | n = 64, L = 8 | n = 128, L = 16 | n = 256, L = 32 |\n|---|---|---|---|---|')
for k, lab in rows:
    cells = []
    for n in ('32', '64', '128', '256'):
        v = lt.get(n, {}).get(k)
        cells.append('-' if v is None else f'{v[0]:.2f} [{v[1]:.2f}, {v[2]:.2f}]')
    out.append(f'| {lab} | ' + ' | '.join(cells) + ' |')
out.append('')

# T-C: head-to-head at ARC's budget
out.append('### Table C. ARC\'s budget, 256 x 32 (E2): N = 2^16 points (Kerdock 66,048), radius exact, nMSE against the '
           'truth; gain = 1 / (nMSE x N), plain MC = 1\n')
out.append('| sampler | random bits | net 200 | 201 | 202 | 203 | 204 | median gain |\n|---|---|---|---|---|---|---|---|')
names = [('mc_pairwise', 'pairwise-independent MC'), ('rqmc_std', 'scrambled Sobol (black-box)'),
         ('rqmc_polar', 'scrambled Sobol, polar frame of W_1 (white-box)'), ('kerdock', 'Kerdock 5-design, Haar rotation'),
         ('det_std', 'centred Sobol, fixed'), ('det_polar', 'centred Sobol, polar frame, fixed')]
co = {s: load('combo', 256, 32, s) for s in S256}
for k, lab in names:
    g = []; bits = None
    for s in S256:
        if co[s] is None or k not in co[s]['methods']:
            g.append(None); continue
        x = co[s]['methods'][k]; bits = x['random_bits']
        g.append(x['gain_mc'])
    out.append(f'| {lab} | {bits if bits is not None else "-"} | ' + ' | '.join(fmt(v) for v in g) + f' | {fmt(med(g))} |')
out.append('')

# T-D: noise sensitivity / perimeter
out.append('### Table D. Gate perimeter and noise sensitivity (E3): medians over nets\n')
out.append('| n x L | layer-1 GSA / (n/sqrt(2 pi)) | total / (nL/sqrt(2 pi)) [min, max] | P(some gate changes), delta = 1e-6 | '
           'output NS slope (mean Hermite degree) | n / V |\n|---|---|---|---|---|---|')
ds = ('1e-06', '1e-05', '0.0001')
for n, L in list(LAD.items()) + [(256, 32)]:
    seeds = S256 if n == 256 else LS
    g1, tot, pa, sl, nv = [], [], [], [], []
    for s in seeds:
        r = load('noise', n, L, s)
        if r is None:
            continue
        fl = sum(np.array(r['gauss'][d]['flips']) for d in ds) / sum(2 * math.sqrt(float(d) / math.pi) for d in ds)
        c = n / math.sqrt(2 * math.pi)
        g1.append(fl[0] / c); tot.append(fl.sum() / (c * L)); pa.append(r['gauss']['1e-06']['p_any'][-1])
        sl.append(r['gauss']['1e-05']['ns'][-1] / 1e-5); nv.append(n / rnd.load_truth(s, n, L)['V'])
    out.append(f'| {n} x {L} | {med(g1):.3f} | {med(tot):.3f} [{min(tot):.2f}, {max(tot):.2f}] | {med(pa):.3f} | '
               f'{med(sl):.1f} | {med(nv):.1f} |')
out.append('')

# T-E: deterministic designs, nMSE x N medians at selected N
out.append('### Table E. Zero-random-bit point sets against the truth (E4): median nMSE x N over nets (plain MC = 1); '
           'k-wise rows give N = q^k\n')
out.append('| n x L | centred Sobol 2^10 / 2^14 / 2^16 | Sobol, polar frame 2^10 / 2^14 / 2^16 | Korobov lattice 2^14 | '
           'k-wise k = 2 | k = 3 | k = 4 | Kerdock fixed / polar-aligned |\n|---|---|---|---|---|---|---|---|')
for n, L in [(32, 4), (64, 8), (128, 16), (256, 32)]:
    seeds = S256 if n == 256 else LS
    acc = {}
    for s in seeds:
        r = load('det', n, L, s)
        if r is None:
            continue
        fl = r['truth_floor']
        for name, ser in r['series'].items():
            for x in ser:
                acc.setdefault((name, x['N']), []).append(x['nmse_x_N'] if x['nmse'] >= 3 * fl else float('nan'))
    if not acc:
        continue
    def g(name, N):
        v = acc.get((name, N), [])
        k = sum(1 for x in v if np.isfinite(x))
        return '-' if not v else f'{fmt(med(v))} ({k}/{len(v)})'
    q = n + 1
    while any(q % p == 0 for p in range(2, int(q ** 0.5) + 1)):
        q += 1
    kw = [g(f'kwise{k}_rb', q ** k) for k in (2, 3, 4)]
    out.append(f"| {n} x {L} | {g('sobol_rb', 1024)} / {g('sobol_rb', 16384)} / {g('sobol_rb', 65536)} | "
               f"{g('sobol_rb_polar', 1024)} / {g('sobol_rb_polar', 16384)} / {g('sobol_rb_polar', 65536)} | "
               f"{g('lattice_rb', 16384)} | {kw[0]} | {kw[1]} | {kw[2]} | "
               f"{g('kerdock_fixed_rb', 66048)} / {g('kerdock_polar_rb', 66048)} |")
out.append('\n(Each cell: median over the nets resolved above 3x the truth floor, with (resolved / run) nets; - = not run. k-wise cells with few resolved nets are not evidence about k.)\n')
open(R('results/tables.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
