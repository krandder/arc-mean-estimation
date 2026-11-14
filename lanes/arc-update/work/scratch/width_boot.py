"""Descriptive uncertainty for the Amendment 4 width exponents (not a registered statistic): bootstrap over nets within
each width (2000 resamples) of p = minus the LS slope of ln(median) on ln n over n = 64, 128, 256; and the same
exponents with the annealed normalisation sum_nets |b|^2 / sum_nets V instead of medians of per-net nMSE."""
import json, os
import numpy as np
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
SE = {64: range(300, 308), 128: range(300, 308), 256: range(200, 205)}
rng = np.random.default_rng(12345)
data = {}
for n, seeds in SE.items():
    L = n // 8; mids = sorted({n // 32, n // 16, 3 * n // 32}); rows = []
    for s in seeds:
        d = json.load(open(os.path.join(RUNS, f'width_n{n}_L{L}_s{s}.json')))
        R = {r['l']: r for r in d['rows']}
        rows.append((d['V'], R[1]['gauss'], R[1]['radgauss'], np.mean([R[l]['radgauss'] for l in mids])))
    data[n] = np.array(rows)
ns = np.log(np.array([64, 128, 256.0]))
for j, name in ((1, 'G1'), (2, 'F1'), (3, 'Zm')):
    med = [np.median(data[n][:, j]) for n in SE]
    p = -np.polyfit(ns, np.log(med), 1)[0]
    boots = []
    for _ in range(2000):
        m = [np.median(data[n][rng.integers(0, len(data[n]), len(data[n])), j]) for n in SE]
        if min(m) > 0:
            boots.append(-np.polyfit(ns, np.log(m), 1)[0])
    ann = [np.sum(data[n][:, j] * data[n][:, 0]) / np.sum(data[n][:, 0]) for n in SE]
    pa = -np.polyfit(ns, np.log(ann), 1)[0] if min(ann) > 0 else float('nan')
    print(f'{name}: p(median) = {p:.2f}, bootstrap 95% [{np.percentile(boots, 2.5):.2f}, {np.percentile(boots, 97.5):.2f}]'
          f'; annealed values {["%.2e" % a for a in ann]}, p(annealed) = {pa:.2f}')

# Full-recursion (Amendment 6, rank transport) radial and Gaussian errors: same descriptive bootstrap and annealed ratio.
for model in ('radgauss', 'gauss'):
    d2 = {}
    for n, seeds in SE.items():
        L = n // 8
        d2[n] = np.array([(json.load(open(os.path.join(RUNS, f'ipr2_n{n}_L{L}_s{s}.json')))['V'],
                           json.load(open(os.path.join(RUNS, f'ipr2_n{n}_L{L}_s{s}.json')))['models'][model]['b2'])
                          for s in seeds])
    med = [np.median(d2[n][:, 1]) for n in SE]
    p = -np.polyfit(ns, np.log(med), 1)[0]
    boots = []
    for _ in range(2000):
        m = [np.median(d2[n][rng.integers(0, len(d2[n]), len(d2[n])), 1]) for n in SE]
        if min(m) > 0:
            boots.append(-np.polyfit(ns, np.log(m), 1)[0])
    ann = [np.sum(d2[n][:, 1] * d2[n][:, 0]) / np.sum(d2[n][:, 0]) for n in SE]
    pa = -np.polyfit(ns, np.log(ann), 1)[0]
    print(f'IPR2 {model}: p(median) = {p:.2f}, bootstrap 95% [{np.percentile(boots, 2.5):.2f}, '
          f'{np.percentile(boots, 97.5):.2f}]; annealed {["%.2e" % a for a in ann]}, p(annealed) = {pa:.2f}')
