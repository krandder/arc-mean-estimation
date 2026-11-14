"""Dev test of gate counts and N_>=2 (dev nets only)."""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel, gates, accounting as acc
rng = np.random.default_rng(99)
mode = sys.argv[1]
out = []
if mode == 'input':
    n, L, seed, ls = 128, 32, 9102, [8, 16, 24, 31]
    Ws = rel.input_weights(seed, n, L)
    cases = [(l, rel.Future(Ws[l:], 0.0), rel.input_cloud(Ws, l, 8192, rng)[0]) for l in ls]
else:
    n, seed, ss = 64, 9202, [3, 15]
    cl = rel.stationary_clouds(seed, n, ss, 8192, rng, chunk=8192)
    cases = [(s, rel.stationary_future(seed, n, s), cl[s]) for s in ss]
for lab, fut, X in cases:
    t0 = time.time()
    fr = rel.gaussian_frame(X[:4096])
    V = rel.v_l(fut, *rel.gaussian_sample(fr, 2048, rng)[:1], rel.gaussian_sample(fr, 2048, rng)[0], rng)
    gc = gates.gate_count(fut, fr, 2048, rng)
    nl = gates.nonlinear_part_counts(fut, fr, 2048, rng, acc.kgrid(fut.n))
    Vl = V[0]
    def Gneed(curve, eps):
        for G in sorted(curve, key=int):
            if curve[G][0] <= eps * Vl:
                return int(G)
    def Nneed(curve, eps):
        for k in sorted(curve, key=int):
            if curve[k][2] <= eps * Vl:
                return int(k)
    print(mode, lab, 't', fut.t, 'V %.4g' % Vl, 'V1/V %.3f' % (nl['V1'][0] / Vl), 'total gates', gc['total_gates'],
          'mean flips vs m %.0f' % gc['mean_flips_vs_m'],
          'G_imp(.1,.01)', [Gneed(gc['importance'], e) for e in (0.1, 0.01)],
          'G_mar(.1,.01)', [Gneed(gc['margin'], e) for e in (0.1, 0.01)],
          'N>=2(.1,.01,.001)', [Nneed(nl['nlAS'], e) for e in (0.1, 0.01, 0.001)],
          'Vnl(g-g_empty)/V %.2f' % (gc['importance']['0'][0] / Vl), '[%.0fs]' % (time.time() - t0), flush=True)
    out.append(dict(lab=lab, t=fut.t, V=V, gc=gc, nl=nl))
json.dump(out, open(f'/home/agent/workspaces/mats/work/relevance/runs/dev_gates_{mode}.json', 'w'), default=float)
