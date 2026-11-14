"""Equivalence of the tiled k3_flat_stats (lib/au.py, after the Part 1 hash) with the frozen untiled version
(frozen/part1/au.py), plus timing. Run: OMP_NUM_THREADS=1 nice -n 19 python tests/test_tiled.py"""
import importlib.util, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
import au  # noqa: E402
spec = importlib.util.spec_from_file_location('au_frozen', os.path.join(HERE, '..', 'frozen', 'part1', 'au.py'))
auf = importlib.util.module_from_spec(spec); spec.loader.exec_module(auf)
rng = np.random.default_rng(11)
n, N, r = 96, 1 << 13, 6
U = np.linalg.qr(rng.standard_normal((n, r)))[0]
E = (rng.chisquare(1, size=(N, r)) - 1) / math.sqrt(2)
X = rng.standard_normal((N, n)) + 1.3 * E @ U.T
ks = (1, 2, 4, 8, 16, 32)
t0 = time.time(); a = au.k3_flat_stats(X, np.zeros(n), ks=ks, tile=512); t1 = time.time()
b = auf.k3_flat_stats(X, np.zeros(n), ks=ks); t2 = time.time()
ok = True
for key in ('fro2', 'fro2_direct', 'pr', 'tr1', 'tr2', 'trK2'):
    rel = abs(a[key] - b[key]) / max(abs(b[key]), 1e-300)
    ok &= rel < 1e-9
    print(f'{key}: tiled {a[key]:.12e} frozen {b[key]:.12e} rel {rel:.1e}')
for k in ks:
    for key in ('topk_flat', 'capk'):
        rel = abs(a[key][k] - b[key][k]) / max(abs(b[key][k]), 1e-300)
        ok &= rel < 1e-9
print(f'times: tiled {t1 - t0:.2f}s frozen {t2 - t1:.2f}s')
print('ALL PASS' if ok else 'FAIL')
