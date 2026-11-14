"""Assemble bit-accounting.md (phase-1 report) from results/P1_scores.json (score_P1v2.py), the method notes and the
earlier (v1) sections. Numbers in the summary and the tables are computed here; the prose around them is fixed.
usage: python3 scratch/build_report.py [status line]"""
import json
import math
import sys

import numpy as np

W = '/home/agent/workspaces/mats/work/bit-accounting'
S = json.load(open(f'{W}/results/P1_scores.json'))
sc, cells = S['scores'], S['cells']


def key(kind, n, L, s, l, cls):
    return f'{kind}_{n}_{L}_{s}_{l}_{cls}'


def vals(kind, n, L, l, cls, D, field='R'):
    out = []
    for s in (5000, 5001, 5002):
        c = cells.get(key(kind, n, L, s, l, cls))
        if c is not None:
            out.append(c[field].get(str(D)))
    return out


def med(v, nd=1):
    v2 = [x for x in v if x is not None]
    if not v:
        return 'pending'
    if not v2:
        return 'unreached'
    s = f'{np.median(v2):.{nd}f}'
    if len(v2) > 1:
        s += f' [{min(v2):.{nd}f}-{max(v2):.{nd}f}]'
    if len(v2) < len(v):
        s += f' ({len(v) - len(v2)} unreached)'
    return s


def slope_list(kind, n, L, l, cls, D1=0.1, D2=0.01):
    out = []
    for s in (5000, 5001, 5002):
        c = cells.get(key(kind, n, L, s, l, cls))
        if c is not None and c['R'].get(str(D1)) is not None and c['R'].get(str(D2)) is not None:
            out.append((c['R'][str(D2)] - c['R'][str(D1)]) / math.log2(D1 / D2))
    return out


NETS = [('relu', 16, 4), ('relu', 32, 8), ('relu', 16, 16), ('relu', 32, 32), ('tanh4', 16, 16), ('feistel', 16, 16),
        ('linear', 16, 16)]


def layers(L):
    return sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))


tab = ['| net | layer | class | bits for 10% error | bits for 1% | bits for 0.1% | bits per halving (10% -> 1%) | '
       'single model r0, 10% / 1% | linear reference 10% / 1% | seeds |', '|' + '---|' * 10]
for kind, n, L in NETS:
    for l in layers(L) + [L]:
        for cls in (['unres'] if l == L else ['local', 'unres']):
            ks = [key(kind, n, L, s, l, cls) for s in (5000, 5001, 5002) if key(kind, n, L, s, l, cls) in cells]
            if not ks:
                continue
            sl = slope_list(kind, n, L, l, cls)
            lin1, lin2 = vals(kind, n, L, l, cls, 0.1, 'R_linref'), vals(kind, n, L, l, cls, 0.01, 'R_linref')
            tab.append(f'| {kind} {n}x{L} | {"output" if l == L else l} | {cls} | {med(vals(kind, n, L, l, cls, 0.1))} | '
                       f'{med(vals(kind, n, L, l, cls, 0.01))} | {med(vals(kind, n, L, l, cls, 0.001))} | '
                       f'{(f"{np.median(sl):.2f}" if sl else "-")} | '
                       f'{med(vals(kind, n, L, l, cls, 0.1, "R_r0"))} / {med(vals(kind, n, L, l, cls, 0.01, "R_r0"))} | '
                       f'{med(lin1)} / {med(lin2)} | {len(ks)} |')

def pred_line(k, txt):
    v = sc.get(k, {})
    h = v.get('hit')
    hs = 'hit' if h is True else ('missed' if h is False else str(h))
    extra = ''
    if 'hits' in v and 'n' in v:
        extra = f' ({v["hits"]}/{v["n"]})'
    elif v.get('frac') is not None and 'n' in v:
        extra = f' ({round(v["frac"] * v["n"])}/{v["n"]})'
    return f'- {k}: {txt}: {hs}{extra}'


preds = ['Registered predictions (PREREG P1; scored by gpu_src/scripts/score_P1v2.py):', '',
         pred_line('KA1', 'output codes within 0.3 bit of the Gaussian bound or below, every ReLU net'),
         pred_line('KA2 (empirical comparison)', 'unrestricted within max(0.5 bit, 15%) of the output curve on >= 90%'),
         pred_line('KA3', 'linear net: the Gaussian answer at every layer, both classes'),
         pred_line('P1.1', 'certificates C1, C2, C3 (unres), C4, C5 (v2), C7 each pass on >= 90%'),
         pred_line('P1.2', 'local count at the input >= 2x the output count on >= 5 of the 6 L = n nets'),
         pred_line('P1.3', 'local count not rising with depth on >= 80% of the 12 ReLU nets'),
         pred_line('P1.4', 'output slope smaller on the deeper net of each width, every seed'),
         f'- P1.5: controls (tanh4, feistel, linear): {sc.get("P1.5", {}).get("hit")} (parts {sc.get("P1.5", {}).get("parts")})']
