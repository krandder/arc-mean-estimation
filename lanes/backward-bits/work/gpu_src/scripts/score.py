"""Scorer for the backward-bits lane (PREREG.md). Reads <root>/<net>/chain{K,R,P,PR}/chain.json, truth.json and the
optional gauss.json / fwd.json / conv_check.json; writes <outdir>/scores.json, <outdir>/layers.md (every net and
layer), <outdir>/summary.md (by config and relative depth), and the verdicts of the registered predictions.
usage: score.py <root> <outdir> [--nets n16L16_s5000_sig0.1_K64,...]   (default: every net under root)
"""
import json
import math
import os
import statistics as stx
import sys

ROOT, OUT = sys.argv[1], sys.argv[2]
NETS = None
if '--nets' in sys.argv:
    NETS = sys.argv[sys.argv.index('--nets') + 1].split(',')
os.makedirs(OUT, exist_ok=True)

# registered tolerances (PREREG.md section 4)
TOL = dict(T_se=0.01, T_gr=0.01, exce=0.02, exce_rel=0.02, restart_I=0.03, restart_I_rel=0.03, restart_H=0.15,
           restart_H_rel=0.05, depth_I=0.03, depth_I_rel=0.03, depth_H=0.15, depth_H_rel=0.05, la_I=0.03, cons=0.01,
           tolH=0.02, rho=0.05)
CHAINS = ['K', 'R', 'P', 'PR']
RATE_RULE = {'K': True, 'R': False, 'P': True, 'PR': False}


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def tolI(T, a, r):
    return max(a, r * abs(T))


REQUIRED = {'K': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'], 'PR': ['C1', 'C2', 'C3', 'C4', 'C6'],
            'R': ['C1', 'C2', 'C6'], 'P': ['C1', 'C2', 'C6']}       # per PREREG section 2 (review r1 #15)


def cert_step(ch, st, H_next):
    """Certificate flags for one step (PREREG section 4). A required certificate with missing evidence is None
    ('incomplete'), never a pass (review r1 #15)."""
    t = st['target']
    sel = st['selected']
    T = t['T']
    f = {}
    if ch in ('K', 'R'):
        f['C1'] = (t['se'] <= TOL['T_se'] and abs(T - t['T_gr']) <= TOL['T_gr']) if 'T_gr' in t else None
    else:
        f['C1'] = t['se'] <= TOL['T_se'] and abs(t['H_rich'] - t['H_plugin']) <= 0.05
    if sel.get('kind') == 'reuse':                 # an exact reuse code uses no predictor
        f['C2'] = True
    else:
        f['C2'] = st['predictor']['excess_ce_te'] <= tolI(T, TOL['exce'], TOL['exce_rel'])
    cert = st.get('cert') or {}
    if 'C3' in REQUIRED[ch]:
        r = cert.get('restart')
        if r is None:
            f['C3'] = None
        elif RATE_RULE[ch]:
            f['C3'] = abs(r['I'] - sel['I']) <= tolI(T, TOL['restart_I'], TOL['restart_I_rel'])
        else:
            f['C3'] = abs(r['H'] - sel['H']) <= max(TOL['restart_H'], TOL['restart_H_rel'] * sel['H'])
    if 'C4' in REQUIRED[ch]:
        r = cert.get('depth4')
        if r is None:
            f['C4'] = None
        elif RATE_RULE[ch]:
            f['C4'] = r['I'] - sel['I'] <= tolI(T, TOL['depth_I'], TOL['depth_I_rel'])
        else:
            f['C4'] = sel['H'] - r['H'] <= max(TOL['depth_H'], TOL['depth_H_rel'] * sel['H'])
    if 'C5' in REQUIRED[ch]:
        la = st.get('lookahead')
        if not la:
            f['C5'] = None
        else:
            best = max([x['I'] for x in la if x['H'] <= sel['H'] + TOL['tolH']] + [0.0])
            f['C5'] = best - sel['I'] <= TOL['la_I']
    f['C6'] = (T <= H_next + TOL['cons']) and (sel['I'] <= min(sel['H'], T) + TOL['cons'])
    return f


