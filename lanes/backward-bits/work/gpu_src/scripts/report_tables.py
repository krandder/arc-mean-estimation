"""Markdown tables for the report from <scores.json> (score.py) and the raw run directory.
usage: report_tables.py <root> <scores.json> <out.md>
Tables: (1) per config and layer, median over seeds [min-max]: truth, chain K (target, rate, relevance, I_out),
chain PR (target, rate, I_out), direct rate for 95% of the truth, certified seeds; (2) the certified-count bracket;
(3) per chain at the input: I_out / I*_0 per net; (4) first-step gap; (5) crn at a few layers; (6) Gaussian vs partition
at rate T; (7) forward-trained codes against chain codes; (8) erasure profile; (9) certificate pass rates.
"""
import json
import os
import statistics as stx
import sys

ROOT, SC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
S = json.load(open(SC))
rows = S['rows']
cfgs = sorted(set(r['cfg'] for r in rows), key=lambda c: [int(v) for v in c.split('x')])
lines = []


def mr(xs, nd=2):
    xs = [x for x in xs if x is not None]
    if not xs:
        return '-'
    m = stx.median(xs)
    if len(xs) == 1:
        return f'{m:.{nd}f}'
    return f'{m:.{nd}f} [{min(xs):.{nd}f}-{max(xs):.{nd}f}]'


def get(rs, k):
    return [r.get(k) for r in rs]


# (1) per layer
for cfg in cfgs:
    rs = [r for r in rows if r['cfg'] == cfg]
    L = max(r['l'] for r in rs) + 1
    lines.append(f'### {cfg} (median over seeds [range]; bits)\n')
    lines.append('| l | truth I*_l | K target T | K rate H | K carries I(c;next) | K knows I(c;c_L) | PR target | PR rate H | '
                 'PR knows I(c;c_L) | direct rate for 0.95 I* | certified K / PR |')
    lines.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for l in sorted(set(r['l'] for r in rs), reverse=True):
        rl = [r for r in rs if r['l'] == l]
        cert = lambda ch: f"{sum(1 for r in rl if r.get(f'{ch}_certified'))}/{sum(1 for r in rl if r.get(f'{ch}_certified') is not None)}" \
            if any(r.get(f'{ch}_certified') is not None for r in rl) else '-'
        lines.append(f"| {l} | {mr(get(rl, 'I_star'))} | {mr(get(rl, 'K_T'))} | {mr(get(rl, 'K_H'))} | {mr(get(rl, 'K_I'))} | "
                     f"{mr(get(rl, 'K_I_out'))} | {mr(get(rl, 'PR_T'))} | {mr(get(rl, 'PR_H'))} | {mr(get(rl, 'PR_I_out'))} | "
                     f"{mr(get(rl, 'dir_relevance_rho_H'))} | {cert('K')} / {cert('PR')} |")
    lines.append('')

# (2) certified-count bracket and erasure profile
lines.append('### Certified count per layer: bits a code needs to carry 95% of what the layer knows about the output code\n')
lines.append('Lower end 0.95 I*_l (no code carrying that much can have less rate); upper end the least rate of a certified '
             'chain-PR code or a direct code that carries at least 0.95 I*_l on the test set. Median over seeds [range]; '
             '"-" = no such code found.\n')
lines.append('| config | l | 0.95 I*_l | upper end | upper / lower | truth loses from l+1 to l |')
lines.append('|---|---|---|---|---|---|')
for cfg in cfgs:
    rs = [r for r in rows if r['cfg'] == cfg]
    L = max(r['l'] for r in rs) + 1
    for l in sorted(set(r['l'] for r in rs), reverse=True):
        if l == L - 1:
            continue
        lo, up, ratio, drop = [], [], [], []
        for r in [r for r in rs if r['l'] == l and 'I_star' in r]:
            lo.append(0.95 * r['I_star'])
            cands = []
            if r.get('PR_I_out') is not None and r['PR_I_out'] >= 0.95 * r['I_star'] and r.get('PR_certified'):
                cands.append(r['PR_H'])
            if r.get('dir_relevance_rho_I') is not None and r['dir_relevance_rho_I'] >= 0.95 * r['I_star']:
                cands.append(r['dir_relevance_rho_H'])
            if cands:
                up.append(min(cands))
                ratio.append(min(cands) / max(0.95 * r['I_star'], 1e-9))
            nxt = next((x for x in rows if x['net'] == r['net'] and x['l'] == l + 1 and 'I_star' in x), None)
            if nxt:
                drop.append(nxt['I_star'] - r['I_star'])
        lines.append(f"| {cfg} | {l} | {mr(lo)} | {mr(up)} | {mr(ratio)} | {mr(drop)} |")
lines.append('')

# (3) at the input
lines.append('### At the input (l = 0): share of the truth each chain keeps, per net\n')
lines.append('| net | I*_0 | K: I_out / I* | R: I_out / I* | P: I_out / I* | PR: I_out / I* | PR: rate | PR: I_chain / I_out | '
             'K target T_0 | R target T_0 |')
lines.append('|---|---|---|---|---|---|---|---|---|---|')
for r in sorted([r for r in rows if r['l'] == 0 and 'I_star' in r], key=lambda r: (r['cfg'], r['seed'])):
    f = lambda ch: f"{r[f'{ch}_I_out'] / r['I_star']:.0%}" if r.get(f'{ch}_I_out') is not None and r['I_star'] > 0 else '-'
    ic = f"{r['PR_I_chain'] / r['PR_I_out']:.0%}" if r.get('PR_I_chain') is not None and r.get('PR_I_out') else '-'
    lines.append(f"| {r['cfg']} s{r['seed']} | {r['I_star']:.2f} | {f('K')} | {f('R')} | {f('P')} | {f('PR')} | "
                 f"{r.get('PR_H', float('nan')):.2f} | {ic} | {r.get('K_T', float('nan')):.2f} | {r.get('R_T', float('nan')):.2f} |")
