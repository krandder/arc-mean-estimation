"""Export per-layer curves with their certificate status (for the arc-update lane, part B):
results/certified_curves.json = {definition, generated, cells: [{family, net, layer, cls, points: [{eps, bits,
bits_min, bits_max, n_restarts, bits_h1 (local), bits_class (local: better of the two starts)}], slopes: [{eps_hi,
eps_lo, bits_per_halving}], flags: {eps: {certificate: status}}, unchecked: [...], certified: bool, notes: [...]}]}.
A cell is certified when every certificate that applies to it passes at every reached eps; checks that did not run
for a cell (e.g. steps/capacity off the checked layers) are listed under 'unchecked', and the cell is then not
certified. Every expected cell is exported.
usage: export_curves.py <runs base> <score_v2 json> <out json>
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vrb  # noqa: E402

BASE, SCORE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
EPS = [0.5, 0.3, 0.2, 0.1, 0.05, 0.03, 0.02, 0.01, 0.005, 0.003, 0.002, 0.001]
runs, refs, idx = vrb.load(BASE)
score = json.load(open(SCORE))


def planned(fam, seed, l, cls):
    """the cells the reduced plan (PREREG A8) runs: local and output everywhere; unrestricted ARC at layers 0 and 31
    (all nets) and 8, 16, 24 (net 4000); unrestricted narrow-deep at layers 0, 8, 16, 64, 255 (all nets)."""
    if cls != 'unres':
        return True
    if fam == 'arc':
        return l in (0, 31) or (seed == 4000 and l in (8, 16, 24))
    return l in (0, 16, 64, 255)   # narrow-deep unrestricted at layer 8 cut by A18


A18_CUT_BASE = {('nd', 16), ('nd', 32), ('nd', 128)}   # local reference-start base cells cut by A18


ENV = {}
for (fam_, s_, l_, c_, v_), rr in idx.items():
    if fam_ not in ('arc', 'nd'):
        continue
    for r in rr:
        for e_ in EPS:
            if r.get('fixed_t') is not None:
                pt_ = min(r['pc'], key=lambda c_: abs(c_['t'] - r['fixed_t']))
                x = pt_['rate'] if pt_['nmse'] <= e_ else None
            else:
                x = vrb.R_lin(r['pc'], e_)
            if x is not None and ((fam_, s_, e_) not in ENV or x < ENV[(fam_, s_, e_)]):
                ENV[(fam_, s_, e_)] = x
A18 = json.load(open('results/conv_subset.json')) if os.path.exists('results/conv_subset.json') else []

def best_known_and_c7(rec, fam, seed, l, cls):
    """A20 (review r2 #6/#9, r3 #3): the lowest individual run (every restart separately) or dedicated point of the cell,
    and C7 against every dedicated variant (fixlam, fixlamlo: reference start; fixlamh1: look-ahead start)."""
    allruns = [(f"{v_}_r{r.get('restart')}" if r.get('fixed_t') is None else f"{v_}_t{r['fixed_t']:g}", v_, r)
               for (fam_, s_, l_, c_, v_), rr in idx.items() if (fam_, s_, l_, c_) == (fam, seed, l, cls) for r in rr]
    for p_ in rec['points']:
        best_ = None
        for nm_, v_, r in allruns:
            if r.get('fixed_t') is not None:
                pt_ = min(r['pc'], key=lambda c_: abs(c_['t'] - r['fixed_t']))
                x = pt_['rate'] if pt_['nmse'] <= p_['eps'] else None
            else:
                x = vrb.R_lin(r['pc'], p_['eps'])
            if x is not None and (best_ is None or x < best_[0]):
                best_ = (x, nm_)
        if best_:
            p_['bits_best_known'], p_['best_known_run'] = best_
    c7 = []
    for v_, start in (('fixlam', 'base'), ('fixlamlo', 'base'), ('fixlamh1', 'h1')):
        same = vrb.base_runs(idx, fam, seed, l, cls) if start == 'base' else idx.get((fam, seed, l, cls, 'h1'), [])
        for r in idx.get((fam, seed, l, cls, v_), []):
            pt_ = min(r['pc'], key=lambda c_: abs(c_['t'] - r['fixed_t']))
            vs = [vrb.R_lin(b['pc'], pt_['nmse']) for b in same]
            vs = [x for x in vs if x is not None]
            if not vs:
                c7.append(dict(variant=v_, t=r['fixed_t'], status='variable-rate curve does not reach its nMSE',
                               R_fixed=pt_['rate'], D_fixed=pt_['nmse']))
                continue
            m_ = sum(vs) / len(vs)
            fail = pt_['rate'] < min(vs) - max(max(vs) - min(vs), 0.03 * m_, 0.5)
            c7.append(dict(variant=v_, t=r['fixed_t'], status='fail' if fail else 'pass', R_fixed=pt_['rate'],
                           D_fixed=pt_['nmse'], R_variable_rate=m_))
    if c7:
        rec['c7'] = c7


cells = []
for fam in ('arc', 'nd'):
    for seed in vrb.SEEDS[fam]:
        for l in vrb.LAYERS[fam] + [vrb.LOUT[fam]]:
            for cls in (('local', 'unres') if l < vrb.LOUT[fam] else ('out',)):
                key = f'{fam}_s{seed}_l{l}_{cls}'
                rs = vrb.base_runs(idx, fam, seed, l, cls)
                h1 = idx.get((fam, seed, l, cls, 'h1'), []) if cls == 'local' else []
                sc = score['cells'].get(key, {})
                rec = dict(family=fam, net=seed, layer=l, cls=cls, restarts=sorted(r['restart'] for r in rs),
                           h1_restarts=sorted(r['restart'] for r in h1), points=[], slopes=[], flags={}, unchecked=[],
                           notes=[])
                if not rs and not h1:
                    cut = (fam == 'nd' and cls == 'unres' and l == 8)
                    rec.update(status=('not run (A18 cut)' if cut else
                                       ('missing (planned, not yet run)' if planned(fam, seed, l, cls)
                                        else 'not run (A8 reduced plan)')), certified=False)
                    cells.append(rec)
                    continue
                for e in EPS:
                    c = vrb.cellR(rs, e) if rs else None
                    p = dict(eps=e, n_restarts=c['n'] if c else 0)
                    if c and math.isfinite(c['mean']):
                        p.update(bits=c['mean'], bits_min=c['min'], bits_max=c['max'])
                    elif c:
                        p['status'] = 'unreached'
                    if h1:
                        h = vrb.cellR(h1, e)
                        if h and math.isfinite(h['mean']):
                            p['bits_h1'] = h['min']
                    if cls == 'local':
                        v = [x for x in (p.get('bits'), p.get('bits_h1')) if x is not None]
                        if v:
                            p['bits_class'] = min(v)
                    rec['points'].append(p)
                    fl = sc.get('eps', {}).get(str(e), {}).get('flags', {})
                    if fl:
                        rec['flags'][str(e)] = fl
                if not rs:
                    # only the 'h1' start has run (its base cell is pending or not planned): its curve, uncertified
                    for a, b in zip(EPS, EPS[1:]):
                        pa = next(p for p in rec['points'] if p['eps'] == a)
                        pb = next(p for p in rec['points'] if p['eps'] == b)
                        s = vrb.slope(pa.get('bits_h1'), pb.get('bits_h1'), a, b)
                        if s is not None:
                            rec['slopes'].append(dict(eps_hi=a, eps_lo=b, bits_per_halving=s, start='h1'))
                    best_known_and_c7(rec, fam, seed, l, cls)
                    rec.update(status=("h1 start only (reference-start base cut by A18)" if (fam, l) in A18_CUT_BASE
                                       else "h1 start only (reference-start base pending)"), certified=False,
                               unchecked=['base (reference start)', 'C3_r2', 'C3_steps2', 'C3_cap2', 'C6'])
                    cells.append(rec)
                    continue
                for a, b in zip(EPS, EPS[1:]):
                    pa = next(p for p in rec['points'] if p['eps'] == a)
                    pb = next(p for p in rec['points'] if p['eps'] == b)
                    s = vrb.slope(pa.get('bits'), pb.get('bits'), a, b)
                    if s is not None:
                        rec['slopes'].append(dict(eps_hi=a, eps_lo=b, bits_per_halving=s))
                bad = sorted({f'{k}={v}' for fl in rec['flags'].values() for k, v in fl.items()
                              if v not in ('pass',) and not v.endswith('missing')})
                unchecked = sorted({k for fl in rec['flags'].values() for k, v in fl.items() if v.endswith('missing')})
                needed = ['C3_r2', 'C3_steps2', 'C3_cap2'] + (['C6'] if cls != 'out' else ['C2']) + \
                    (['C1'] if cls == 'unres' else [])
                have = {k for fl in rec['flags'].values() for k in fl}
                unchecked += [k for k in needed if k not in have]
                # C3 by proxy: the certificate net of the family (ARC 4000; narrow-deep: every net) at the same layer
                proxy = []
                cert_net = 4000 if fam == 'arc' else seed
                if seed != cert_net:
                    pc = score['cells'].get(f'{fam}_s{cert_net}_l{l}_{cls}', {}).get('eps', {})
                    for k in [u for u in unchecked if u.startswith('C3_')]:
                        st = [e_.get('flags', {}).get(k) for e_ in pc.values()]
                        st = [x for x in st if x in ('pass', 'fail')]
                        if st and all(x == 'pass' for x in st):
                            proxy.append(k)
                        elif st:
                            bad.append(f'{k}=fail_on_net_{cert_net}')
                rec['c3_by_proxy'] = proxy
                rec['unchecked'] = sorted(set(unchecked) - set(proxy))
                c4, c8 = sc.get('C4', {}), sc.get('C8', {})
                if c4.get('frac_below_097'):
                    rec['notes'].append(f"C4: refitted prior > 3% better at {c4['frac_below_097']:.2f} of the checked points")
                if c8.get('frac_head_below_08'):
                    rec['notes'].append(f"C8: output-space head < 0.8 x the layer-l decoder at {c8['frac_head_below_08']:.2f} "
                                        f"of the points")
                # the certificate and added runs of this cell (bits at each eps; they are not part of the base count)
                extra = {}
                r2 = [r for r in idx.get((fam, seed, l, cls, 'base'), []) if r.get('restart') == 2]
                for v in ('r2', 'steps2', 'cap2', 'steps4', 'cap2steps4', 'cap2steps8', 'cap4steps4', 'steps8',
                          'wide2steps2', 'h1s2', 'h1s4', 'h1s8', 'h1c2', 'h1lr', 'reflr', 'rndhi', 'rndmid', 'bwd', 'bwds2'):
                    rr = r2 if v == 'r2' else idx.get((fam, seed, l, cls, v), [])
                    if rr:
                        extra[v] = [dict(eps=e, bits=(lambda c: c['mean'] if c and math.isfinite(c['mean']) else None)(
                            vrb.cellR(rr, e))) for e in EPS]
                if extra:
                    rec['extra_runs'] = extra
                best_known_and_c7(rec, fam, seed, l, cls)
                # A19/A20 consistency: unrestricted and output cells against the net's best-known envelope
                if cls in ('unres', 'out'):
                    for p_ in rec['points']:
                        env_ = ENV.get((fam, seed, p_['eps']))
                        x = p_.get('bits')
                        if env_ and x is not None and x > env_ * 1.03 and x - env_ > 0.5:   # C3's tolerance
                            p_['consistency'] = f'{100 * (x / env_ - 1):.0f}% above the best-known envelope of the net'
                # A18 convergence verdicts (subset cells) and C7 (dedicated models)
                if fam == 'arc' and seed == 4000:
                    rec['a18'] = [dict(eps=q['eps'], verdict=q['verdict'], lowest=q['lowest'], run=q['run'])
                                  for q in A18 if q['layer'] == l and q['cls'] == cls]

                cons = [p_['consistency'] for p_ in rec['points'] if p_.get('consistency')]
                if cons:
                    rec['notes'].append('consistency (A19): ' + cons[0])
                c7f = [c_ for c_ in rec.get('c7', []) if c_.get('status') == 'fail']
                if c7f:
                    bad.append('C7=fail')
                rec['unchecked'] = sorted(set(rec['unchecked']) | set(f'{k} (only on net {cert_net})' for k in proxy))
                rec['failed'] = sorted(set(bad))
                rec['certified'] = (not bad) and (not rec['unchecked']) and (not rec['notes'])
                rec['status'] = ('flagged' if bad else ('certified' if rec['certified'] else 'not fully checked'))
                cells.append(rec)
json.dump(dict(generated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               definition=('bits = mean over training restarts 0-1 of the held-out rate (trained prior; bits per sample, an '
                           'upper bound on the information the code carries) at which the cell reaches output nMSE eps, '
                           'linear interpolation in nMSE between evaluated points (achievable by time-sharing); '
                           'slope = bits per halving of the output RMS error; flags = certificate statuses (PREREG P1, '
                           'A4 rules); certified = every applicable certificate ran and passed. Local cells: bits = the '
                           'reference start (base), bits_h1 = the one-layer look-ahead start (A3/A7/A10), bits_class = '
                           'the better of the two (the count to use; an upper bound for the class). Status "h1 start only" '
                           '= the base cell has not run; "not run (A8 reduced plan)" = outside the reduced plan. Base '
                           'restarts: 0-1 at ARC layers 0 (unrestricted), 31 and the output, narrow-deep everywhere; '
                           'restart 0 at the other ARC cells (A8). extra_runs: the certificate and added runs of a cell (restart 2, '
                           '2x/4x steps, 2x depth, depth 6 with 4x steps, 10x encoder learning rate), bits at each eps; '
                           'they show how far the base count may still fall; bits_best_known = the lowest bits over every run of the '
                           'cell (base, both starts, extra runs), the tightest upper bound found.'),
               cells=cells), open(OUT, 'w'), indent=1)
from collections import Counter  # noqa: E402
print(len(cells), 'cells', Counter(c['status'] for c in cells), '->', OUT)
