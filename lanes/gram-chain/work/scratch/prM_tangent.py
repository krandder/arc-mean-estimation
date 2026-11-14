"""Post hoc diagnostic: participation ratio of the future's tangent sensitivity M = J^T J over t layers (stationary
state, shared future noise), from the exact tangent chain: two orthonormal tangent vectors u, v orthogonal to the state;
PR_M = E[|Ju|^2 |Jv|^2] / E[(Ju.Jv)^2] (variance-weighted, as PR_w). Compared with the free-probability value
n/(2t + 1) (frozen-gate ReLU layers) and with the Lyapunov-spectrum value coth(t/n)."""
import sys, json, math
sys.path.insert(0, '/home/agent/workspaces/mats/work/gram-chain/lib')
import numpy as np
import gc2

rng = np.random.default_rng(424242)
out = {}
for n in (16, 64, 256):
    P = 4000 if n <= 64 else 2000
    Q0 = gc2.sample_Q_stationary(n, P, rng)
    G = np.zeros((P, 3, 3))
    G[:, 0, 0] = Q0
    G[:, 1, 1] = 1.0
    G[:, 2, 2] = 1.0
    rows = []
    for t in range(1, 65):
        # one layer: hidden layers carry noise on the state; the last of the t layers is the noiseless output layer
        Gt = gc2.step(G, n, rng, Rs=1, tan_base=[0, 0], out=True)
        if t in (1, 2, 4, 8, 16, 32, 64):
            a, b, c = Gt[:, 1, 1], Gt[:, 2, 2], Gt[:, 1, 2]
            pr = float(np.mean(a * b) / np.mean(c * c))
            rows.append(dict(t=t, PR_M=pr, free=n / (2 * t + 1), lyap=1 / math.tanh(t / n)))
        G = gc2.step(G, n, rng, Rs=1, tan_base=[0, 0])
    out[n] = rows
    print(n, [(r['t'], round(r['PR_M'], 2), round(r['free'], 2), round(r['lyap'], 2)) for r in rows], flush=True)
json.dump(out, open('/home/agent/workspaces/mats/work/gram-chain/results/prM_tangent.json', 'w'), indent=1)