def certified(flags):
    """True (all pass), False (some fail), None (none fail but some evidence missing: incomplete)."""
    if any(v is False for v in flags.values()):
        return False
    if any(v is None for v in flags.values()):
        return None
    return True


def net_list():
    if NETS:
        return NETS
    return sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)) and d.startswith('n'))


def parse(name):
    a, s, sig, K = name.split('_')
    n, L = a[1:].split('L')
    return int(n), int(L), int(s[1:]), float(sig[3:]), int(K[1:])


nets = {}
for name in net_list():
    n, L, seed, sigma, KL = parse(name)
    d = dict(n=n, L=L, seed=seed, sigma=sigma, KL=KL, chains={}, truth=None)
    for ch in CHAINS:
        c = load(os.path.join(ROOT, name, f'chain{ch}', 'chain.json'))
        if c and c.get('done'):
            d['chains'][ch] = c
            gp = os.path.join(ROOT, name, f'chain{ch}', 'gauss_p.json')        # amended power-constrained run (D8)
            d.setdefault('gauss', {})[ch] = load(gp) if os.path.exists(gp) else load(os.path.join(ROOT, name, f'chain{ch}', 'gauss.json'))
            d.setdefault('conv', {})[ch] = load(os.path.join(ROOT, name, f'chain{ch}', 'conv_check.json'))
    tr = load(os.path.join(ROOT, name, 'truth.json'))
    d['truth'] = tr if tr and tr.get('done') else None
    d['fwd'] = load(os.path.join(ROOT, name, 'fwd.json'))
    nets[name] = d

rows = []
for name, d in nets.items():
    L = d['L']
    for l in range(L - 1, -1, -1):
        r = dict(net=name, cfg=f"{d['n']}x{L}", seed=d['seed'], l=l, rel=l / (L - 1))
        if d['truth'] and str(l) in d['truth']['layers']:
            t = d['truth']['layers'][str(l)]
            r['I_star'] = t['truth']['T']
            r['I_star_se'] = t['truth'].get('se_boot', t['truth']['se'])
            for ch, v in t['chains'].items():
                r[f'{ch}_I_out'] = v['I_out']
                r[f'{ch}_I_chain'] = v['I_chain']
                r[f'{ch}_H_truthpass'] = v['H']
            for k, v in t.get('direct', {}).get('selected', {}).items():
                r[f'dir_{k}_H'] = v['H']
                r[f'dir_{k}_I'] = v['I']
            if t.get('direct'):
                r['dir_exce'] = t['direct']['predictor']['excess_ce_te']
            cr = t.get('crn', {})
            for k, v in cr.items():
                if isinstance(v, dict) and 'mean' in v:
                    r[f'crn_{k}'] = v['mean']['crn']
                    r[f'crnopt_{k}'] = v['opt']['crn']
                    r[f'avg_{k}'] = v['mean']['avg']
        for ch, c in d['chains'].items():
            st = c['steps'].get(str(l))
            if st is None:
                continue
            if l == L - 1:
                r[f'{ch}_T'] = st['T']
                r[f'{ch}_H'] = st['H']
                r[f'{ch}_I'] = st['I']
                continue
            Hn = c['steps'][str(l + 1)]['selected']['H'] if l + 1 < L - 1 else c['steps'][str(L - 1)]['H']
            r[f'{ch}_T'] = st['target']['T']
            r[f'{ch}_T_se'] = st['target']['se']
            r[f'{ch}_erased'] = st['target']['erased']
            r[f'{ch}_H'] = st['selected']['H']
            r[f'{ch}_I'] = st['selected']['I']
            r[f'{ch}_K'] = st['selected']['K']
            r[f'{ch}_kind'] = st['selected'].get('kind')
            r[f'{ch}_reached'] = st['selected']['reached']
            r[f'{ch}_exce'] = st['predictor']['excess_ce_te']
            r[f'{ch}_reuse_H'] = st['reuse']['H']
            r[f'{ch}_reuse_I'] = st['reuse']['I']
            r[f'{ch}_LB'] = st.get('lower_bound_Kcells')
            r[f'{ch}_Hnext'] = Hn
            for k, v in (st.get('cert') or {}).items():
                r[f'{ch}_cert_{k}_H'] = v['H']
                r[f'{ch}_cert_{k}_I'] = v['I']
                r[f'{ch}_cert_{k}_exce'] = v['excess_ce_te']
            flags = cert_step(ch, st, Hn)
            for k, v in flags.items():
                r[f'{ch}_{k}'] = v
            r[f'{ch}_certified'] = certified(flags)
            r[f'{ch}_reached'] = st['selected'].get('reached')
            r[f'{ch}_maxcand_H'] = max([e['H'] for e in st.get('cands', [])] + [st['selected']['H']])
        rows.append(r)