lines.append('')

# (4) first step
lines.append('### First backward step (l = L-2): the gap, per net\n')
lines.append('| net | H(c_L) | erased | T | rate rule: H, I (I/T) | 95% rule (R): H, I | reuse: H, I |')
lines.append('|---|---|---|---|---|---|---|')
for name in sorted(set(r['net'] for r in rows)):
    rr = [r for r in rows if r['net'] == name]
    L = max(r['l'] for r in rr) + 1
    r = next((x for x in rr if x['l'] == L - 2), None)
    top = next((x for x in rr if x['l'] == L - 1), None)
    if not r or 'K_T' not in r:
        continue
    HcL = top.get('K_H') if top else None
    lines.append(f"| {r['cfg']} s{r['seed']} | {HcL:.2f} | {r['K_erased']:.2f} | {r['K_T']:.2f} | {r['K_H']:.2f}, "
                 f"{r['K_I']:.2f} ({r['K_I'] / r['K_T']:.0%}) | {r.get('R_H', float('nan')):.2f}, {r.get('R_I', float('nan')):.2f} | "
                 f"{r['K_reuse_H']:.2f}, {r['K_reuse_I']:.2f} |")
lines.append('')

# (10) deeper encoders
lines.append('### Deeper encoders: does depth help, and where is the reuse composition chosen?\n')
lines.append('| config | C4 fails (depth 4 beats depth 2), K | C4 fails, PR | excess CE (bits), K, upper half of layers | '
             'excess CE, K, lower half | reuse selected: K / R / P / PR (steps) | direct predictor excess CE, upper / lower half |')
lines.append('|---|---|---|---|---|---|---|')
for cfg in cfgs:
    rs = [r for r in rows if r['cfg'] == cfg]
    L = max(r['l'] for r in rs) + 1
    noisy_rs = [r for r in rs if r['l'] < L - 1]
    up = [r for r in noisy_rs if r['l'] >= (L - 1) / 2]
    lo = [r for r in noisy_rs if r['l'] < (L - 1) / 2]
    c4 = lambda ch: f"{sum(1 for r in noisy_rs if r.get(f'{ch}_C4') is False)}/{sum(1 for r in noisy_rs if r.get(f'{ch}_C4') is not None)}"
    reuse = ' / '.join(str(sum(1 for r in noisy_rs if r.get(f'{ch}_kind') == 'reuse')) for ch in ('K', 'R', 'P', 'PR'))
    lines.append(f"| {cfg} | {c4('K')} | {c4('PR')} | {mr(get(up, 'K_exce'), 3)} | {mr(get(lo, 'K_exce'), 3)} | {reuse} | "
                 f"{mr(get(up, 'dir_exce'), 3)} / {mr(get(lo, 'dir_exce'), 3)} |")
lines.append('')

# (9) certificates
lines.append('### Certificate pass rates (chains K and PR, all steps)\n')
lines.append('| certificate | K | PR |')
lines.append('|---|---|---|')
for c in ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'certified']:
    vals = []
    for ch in ('K', 'PR'):
        xs = [r.get(f'{ch}_{c}') for r in rows if r.get(f'{ch}_{c}') is not None]
        vals.append(f'{sum(xs)}/{len(xs)} ({sum(xs) / len(xs):.0%})' if xs else '-')
    lines.append(f'| {c} | {vals[0]} | {vals[1]} |')
lines.append('')

# (6) Gaussian
g = S.get('gauss') or []
if g:
    lines.append('### Gaussian channel against partitions at rate T (chain K steps)\n')
    lines.append('| net | l | T | partition (H <= T): I | Gaussian at info rate T: I |')
    lines.append('|---|---|---|---|---|')
    for e in sorted(g, key=lambda e: (e['net'], -e['l'])):
        lines.append(f"| {e['net']} | {e['l']} | {e['T']:.2f} | {e['I_partition']:.2f} ({e['I_partition'] / e['T']:.0%}) | "
                     f"{e['I_gauss_at_T']:.2f} ({e['I_gauss_at_T'] / e['T']:.0%}) |")
    lines.append('')

# (7) forward-trained codes
fw = []
for name in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, name, 'fwd.json')
    if os.path.exists(p):
        fw.append((name, json.load(open(p))))
if fw:
    lines.append('### Forward-trained codes (trained on the shared-noise distortion) against the chains\' codes\n')
    lines.append('| net | l | I*_l | forward codes: K cells -> (H, I(c;c_L), crn) | chain K (H, I_out, crn) | chain PR (H, I_out, crn) |')
    lines.append('|---|---|---|---|---|---|')
    for name, d in fw:
        for l, e in sorted(d.items(), key=lambda kv: -int(kv[0])):
            r = next((x for x in rows if x['net'] == name and x['l'] == int(l)), {})
            fcodes = '; '.join(f"{x['K']}: ({x['H']:.2f}, {x['I_out']:.2f}, {x['learned']['crn']:.3f})" for x in e['rows'])
            ck = f"({r.get('K_H', float('nan')):.2f}, {r.get('K_I_out', float('nan')):.2f}, {r.get('crn_chainK', float('nan')):.3f})"
            cp = f"({r.get('PR_H', float('nan')):.2f}, {r.get('PR_I_out', float('nan')):.2f}, {r.get('crn_chainPR', float('nan')):.3f})"
            lines.append(f"| {name} | {l} | {e['I_star']:.2f} | {fcodes} | {ck} | {cp} |")
    lines.append('')

open(OUT, 'w').write('\n'.join(lines) + '\n')
print('wrote', OUT, len(lines), 'lines')
