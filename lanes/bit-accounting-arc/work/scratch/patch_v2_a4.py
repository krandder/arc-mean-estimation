"""Patch vrlib.py (amendment A4, review r1 findings 1 and 13):
1. jac_stats: the Jacobian is taken through the data-span frame S^{1/2} (not the full-rank decoder frame T), so G and
   E[J] live on the data's span and the anchor/reference coordinates have unit variance (the null directions of dead
   units carried spurious future-weight: dev nd 111 l = 64 leading coordinate variance 0.0049 instead of 1).
2. Gradient clipping: the output head (trained on detached codes) is clipped separately, so its gradients cannot shrink
   the main model's updates through a shared norm."""
P = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/lib/vrlib.py'
src = open(P).read()


def rep(a, b):
    global src
    assert src.count(a) == 1, (a[:60], src.count(a))
    src = src.replace(a, b)


rep("""    T = torch.tensor(fh['T'], dtype=DT, device=DEV)
    Sm = torch.tensor(fh['Sm12'], dtype=DT, device=DEV)""", """    T = torch.tensor(fh['S12'], dtype=DT, device=DEV)      # data-span frame (A4): J vanishes off the data's span
    Sm = torch.tensor(fh['Sm12'], dtype=DT, device=DEV)""")
rep("""        with torch.no_grad():
            sq = torch.zeros(M, device=DEV)
            for p in model.parameters():
                if p.grad is not None:
                    sq += p.grad.pow(2).flatten(1).sum(1)
            fac = (clip / (sq.sqrt() + 1e-12)).clamp(max=1.0)
            for p in model.parameters():
                if p.grad is not None:
                    p.grad.mul_(fac.view(M, *([1] * (p.grad.dim() - 1))))""", """        with torch.no_grad():
            for grp in clip_groups:                      # main model and output head clipped separately (A4)
                sq = torch.zeros(M, device=DEV)
                for p in grp:
                    if p.grad is not None:
                        sq += p.grad.pow(2).flatten(1).sum(1)
                fac = (clip / (sq.sqrt() + 1e-12)).clamp(max=1.0)
                for p in grp:
                    if p.grad is not None:
                        p.grad.mul_(fac.view(M, *([1] * (p.grad.dim() - 1))))""")
rep("""    gnet = GraphedNet(bnet, l, M, B) if (graphs and DEV == 'cuda') else None""", """    gnet = GraphedNet(bnet, l, M, B) if (graphs and DEV == 'cuda') else None
    head_ids = {id(p) for nm, p in model.named_parameters() if nm.startswith('head.') or nm == 'Bhead'}
    clip_groups = [[p for p in model.parameters() if id(p) not in head_ids],
                   [p for p in model.parameters() if id(p) in head_ids]]""")
open(P, 'w').write(src)
print('ok')
