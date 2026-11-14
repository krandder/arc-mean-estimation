"""Does the radial part of E|h1 - h2|^2 have an infinite mean (heavy radius tail x radius ratio)? n = 64, R = 2."""
import sys, numpy as np, time
sys.path.insert(0, 'lib')
import gc2
n = 64
P = 20000
rng = np.random.default_rng(3)
Q0 = gc2.sample_Q_stationary(n, P, rng)
G = gc2.init_identical(Q0, 2)
t0 = time.time()
for t in range(8 * n):
    G = gc2.step(G, n, rng)
d = gc2.diffs(G, n)
q = d['Q'] / n
ell2 = d['ell'] ** 2
ang = 2 * n * d['Q'] * d['delta']
rad = n * d['Q'] * ell2
print('time %.0fs' % (time.time() - t0))
for lo, hi in [(0, 0.3), (0.3, 0.6), (0.6, 1.2), (1.2, 2.5), (2.5, 5), (5, 10), (10, 1e9)]:
    m = (q >= lo) & (q < hi)
    if m.sum() > 20:
        print('q in [%g,%g): N=%d  E ell^2 n^(2/3)=%.3f  E delta n^(2/3)=%.3f  radial part/n=%.3f  angular part/n=%.3f' % (
            lo, hi, m.sum(), ell2[m].mean() * n ** (2 / 3), d['delta'][m].mean() * n ** (2 / 3), rad[m].mean() / n,
            ang[m].mean() / n))
h = d['h'] / n
order = np.argsort(q)
print('share of E|h1-h2|^2 from the top 1%% of q: %.3f, top 0.1%%: %.3f' % (
    h[order[-P // 100:]].sum() / h.sum(), h[order[-P // 1000:]].sum() / h.sum()))
print('share of radial part in E|h1-h2|^2: %.3f' % (rad.sum() / (rad.sum() + ang.sum())))
