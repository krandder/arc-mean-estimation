"""Summarise structure runs: inverse gains (m x risk / V; plain MC = 1) and implied harmonic partial sums."""
import json, sys, glob, numpy as np
files = sys.argv[1:]
for f in files:
    r = json.load(open(f)); V = r['V']; Vrb = r['V_rb']; d = r.get('designs', {})
    g = lambda k: d[k]['inv_gain_mc'] if k in d else float('nan')
    rel = lambda k: g(k) / (Vrb / V)        # relative to radius-exact MC
    E12 = 1 - rel('simplex'); E2 = 1 - rel('onb'); E1 = E12 - E2
    ev = r['V_even'] / Vrb; od = r['V_odd'] / Vrb
    ev4 = rel('cross') / 2; ev6 = rel('kerdock') / 2 if 'kerdock' in d else float('nan')
    rq = r.get('rqmc', {})
    best_ml = max(r['multilevel'].values(), key=lambda v: v['gain_vs_rb'])
    print(f"{f.split('/')[-1]:34s} Vrb/V={Vrb/V:.3f} |mu|^2/V={r['mean_norm2_over_V']:.1f} | E1={E1:.2f} E2={E2:.2f} odd={od:.2f} even={ev:.2f} even>=4={ev4:.2f} even>=6={ev6:.2f} | "
          f"gain_mc: onb {1/g('onb'):.2f} simplex {1/g('simplex'):.2f} cross {1/g('cross'):.2f} kerdock {1/g('kerdock'):.2f} mub {1/g('mub'):.2f} | ML {best_ml['gain_vs_mc']:.2f}")
    line = '   rqmc gain_mc: ' + ' '.join(f"{k.replace('rqmc_rb_','')}={1/v['inv_gain_mc']:.2f}" for k, v in rq.items())
    print(line)
    det = r.get('deterministic', {})
    if det: print('   det nmse*m (std/polar): ' + ' '.join(f"{k.replace('sobol_det_','')}={v['nmse_times_m']:.2f}/{v['polar_nmse_times_m']:.2f}" for k, v in det.items()))
