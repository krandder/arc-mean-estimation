"""cones.first_moment against Monte Carlo (n = 4, 6) on random cones; exits nonzero on failure."""
import sys, os, time, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import cones
rs = np.random.RandomState(1); ok = True
for n in (4, 5, 6):
    X = rs.standard_normal((1 << 22, n))
    for t in range(6):
        m = rs.randint(2, 2 * n)
        # cones guaranteed nonempty: constraints chosen positive on a random direction
        v = rs.standard_normal(n); G = rs.standard_normal((m, n)); G = np.where((G @ v)[:, None] >= 0, G, -G)
        st = {}; t0 = time.time(); ex = cones.first_moment(G, st); dt = time.time() - t0
        inside = ((X @ G.T) >= 0).all(1); mc = (X * inside[:, None]).mean(0)
        se = np.sqrt((X ** 2 * inside[:, None]).mean(0) / len(X))
        z = np.max(np.abs(ex - mc) / (se + 1e-12))
        print(f'n={n} m={m} P~{inside.mean():.4f} max|exact-MC|/se={z:.2f} simplices={st.get("simplices", 0)} fails={st.get("qhull_fail", 0)} {dt:.2f}s')
        ok &= bool(z < 5)
# deterministic regression cases from review 2 (item 2)
R = np.full((4, 4), 1 - 1e-13); np.fill_diagonal(R, 1.0)
v = cones._orthant(R); print(f'near-singular equicorrelation orthant {v:.4f} (expect ~0.5)'); ok &= bool(abs(v - 0.5) < 1e-3)
v = cones.measure(np.array([[1., 0, 0], [0, 1, 0], [1, 1, 0]])); print(f'rank-deficient cone {v:.6f} (expect 0.25)'); ok &= bool(abs(v - 0.25) < 1e-6)
print('ALL PASS' if ok else 'FAILED'); sys.exit(0 if ok else 1)