def med(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return stx.median(xs) if xs else None


def frac(xs):
    xs = [x for x in xs if x is not None]
    return (sum(1 for x in xs if x) / len(xs)) if xs else None


# ---------------------------------------------------------------- registered predictions (PREREG section 5)
EXPECTED_NETS = 12          # 4 configs x 3 seeds (review r1 #19: a verdict on fewer is provisional)
pred = {}
noisy = [r for r in rows if 'K_T' in r and r['l'] < parse(r['net'])[1] - 1]
inputs = [r for r in rows if r['l'] == 0 and 'I_star' in r]
first = [r for r in rows if r['l'] == parse(r['net'])[1] - 2]
n_nets_truth = len(set(r['net'] for r in inputs))


def count(xs, k, expected=EXPECTED_NETS):
    dec = [x for x in xs if x is not None]
    return dict(count=sum(dec), n=len(dec), undecided=len(xs) - len(dec), expected=expected, hit=sum(dec) >= k,
                provisional=len(dec) < expected)


def share(xs, f, none_is=None):
    xs = [(none_is if x is None else x) for x in xs]
    dec = [x for x in xs if x is not None]
    v = (sum(dec) / len(dec)) if dec else None
    return dict(value=v, n=len(dec), undecided=len(xs) - len(dec), hit=(v is not None and v >= f),
                provisional=(n_nets_truth < EXPECTED_NETS))


pred['B1'] = share([r['K_T'] - r['K_I'] >= 0.1 * r['K_T'] for r in noisy if 'K_I' in r], 0.9)
HcL = {name: d['chains'][next(iter(d['chains']))]['out']['H_cL'] for name, d in nets.items() if d['chains']}
b2, b3 = [], []
for r in first:
    ch = 'R' if 'R_H' in r else ('PR' if 'PR_H' in r else None)
    if ch is None:
        continue
    T, H, top = r[f'{ch}_T'], r[f'{ch}_H'], HcL[r['net']]
    if r.get(f'{ch}_reached'):
        b2.append(H >= T + 1.0)
        b3.append(H > top + 0.5)
    else:      # 95% not reached: the needed rate exceeds the largest candidate tried (review r1 #16)
        mx = r[f'{ch}_maxcand_H']
        b2.append(True if mx >= T + 1.0 else None)
        b3.append(True if mx > top + 0.5 else None)
pred['B2'] = count(b2, 10)
pred['B3'] = count(b3, 9)
pred['B4'] = count([r['K_I_out'] <= 0.6 * r['I_star'] for r in inputs if 'K_I_out' in r], 9)
pred['B5'] = count([r['PR_I_out'] >= 0.8 * r['I_star'] for r in inputs if 'PR_I_out' in r], 9)
pred['B6'] = count([r['R_T'] >= r['I_star'] + 0.25 for r in inputs if 'R_T' in r], 9)
pred['B7'] = count([r['K_T'] <= r['I_star'] - 0.25 for r in inputs if 'K_T' in r], 9)
pred['B8'] = count([r['PR_I_chain'] >= 0.9 * r['PR_I_out'] for r in inputs if 'PR_I_chain' in r], 9)
pred['B9'] = share([r['dir_rate_K_I'] - r['K_I_out'] <= 0.15 for r in rows
                    if 'dir_rate_K_I' in r and 'K_I_out' in r and r['l'] < parse(r['net'])[1] - 1], 0.8)
pred['B10'] = share([r.get(f'{ch}_C4') for r in rows for ch in ('K', 'PR') if f'{ch}_C4' in r], 0.9, none_is=False)
pred['B11'] = share([r.get(f'{ch}_certified') for r in rows for ch in ('K', 'PR') if f'{ch}_certified' in r], 0.9,
                    none_is=False)
pred['B12'] = count([r['crn_chainPR'] < r['crn_chainK'] for r in inputs if 'crn_chainPR' in r and 'crn_chainK' in r], 9)
# Gaussian channel (B13, B14): linear interpolation along the measured curve, ordered by rate; layers whose curve does
# not bracket T are unresolved (review r1 #18)
b13, b14, gauss_rows = [], [], []
for name, d in nets.items():
    g = (d.get('gauss') or {}).get('K')
    if not g:
        continue
    for l, e in g.items():
        for row in e['rows']:
            ests = [row['rate_mc'], row['rate_mc_loo'], row['rate_mc_half'], row['rate_mc_loo_half']]
            if row['rate_mc'] <= 6:
                b13.append(max(ests) - min(ests) <= 0.15)
        pts = sorted((row['rate_mc'], row['I_dec']) for row in e['rows'])
        T = e['T']
        IG = None
        for (r0, i0), (r1, i1) in zip(pts, pts[1:]):
            if r0 <= T <= r1:
                IG = i0 + (i1 - i0) * (T - r0) / max(r1 - r0, 1e-9)
                break
        b14.append(None if IG is None else IG >= e['discrete']['I'] + 0.1)
        gauss_rows.append(dict(net=name, l=int(l), T=T, I_gauss_at_T=IG, I_partition=e['discrete']['I'],
                               H_partition=e['discrete']['H'], rates=[p_[0] for p_ in pts]))
pred['B13'] = share(b13, 0.9)
pred['B14'] = share(b14, 0.75)

# ---------------------------------------------------------------- PREREG section 6 checks (review r1 #17)
checks = {}
viol = []
for name in nets:
    rs = sorted([r for r in rows if r['net'] == name and 'I_star' in r], key=lambda r: r['l'])
    for a_, b_ in zip(rs, rs[1:]):
        if b_['l'] == a_['l'] + 1 and a_['I_star'] > b_['I_star'] + 0.01 + 3 * max(a_.get('I_star_se', 0), 0.0):
            viol.append((name, a_['l']))
checks['truth_monotone_violations'] = viol
allway = {}
for cfg in sorted(set(r['cfg'] for r in rows)):
    rs = [r for r in rows if r['cfg'] == cfg]
    seeds = sorted(set(r['seed'] for r in rs))
    L = max(r['l'] for r in rs) + 1
    for ch in CHAINS:
        cert_ok, info_ok, complete = True, True, True
        for l in range(0, L - 1):
            rl = [r for r in rs if r['l'] == l]
            cs = [r.get(f'{ch}_certified') for r in rl]
            if len([c for c in cs if c is not None]) < len(seeds):
                complete = False
            if sum(1 for c in cs if c is True) < 2:
                cert_ok = False
            ok80 = [r[f'{ch}_I_out'] >= 0.8 * r['I_star'] for r in rl if f'{ch}_I_out' in r and 'I_star' in r]
            if len(ok80) < len(seeds):
                complete = False
            if sum(ok80) < 2:
                info_ok = False
        allway[f'{cfg}_{ch}'] = dict(certified_steps=cert_ok, carries_80pct=info_ok, complete=complete,
                                     verdict=(cert_ok and info_ok))
checks['certified_all_the_way'] = allway

json.dump(dict(tol=TOL, predictions=pred, checks=checks, gauss=gauss_rows, rows=rows), open(os.path.join(OUT, 'scores.json'), 'w'), indent=1)


def f3(v):
    if v is None:
        return '-'
    if isinstance(v, bool):
        return 'y' if v else 'n'
    return f'{v:.3f}' if abs(v) < 100 else f'{v:.1f}'


# every net and layer
cols = ['l', 'I_star', 'K_T', 'K_H', 'K_I', 'K_I_out', 'K_I_chain', 'K_certified', 'R_T', 'R_H', 'R_I', 'R_I_out',
        'P_T', 'P_H', 'P_I_out', 'PR_T', 'PR_H', 'PR_I_out', 'PR_I_chain', 'PR_certified', 'dir_rate_K_H',
        'dir_rate_K_I', 'dir_rate_truth_H', 'dir_rate_truth_I', 'dir_relevance_rho_H', 'dir_relevance_rho_I',
        'crn_chainK', 'crn_chainPR', 'crn_direct_rate_truth', 'crn_zero_bit']
with open(os.path.join(OUT, 'layers.md'), 'w') as fh:
    fh.write('# Every net and layer (bits; crn = shared-noise output nMSE, cell-mean decoder)\n\n')
    for name in nets:
        fh.write(f'## {name}\n\n| ' + ' | '.join(cols) + ' |\n|' + '---|' * len(cols) + '\n')
        for r in [r for r in rows if r['net'] == name]:
            fh.write('| ' + ' | '.join(f3(r.get(c)) if c != 'l' else str(r['l']) for c in cols) + ' |\n')
        fh.write('\n')

# summary by config and layer (median over seeds)
with open(os.path.join(OUT, 'summary.md'), 'w') as fh:
    fh.write('# Summary: median over seeds by config and layer (bits)\n\n')
    for cfg in sorted(set(r['cfg'] for r in rows), key=lambda c: [int(v) for v in c.split('x')]):
        rs = [r for r in rows if r['cfg'] == cfg]
        fh.write(f'## {cfg}\n\n| ' + ' | '.join(cols) + ' |\n|' + '---|' * len(cols) + '\n')
        for l in sorted(set(r['l'] for r in rs), reverse=True):
            rl = [r for r in rs if r['l'] == l]
            vals = []
            for c in cols:
                if c == 'l':
                    vals.append(str(l))
                    continue
                xs = [r.get(c) for r in rl if r.get(c) is not None]
                if xs and isinstance(xs[0], bool):
                    vals.append(f'{sum(xs)}/{len(xs)}')
                else:
                    vals.append(f3(med(xs)))
            fh.write('| ' + ' | '.join(vals) + ' |\n')
        fh.write('\n')
    fh.write('## Registered predictions\n\n')
    for k, v in pred.items():
        tag = ('HIT' if v['hit'] else 'MISS') + (' (provisional: incomplete data)' if v.get('provisional') else '')
        fh.write(f'- {k}: {tag} {json.dumps({a: b for a, b in v.items() if a not in ("hit", "provisional")})}\n')
    fh.write('\n## PREREG section 6: certified all the way to the input (per config and chain)\n\n')
    for k, v in checks['certified_all_the_way'].items():
        fh.write(f"- {k}: {'YES' if v['verdict'] else 'NO'} (steps certified on >= 2 seeds: {v['certified_steps']}; "
                 f"carries >= 80% of I* at every layer on >= 2 seeds: {v['carries_80pct']}; complete: {v['complete']})\n")
    fh.write(f"\nTruth monotonicity violations (I*_l > I*_(l+1) + 0.01 + 3 SE): {checks['truth_monotone_violations']}\n")
print(json.dumps(pred, indent=1))
print(json.dumps(checks, indent=1))
