"""PREREG Amendment 2 gates for GPU run 2 (Phase 2 dev MLP 12 parity). usage: gpu_gates2.py LANE_ROOT"""
import glob, json, os, sys
import numpy as np

ROOT = sys.argv[1]
G = os.path.join(ROOT, 'runs', 'gpu2')
D = os.path.join(ROOT, 'runs_dev')
ok = True


def cmp(name, a, b, fa=None, fb=None):
    global ok
    a = np.asarray(a); b = np.asarray(b)
    rel = float(np.abs(a - b).max() / np.abs(b).max())
    good = rel <= 1e-6 and (fa is None or fa == fb)
    ok &= good
    print(f'{name}: max rel diff {rel:.2e}' + (f', flops gpu {fa:.6e} cpu {fb:.6e}' if fa is not None else '') + f' -> {"PASS" if good else "FAIL"}')


for v in ('k2', 'k2a', 'k3f'):
    g = json.load(open(os.path.join(G, f'parity_arc_p2_12_{v}.json'))); c = json.load(open(os.path.join(D, f'arc_p2_12_{v}.json')))
    cmp(f'arc {v}', g['mean'], c['mean'], g['flops'], c['flops'])
g = json.load(open(os.path.join(G, 'parity_lv_p2_12.json'))); c = json.load(open(os.path.join(D, 'lv_p2_12.json')))
for arm in c['arms']:
    cmp(f'lv {arm}', g['arms'][arm]['mean'], c['arms'][arm]['mean'], g['arms'][arm]['flops'], c['arms'][arm]['flops'])
for job in ('cov', 'sl3'):
    g = json.load(open(os.path.join(G, f'parity_{job}_p2_12.json'))); c = json.load(open(os.path.join(D, f'{job}_p2_12.json')))
    cmp(job, g['mean'], c['mean'], g['flops'], c['flops'])
g = json.load(open(os.path.join(G, 'parity_rqmc_p2_12.json'))); c = json.load(open(os.path.join(D, 'rqmc_p2_12.json')))
for rg in g['rows']:
    rc = [r for r in c['rows'] if r['m'] == rg['m']][0]
    cmp(f'rqmc m={rg["m"]}', rg['est'], rc['est'][:len(rg['est'])])
print('ALL GATES PASS' if ok else 'A GATE FAILED: GPU run 2 results are reported, not scored')
if ok:
    files = [f for f in glob.glob(os.path.join(G, '*')) if not os.path.basename(f).startswith(('parity_', 'nvidia', 'versions', 'queue'))]
    print('to copy:', ' '.join(sorted(os.path.basename(f) for f in files)))
