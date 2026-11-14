"""Plain product of experts with learned, input-dependent diagonal variances (Kelvin's final fusion rule, ~19:00Z).
Toys: (1) two experts confident on DISJOINT coordinates: after NLL training on the fused prediction both ends are tight
and the means correct; (2) two IDENTICAL experts with shared errors: the learned per-expert variances grow so the fused
prediction is calibrated (fused variance ~ the true error variance)."""
import os, sys
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import lmle  # noqa: E402

torch.manual_seed(0)
DT = torch.float64
ok = True


def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + ('  ' + info if info else ''))
    ok = ok and bool(cond)


def make_bank(A1, A2):
    b = lmle.Bank(2, 2, 2, 2)
    with torch.no_grad():
        b.logpi.zero_(); b.mu.zero_(); b.Lg.copy_(torch.eye(2, dtype=DT).repeat(2, 1, 1))   # identical gates
        base = (A1 + A2) / 2
        b.B.copy_(base)
        for k, Ak in enumerate((A1, A2)):
            u_, s_, vt_ = np.linalg.svd((Ak - base).numpy())
            b.U[k].copy_(torch.as_tensor(u_ * s_)); b.V[k].copy_(torch.as_tensor(vt_.T))
        b.b.zero_(); b.logsig.zero_()
    return b


def train(bank, U, Y, steps=600):
    opt = torch.optim.Adam([bank.logsig, bank.cgate], lr=0.05)
    for _ in range(steps):
        pred, Unc, _ = lmle.LMLE.pointwise(bank, U, 'poe')
        var = torch.diagonal(Unc, dim1=-2, dim2=-1)
        nll = (((Y - pred) ** 2) / var + torch.log(var)).mean()
        opt.zero_grad(); nll.backward(); opt.step()
    with torch.no_grad():
        pred, Unc, _ = lmle.LMLE.pointwise(bank, U, 'poe')
    return pred, torch.diagonal(Unc, dim1=-2, dim2=-1)


U = torch.randn(4000, 2, dtype=DT)
# (1) disjoint: expert 1 predicts coordinate 1 exactly (coordinate 2 = 0), expert 2 the reverse; small target noise
Y = U + 0.01 * torch.randn(4000, 2, dtype=DT)
bank = make_bank(torch.diag(torch.tensor([1.0, 0.0], dtype=DT)), torch.diag(torch.tensor([0.0, 1.0], dtype=DT)))
pred, var = train(bank, U, Y)
err = float(((pred - Y) ** 2).mean(0).max())
check('disjoint: fused means correct (MSE <= 2e-4 per coordinate)', err <= 2e-4, f'{err:.2e}')
check('disjoint: both ends tight (fused variance <= 3e-4)', float(var.mean(0).max()) <= 3e-4, str(var.mean(0).numpy()))
# (2) identical experts with shared errors (target noise variance 1)
Y2 = U + torch.randn(4000, 2, dtype=DT)
bank2 = make_bank(torch.eye(2, dtype=DT), torch.eye(2, dtype=DT))
pred2, var2 = train(bank2, U, Y2)
emp = float(((pred2 - Y2) ** 2).mean())
check('identical: fused variance calibrated (within 10% of the actual squared error)', abs(float(var2.mean()) / emp - 1) < 0.1,
      f'fused var {float(var2.mean()):.3f}, actual {emp:.3f}')
with torch.no_grad():
    beta = torch.exp(bank2.log_gates(U)).mean(0)                                   # (K,) = 0.5 each here
    eff = (torch.exp(bank2.logsig) / beta[:, None] ** bank2.cgate).numpy()        # effective per-expert variance
check('identical: each expert learned effective variance ~2x the fused one', bool(np.all(eff > 1.5 * float(var2.mean()))), str(eff.round(3)))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
