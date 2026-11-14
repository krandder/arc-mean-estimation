"""Collate the hashed scorers' outputs into results/scorecard.md (descriptive; changes no scoring rule).
Runs score_prereg.py, score_attr.py, score_amend2.py, score_amend3.py, score_amend4.py, each writing
results/score_*.json, then prints one row per registered prediction with the measured value and whether it holds.
usage: scorecard.py [--no-run]"""
import json, os, subprocess, sys

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RES = os.path.join(HERE, 'results')
PY = sys.executable
os.makedirs(RES, exist_ok=True)
JOBS = [('score_prereg.py', [], 'score_prereg.json'),
        ('score_attr.py', ['200,201,202,203,204'], 'score_attr.json'),
        ('score_amend2.py', [], 'score_amend2.json'),
        ('score_amend3.py', [], 'score_amend3.json'),
        ('score_amend4.py', [], 'score_amend4.json'),
        ('score_amend5.py', [], 'score_amend5.json'),
        ('score_amend6.py', [], 'score_amend6.json')]
if '--no-run' not in sys.argv:
    for script, args, out in JOBS:
        r = subprocess.run([PY, os.path.join(HERE, 'scratch', script)] + args + [os.path.join(RES, out)],
                           capture_output=True, text=True, cwd=HERE)
        if r.returncode != 0:
            print(f'{script} failed:\n{r.stderr[-2000:]}')
J = {}
for _, _, out in JOBS:
    p = os.path.join(RES, out)
    J[out] = json.load(open(p)) if os.path.exists(p) else {}
P, A, R2, R3, R4, R5, R6 = (J['score_prereg.json'], J['score_attr.json'].get('scores', {}),
                            J['score_amend2.json'].get('scores', {}), J['score_amend3.json'].get('scores', {}),
                            J['score_amend4.json'].get('scores', {}), J['score_amend5.json'].get('scores', {}),
                            J['score_amend6.json'].get('scores', {}))


_r8 = A.get('P8_ratios_radgauss_over_gauss', {})
P8 = dict(hit=bool(sum(_r8.get(str(l), _r8.get(l, 0.0)) >= 0.5 for l in (8, 16, 24)) >= 2)) if _r8 else {}


def f(x, fmt='{:.3g}'):
    if isinstance(x, dict):
        return '; '.join(f'{k}: {f(v, fmt)}' for k, v in x.items())
    if isinstance(x, list):
        return '[' + ', '.join(f(v, fmt) for v in x) + ']'
    if isinstance(x, float):
        return fmt.format(x)
    return str(x)


def hit(d):
    if not d or 'hit' not in d:
        return 'not scored'
    return 'HOLDS' if d['hit'] else 'FAILS'


# Explicit states added 09:58Z after the GPT-6 review (finding 10): rows whose registered sample is incomplete or whose
# run was stopped are labelled, not given a mechanical HOLDS/FAILS. Validity gates of Amendment 6 are enforced.
def n_nets(js, n='256', key='radgauss'):
    try:
        return len(js['per_width'][n][key])
    except (KeyError, TypeError):
        return 0


A6 = J['score_amend6.json']
k6 = n_nets(A6)
valid6 = bool(R6.get('P24', {}).get('hit'))
widths6 = sum(1 for w in ('64', '128', '256') if n_nets(A6, w) > 0)
nrank = len(A.get('P9b', {}).get('pr_l1', []))
STATE = {'P19': 'PARTIAL: 1 of 5 nets (run stopped); the same Gaussian path in Amendment 6 is within 1.5x on 5 of 5',
         'P20': 'UNDETERMINED (run stopped, noise-dominated)', 'P21': 'UNDETERMINED (run stopped, noise-dominated)',
         'P22': 'UNDETERMINED (run stopped)', 'P23': 'UNDETERMINED (run stopped)'}
for k in ('P9a', 'P9b', 'P9c'):
    if nrank < 5:
        STATE[k] = f'PARTIAL ({nrank} of 5 nets): ' + hit(A.get(k))
for k in ('P25', 'P26', 'P27'):
    if not valid6:
        STATE[k] = 'UNDETERMINED (validity gate P24 failed)'
    elif k6 < 5:
        STATE[k] = f'PENDING ({k6} of 5 nets)'
