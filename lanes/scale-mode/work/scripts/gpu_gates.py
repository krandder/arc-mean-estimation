"""PREREG Amendment 1 gates for the GPU results. usage: gpu_gates.py LANE_ROOT
Prints the gates' outcomes and, if all pass, the list of files to copy from runs/gpu into runs/."""
import glob, json, os, sys
import numpy as np

ROOT = sys.argv[1]
G = os.path.join(ROOT, 'runs', 'gpu')
D = os.path.join(ROOT, 'runs_dev')
ok = True
# 1. LV family and ARC k2/k2a on dev net 699 at 128 x 32: estimates within 1e-6 relative, identical FLOPs
g = json.load(open(os.path.join(G, 'parity_lv_au699_n128_L32.json')))
c = json.load(open(os.path.join(D, 'lv_au699_n128_L32.json')))
for arm in c['arms']:
    a = np.array(g['arms'][arm]['mean']); b = np.array(c['arms'][arm]['mean'])
    rel = float(np.abs(a - b).max() / np.abs(b).max())
    fl = (g['arms'][arm]['flops'], c['arms'][arm]['flops'])
    good = rel <= 1e-6 and fl[0] == fl[1]
    ok &= good
    print(f'lv {arm}: max rel diff {rel:.2e}, flops gpu {fl[0]:.6e} cpu {fl[1]:.6e} -> {"PASS" if good else "FAIL"}')
for v in ('k2', 'k2a'):
    a = np.array(json.load(open(os.path.join(G, f'parity_arc_au699_n128_L32_{v}.json')))['mean'])
    cj = json.load(open(os.path.join(D, f'arc_au699_n128_L32_{v}.json')))
    gj = json.load(open(os.path.join(G, f'parity_arc_au699_n128_L32_{v}.json')))
    b = np.array(cj['mean'])
    rel = float(np.abs(a - b).max() / np.abs(b).max())
    good = rel <= 1e-6 and gj['flops'] == cj['flops']
    ok &= good
    print(f'arc {v}: max rel diff {rel:.2e}, flops gpu {gj["flops"]:.6e} cpu {cj["flops"]:.6e} -> {"PASS" if good else "FAIL"}')
# 2. truth within MC noise
tg = np.load(os.path.join(G, 'parity_truth_au699_n128_L32.npz')); tc = np.load(os.path.join(D, 'truth_au699_n128_L32.npz'))
def mv(t):
    N = float(t['N']); S1 = t['S1A'][-1] + t['S1B'][-1]; S2 = t['S2A'][-1] + t['S2B'][-1]
    Y = S1 / N; return Y, S2 / N - Y ** 2, N
Yg, Vg, Ng = mv(tg); Yc, Vc, Nc = mv(tc)
stat = float(((Yg - Yc) ** 2).sum() / Vc.sum()); bound = 10 * (1 / Nc + 1 / Ng)
good = stat <= bound
ok &= good
print(f'truth: |dY|^2/trVar {stat:.2e} vs bound {bound:.2e} (expected ~{1 / Nc + 1 / Ng:.2e}) -> {"PASS" if good else "FAIL"}')
# 3. weight checksums
loc = json.load(open(os.path.join(ROOT, 'runs', 'local_checksums.json')))
for f in sorted(glob.glob(os.path.join(G, 'truth_au*.npz'))):
    tag = os.path.basename(f)[6:-4]
    cs = float(np.load(f)['checksum'])
    good = abs(cs - loc[tag]) <= 1e-9 * max(1.0, abs(loc[tag]))
    ok &= good
    print(f'checksum {tag}: gpu {cs:.10e} local {loc[tag]:.10e} -> {"PASS" if good else "FAIL"}')
print('ALL GATES PASS' if ok else 'A GATE FAILED: GPU results are reported, not scored')
if ok:
    files = [f for f in glob.glob(os.path.join(G, '*')) if not os.path.basename(f).startswith(('parity_', 'nvidia', 'versions', 'queue'))]
    print('to copy:', ' '.join(sorted(os.path.basename(f) for f in files)))
