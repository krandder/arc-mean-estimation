"""Patch vrlib.py (amendment A5, process/diagnostics only): the prior refits (C4 diagnostic since A4) cost ~50 s per
(model, t) for K = 256 on a shared L4 (150 EM iterations on 16384 x 256 x 8), i.e. ~20 min per model and ~2.7 h per
8-model process. Refits now run every 4th t (7 points incl. the ends), with 40 EM iterations, on the first 16384
held-out codes (8192 per half). The primary rate (the trained prior's, on all 32768 inputs) is unchanged."""
P = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/lib/vrlib.py'
src = open(P).read()


def rep(a, b):
    global src
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)


rep("""def refit_rates(Zm, gm, rk, tc=True, J=8):""", """def refit_rates(Zm, gm, rk, tc=True, J=8, iters=40, P_max=16384):""")
rep("""    P, K = Zm.shape
    h2 = P // 2
    sd = torch.sqrt(gm * gm + 1.0)""", """    Zm = Zm[:P_max]
    P, K = Zm.shape
    h2 = P // 2
    sd = torch.sqrt(gm * gm + 1.0)""")
rep("""        mu, var, lw = fit_mixture(A_.float(), J=J, var_floor=1e-4)""",
    """        mu, var, lw = fit_mixture(A_.float(), J=J, iters=iters, var_floor=1e-4)""")
rep("""        mu, var, lw = fit_mixture(wA.float(), J=J, var_floor=1e-6)""",
    """        mu, var, lw = fit_mixture(wA.float(), J=J, iters=iters, var_floor=1e-6)""")
rep("""def evaluate(model, bnet, fr, l, t_grid, P, seeds, chunk=4096, refit_every=1, tc=True, refine_every=0, P_ref=8192,""",
    """def evaluate(model, bnet, fr, l, t_grid, P, seeds, chunk=4096, refit_every=4, tc=True, refine_every=0, P_ref=8192,""")
open(P, 'w').write(src)
print('ok')