if k6 < 5:
    STATE['P24'] = f'PENDING ({k6} of 5 nets)'
if widths6 < 3:
    STATE['P28'] = f'PENDING ({widths6} of 3 widths)'


rows = [
    ('P1a', 'G_3/G_2 <= 2/L at n = 32, 64, 128, 256', P.get('P1a', {}).get('ratios'), P.get('P1a')),
    ('P1b', 'G_4/G_3 <= 2/L at n = 64, 128', P.get('P1b', {}).get('ratios'), P.get('P1b')),
    ('P2', 'G_3 < 1 (n = 128, 256), G_4 < 1 (128); best order >= 3 G_RQMC < 0.5 (n >= 64)',
     {k: P.get('P2', {}).get(k) for k in ('G3_128', 'G3_256', 'G4_128', 'best_order_ge3_G_RQMC')}, P.get('P2')),
    ('P3', 'RQMC reaches the best K = 2 error at <= 4x its cost, >= 4 of 5 nets (per-net G_RQMC)',
     P.get('P3', {}).get('per_net'), P.get('P3')),
    ('P4', 'at 6.5e4 passes RQMC >= 10x below the best affordable ARC variant, 5 of 5 nets',
     P.get('P4', {}).get('ratio_best_affordable_over_rqmc'), P.get('P4')),
    ('P5a', 'G_3 strictly decreases over n = 32..256', P.get('P5a', {}).get('G3'), P.get('P5a')),
    ('P5b', 'G_2(256) < G_2(32)', {k: P.get('P5b', {}).get(k) for k in ('G2_32', 'G2_256')}, P.get('P5b')),
    ('P6a k2', 'b_8^2 >= 0.3 total (ARC k2), >= 4 of 5', A.get('P6a_arc_k2', {}).get('pass_count'),
     A.get('P6a_arc_k2')),
    ('P6a exact', 'b_8^2 >= 0.3 total (exact Gaussian), >= 4 of 5', A.get('P6a_exact_gauss', {}).get('pass_count'),
     A.get('P6a_exact_gauss')),
    ('P6b k2', 'total >= 0.4 (a^2 + b^2) at l = 4, 8, 16 (k2), >= 4 of 5', A.get('P6b_arc_k2', {}).get('pass_count'),
     A.get('P6b_arc_k2')),
    ('P6b exact', 'same for the exact Gaussian recursion', A.get('P6b_exact_gauss', {}).get('pass_count'),
     A.get('P6b_exact_gauss')),
    ('P6c', 'abs(a_31^2) < 1e-5 (code check of CHECK-1), k2', A.get('CHECK_a31_arc_k2', {}).get('max_abs'),
     A.get('CHECK_a31_arc_k2')),
    ('P7', 'median Gamma*_2 >= 5e-5 at l = 4, 8, 16 and >= 0.2 x k2 total at l = 16',
     A.get('P7', {}).get('medians'), A.get('P7')),
    ('P8', 'median Gamma_rad/Gamma*_2 >= 0.5 at >= 2 of l = 8, 16, 24 (rule applied here to score_attr ratios)',
     A.get('P8_ratios_radgauss_over_gauss'), P8),
    ('P9a', 'PR3 <= covariance PR at every layer, every net', None, A.get('P9a')),
    ('P9b', 'PR3(1) >= 40 and PR3 <= 4 at l >= 16, every net (nets with rank runs)',
     {k: A.get('P9b', {}).get(k) for k in ('pr_l1', 'pr_deep_max')}, A.get('P9b')),
    ('P9c', 'held-out top-32 capture <= 0.2 at l = 1 and >= 0.9 at l = 16, every net',
     {k: A.get('P9c', {}).get(k) for k in ('cap32_l1', 'cap32_l16')}, A.get('P9c')),
    ('P9d', 'planted rank 32 control gives PR3 in [24, 40]', A.get('P9d_control_planted32', {}).get('pr'),
     A.get('P9d_control_planted32')),
    ('P10', 'exact Gaussian at 256 x 32: median nMSE in [2e-4, 2e-3], median G_RQMC <= 1.5',
     {k: P.get('P10', {}).get(k) for k in ('nmse', 'G_RQMC')}, P.get('P10')),
    ('P11', 'e*(256) >= 3 e*(32) and e*(128) >= e*(64)', P.get('P11', {}).get('e_star'), P.get('P11')),
    ('P12', 'e_3/e_2 >= 0.2 at n = 64, 128, 256', P.get('P12', {}).get('e3_over_e2'), P.get('P12')),
    ('P13', 'gamma_{2->3} < 1 at every n', {n: v.get('gamma23') for n, v in
                                           J['score_amend3.json'].get('per_width', {}).items()}, R3.get('P13')),
    ('P14', 'gamma_{2->3} in [0.5, 1.5] x log 8/log n at n = 128, 256',
     {n: (v.get('gamma23'), v.get('pred')) for n, v in J['score_amend3.json'].get('per_width', {}).items()},
     R3.get('P14')),
    ('R1', 'median Gamma_rad/Gamma*_2 <= 0.33 at >= 2 of l = 1, 2, 4 (nets 201-204)',
     R2.get('R1', {}).get('median_ratios'), R2.get('R1')),
    ('R2', 'median Z = max_{l = 8, 16, 24} Gamma_rad >= 5e-5 (201-204)', R2.get('R2', {}).get('median_Z'),
     R2.get('R2')),
    ('R3', 'RQMC reaches Z at <= 2e4 passes on >= 3 of 4 nets', R2.get('R3', {}).get('costs'), R2.get('R3')),
    ('P15', 'p(G1) in [0.6, 1.4]', R4.get('P15', {}).get('p_G1'), R4.get('P15')),
    ('P16', 'p(F1) >= p(G1) + 0.4', {k: R4.get('P16', {}).get(k) for k in ('p_F1', 'p_G1')}, R4.get('P16')),
    ('P17', 'p(Zm) in [0.5, 1.5]', R4.get('P17', {}).get('p_Zm'), R4.get('P17')),
    ('P18', 'Wr(256)/Wr(64) <= 2', R4.get('P18', {}).get('Wr_256_over_64'), R4.get('P18')),
    ('P19', 'Gaussian IPR within 1.5x of the deductive exact Gaussian recursion, every 256 net',
     R5.get('P19', {}).get('per_net_ok'), R5.get('P19')),
    ('P20', 'median radial IPR >= 0.5 Zm(256)', {k: R5.get('P20', {}).get(k) for k in ('median_radial_ipr', 'Zm256')},
     R5.get('P20')),
    ('P21', 'median radial IPR / Gaussian IPR <= 0.5 at 256', R5.get('P21', {}).get('median_ratio'), R5.get('P21')),
    ('P22', 'p_full in [0.5, 1.5] over n = 64, 128, 256', R5.get('P22', {}).get('p_full'), R5.get('P22')),
    ('P23', 'RQMC reaches the radial IPR error at <= 2e4 passes on >= 4 of 5 nets', R5.get('P23', {}).get('rqmc_costs'),
     R5.get('P23')),
    ('P24', 'rank-transport radial IPR: median replicate noise var at 256 <= 1e-4 (validity)',
     R6.get('P24', {}).get('median_noise_var'), R6.get('P24')),
    ('P25', 'median radial IPR2 >= 0.5 Zm(256)', {k: R6.get('P25', {}).get(k) for k in ('median_radial_ipr', 'Zm256')},
     R6.get('P25')),
    ('P26', 'median radial IPR2 / Gaussian IPR2 <= 0.5 at 256', R6.get('P26', {}).get('median_ratio'), R6.get('P26')),
    ('P27', 'RQMC reaches the radial IPR2 error at <= 2e4 passes on >= 4 of 5 nets', R6.get('P27', {}).get('rqmc_costs'),
     R6.get('P27')),
    ('P28', 'p_full (IPR2) in [0.5, 1.5] over n = 64, 128, 256', R6.get('P28', {}).get('p_full'), R6.get('P28')),
]
L = ['# Pre-registration scorecard (generated by scratch/scorecard.py from the hashed scorers)\n',
     '| id | prediction (PREREG wording abbreviated) | measured | result |', '|---|---|---|---|']
for i, d, v, h in rows:
    L.append(f'| {i} | {d} | {f(v)} | {STATE.get(i.split()[0], hit(h)) if i.split()[0] in STATE else hit(h)} |')
open(os.path.join(RES, 'scorecard.md'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
