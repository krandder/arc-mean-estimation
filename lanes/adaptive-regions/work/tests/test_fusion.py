"""Toy tests for the tempered product-of-experts fusion (lib/lmle.fuse_tempered), main ~18:40Z.
(1) two experts confident on DISJOINT coordinates: both ends stay tight and the means are taken from the confident
expert; (2) two identical experts: the fusion stays calibrated (variance of one expert, not half of it)."""
import os, sys
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import lmle  # noqa: E402

DT = torch.float64
ok = True


def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + ('  ' + info if info else ''))
    ok = ok and bool(cond)


beta = torch.tensor([[0.5, 0.5]], dtype=DT)
mu = torch.tensor([[[1.0, 2.0, 0.0, 0.0], [0.0, 0.0, 3.0, 4.0]]], dtype=DT)
P1 = torch.diag(torch.tensor([1e4, 1e4, 1.0, 1.0], dtype=DT)); P2 = torch.diag(torch.tensor([1.0, 1.0, 1e4, 1e4], dtype=DT))
Ri = torch.stack([P1, P2])
eta, Lam, _ = lmle.fuse_tempered(beta, Ri, mu)
m = torch.linalg.solve(Lam, eta[..., None])[..., 0][0]
var = torch.diagonal(torch.linalg.inv(Lam[0]))
check('disjoint: means from the confident expert', float((m - torch.tensor([1.0, 2.0, 3.0, 4.0], dtype=DT)).abs().max()) < 1e-3, str(m.numpy().round(4)))
check('disjoint: both ends stay tight (variance <= 1.01e-4)', float(var.max()) <= 1.01e-4, str(var.numpy()))
# normalised gPoE for comparison: inflated by ~1/beta
Lg = 0.5 * P1 + 0.5 * P2
check('(reference) normalised gPoE inflates the variance ~2x', float(torch.diagonal(torch.linalg.inv(Lg)).max()) > 1.9e-4, str(torch.diagonal(torch.linalg.inv(Lg)).numpy()))
# identical experts: calibrated
mu2 = torch.tensor([[[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]]], dtype=DT)
Ri2 = torch.stack([P1, P1])
eta, Lam, _ = lmle.fuse_tempered(beta, Ri2, mu2)
m2 = torch.linalg.solve(Lam, eta[..., None])[..., 0][0]
var2 = torch.diagonal(torch.linalg.inv(Lam[0]))
check('identical: mean exact', float((m2 - mu2[0, 0]).abs().max()) < 1e-9)
check('identical: calibrated (variance equals one expert, not half)', float((var2 - torch.diagonal(torch.linalg.inv(P1))).abs().max()) < 1e-12, str(var2.numpy()))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