cov = {}
for k, c in cells.items():
    kind, n, L, s_, l, cls = k.split('_')
    for D in ('0.3', '0.1', '0.03', '0.01', '0.003', '0.001'):
        if c['R'].get(D) is None:
            g = cov.setdefault((f'{kind} {n}x{L}', D), [0, 0])
            g[0] += 1
            g[1] += c['R_linref'].get(D) is not None
covtab = ['| net | error level | cells not reached by learned codes | of these, reached by the linear reference |',
          '|---|---|---|---|'] + [f'| {a} | {D} | {v[0]} | {v[1]} |' for (a, D), v in sorted(cov.items())]
cert_names = {'C1': 'three restarts agree', 'C2': '2x steps does not improve', 'C3': '2x width does not improve (unres)',
              'C3_local': '2x width does not improve (local: width 2n leaves the class)', 'C4': 'refitted priors no better',
              'C5': 'centroid (first version)', 'C5v2': 'output-space residual centroid (amendment)',
              'C6_r0': 'one model for all prices within 3% of single-price models',
              'C6_long': 'same, for the 2x-steps model', 'C7': 'learned code at or below the linear reference'}
cert = ['| certificate | passes | points | not covered |', '|---|---|---|---|']
for k, name in cert_names.items():
    v = sc.get(k, {})
    cert.append(f'| {k}: {name} | {("-" if v.get("frac") is None else f"{100 * v["frac"]:.0f}%")} | {v.get("n", 0)} | '
                f'{v.get("not_covered", 0)} |')

status = sys.argv[1] if len(sys.argv) > 1 else 'REPORT v2 (phase 1, interim)'
head = open(f'{W}/notes/report_v2_head.txt').read()
head = head.replace('Status: REPORT v2 (phase 1).', f'Status: {status}. Coverage: main cells {sc["coverage"]["main"]}, extra '
                    f'certificates {sc["coverage"]["certificates"]}.')
summary = open(f'{W}/notes/report_v2_summary.txt').read() if __import__('os').path.exists(f'{W}/notes/report_v2_summary.txt') else '[summary pending]\n'
sys.path.insert(0, f'{W}/scratch')
from summary_fill import fill  # noqa: E402
head = head.replace('[filled from results]', fill(summary.strip()))
method = open(f'{W}/notes/report_p1_method.txt').read()
head = head.replace('## 1. What phase 1 measures\n\n[notes/report_p1_method.txt]', method.strip())
parts = [head.strip(), '',
         '## 2. Bits per layer (phase 1; median over seeds [range]; "unreached" = beyond the trained price range)', '',
         'Counts are conservative (time-sharing between achieved points). "Bits" columns = R*, the best code of the class '
         'found by any variant (an envelope over several models); "single model r0" = the registered single '
         'lambda-conditioned model, which is often several bits higher at the early layers. Every cell, seed, source and '
         'certificate flag: results/P1_table.md; curves: figs/P1_curves_*.png.', ''] + tab + ['',
         '## 3. What the certificates show, and what they do not (registered in PREREG P1, P1-A)', '',
         'Share of (cell, error level) points where each check passes; "not covered" = the curves do not reach that error '
         'within the trained price range.', ''] + cert + [''] + preds + ['',
         open(f'{W}/notes/report_v2_certs.txt').read().strip() if __import__('os').path.exists(f'{W}/notes/report_v2_certs.txt') else '',
         '', 'Where the learned curves do not reach an error level within the trained price range (lambda >= 1e-4):', ''] + covtab + ['',
         open(f'{W}/notes/report_p2_part1.txt').read().strip() if __import__('os').path.exists(f'{W}/notes/report_p2_part1.txt') else '',
         '', open(f'{W}/notes/report_p2_maps.txt').read().strip() if __import__('os').path.exists(f'{W}/notes/report_p2_maps.txt') else '',
         '', open(f'{W}/notes/report_p2_U.txt').read().strip() if __import__('os').path.exists(f'{W}/notes/report_p2_U.txt') else '',
         '', open(f'{W}/notes/report_p2_noisy.txt').read().strip() if __import__('os').path.exists(f'{W}/notes/report_p2_noisy.txt') else '',
         '',
         '', '## 4. Earlier measurements (before phase 1): fixed-budget codes, ARC and narrow-deep', '',
         open(f'{W}/notes/report_v1_section3.md').read().strip(), '',
         '## 5. Background for phase 2: scrambling, the curriculum autoencoder, shared noise, estimation (earlier runs)', '',
         open(f'{W}/notes/report_v1_sections4to7.md').read().strip(), '',
         open(f'{W}/notes/report_v1_sections8to9.md').read().strip(), '']
open(f'{W}/bit-accounting.md', 'w').write('\n'.join(parts) + '\n')
print('written', sum(1 for _ in open(f'{W}/bit-accounting.md')), 'lines')
