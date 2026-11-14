"""Patch gpu_src/lib/vrlib.py: model and init around the analytic reference anchor (aligned with the sibling lane's
phase-1 design): gain = water-filled analytic gain (capped at SNR 256) + learned correction; prior on the standardised
code with a unit lower-triangular map; init modes ref / outpca / refu / random; Jacobian statistics G = E[J^T J]."""
import sys

P = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/lib/vrlib.py'
src = open(P).read()
i0 = src.index('class VRCode(nn.Module):')
i1 = src.index('class Frames:')
new_mid = open('/home/agent/workspaces/mats/work/bit-accounting-arc/scratch/vr_model_v2.py.txt').read()
src = src[:i0] + new_mid + src[i1:]
a = """    out = [(model.gamma, 1, model.anch_t), (model.p_logit, 1, model.anch_t), (model.p_mean, 1, model.anch_t),
           (model.p_lsd, 1, model.anch_t), (model.dec.film, 2, model.anch_t)]"""
b = """    out = [(model.c, 1, model.anch_t), (model.p_logit, 1, model.anch_t), (model.p_mean, 1, model.anch_t),
           (model.p_lsd, 1, model.anch_t), (model.dec.film, 2, model.anch_t)]
    if model.tri:
        out.append((model.Ltri, 1, model.anch_t))"""
assert a in src
src = src.replace(a, b)
a = """        g = model.gains(hat(torch.full((M, 1), float(tv), device=DEV), model.anch_t)).view(M, K)"""
b = """        tt = torch.full((M, 1), float(tv), device=DEV)
        g = model.gains(tt, hat(tt, model.anch_t)).view(M, K)"""
assert a in src
src = src.replace(a, b)
assert "opt = torch.optim.Adam(groups)" in src
src = src.replace("opt = torch.optim.Adam(groups)", "opt = torch.optim.Adam(groups, betas=(0.9, 0.99))")
open(P, 'w').write(src)
print('patched', file=sys.stderr)
