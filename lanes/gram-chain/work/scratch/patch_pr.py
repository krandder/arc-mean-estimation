"""Patch partB.py's pr mode to the R = 10 four-future design (22:10Z, before any pr run)."""
p = '/home/agent/workspaces/mats/work/gram-chain/scratch/partB.py'
s = open(p).read()
start = s.index("elif mode == 'pr':")
end = s.index("elif mode == 'pert':")
new = '''elif mode == 'pr':
    # Fixed 22:10Z before any pr run (deviation logged): the registered R = 8 design gave all four pasts one shared future
    # per copy set, which biases the closed estimator (future-noise covariance between the two past pairs). Correct
    # design, R = 10: replicas (past, future) = (P1,F1) (P2,F1) (P1,F2) (P2,F2) (P3,F3) (P4,F3) (P3,F4) (P4,F4) (P3,F1)
    # (P4,F1). Closed: |g1-g2|^2 <- x(01;23), |g3-g4|^2 <- x(45;67), ((g1-g2).(g3-g4))^2 <- x(01;45) x(23;67), four
    # independent futures. Total (P1..P4 under F1): replicas 0, 1, 8, 9.
    P = a.P or (4000 if n <= 64 else (2000 if n <= 256 else 600))
    tmax = a.tmax or min(4 * n, 256)
    Q0 = gc2.sample_Q_stationary(n, P, rng)
    G4 = gc2.init_identical(Q0, 4)
    for _ in range(6 * n):
        G4 = gc2.step(G4, n, rng)
    pm = [0, 1, 0, 1, 2, 3, 2, 3, 2, 3]
    G = G4[:, pm][:, :, pm].copy()
    lab = np.array([0, 0, 1, 1, 2, 2, 3, 3, 0, 0])
    grid = set(tgrid(tmax))
    rows = []
    for t in range(1, tmax + 1):
        if t in grid:
            Cc, _ = out_dirs(G, list(range(10)))
            x = lambda p, q: Cc[:, p[0], q[0]] - Cc[:, p[0], q[1]] - Cc[:, p[1], q[0]] + Cc[:, p[1], q[1]]
            p01, p23, p45, p67, p89 = (0, 1), (2, 3), (4, 5), (6, 7), (8, 9)
            t11, t22, t12 = x(p01, p01), x(p89, p89), x(p01, p89)
            c1, c2 = x(p01, p23), x(p45, p67)
            d1, d2 = x(p01, p45), x(p23, p67)
            num_tot, den_tot = np.mean(t11 * t22), np.mean(t12 ** 2)
            num_cl, den_cl = np.mean(c1 * c2), np.mean(d1 * d2)
            B = 100
            idx = rng.integers(0, P, (B, P))
            rows.append(dict(t=t, PR_tot=float(num_tot / den_tot), PR_tot_rom=float(np.mean(t11) ** 2 / den_tot),
                             PR_closed=float(num_cl / den_cl) if den_cl > 0 else None,
                             trC_closed=float(np.mean(c1) / 2), trC_tot=float(np.mean(t11) / 2),
                             PR_tot_se=float(np.std([np.mean(t11[i] * t22[i]) / np.mean(t12[i] ** 2) for i in idx])),
                             PR_closed_se=float(np.std([np.mean(c1[i] * c2[i]) / np.mean(d1[i] * d2[i]) for i in idx]))))
            print(rows[-1], '%.0fs' % (time.time() - t0), flush=True)
        G = gc2.step(G, n, rng, labels=lab)
    res.update(P=P, rows=rows, design='R10 four futures')
'''
s = s[:start] + new + s[end:]
open(p, 'w').write(s)
print('patched')
