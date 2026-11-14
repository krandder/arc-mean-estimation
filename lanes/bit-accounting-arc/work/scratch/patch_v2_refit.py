"""Patch evaluate()'s refit block: three fresh priors on held-out codes (cross-fitted halves):
refit_tri (the trained family: unit lower-triangular map from the LDL factor of the held-out covariance of the
standardised code, then a factorised 8-mixture), refit_fact (factorised mixture, no map), refit_gauss (full-covariance
Gaussian on z); copula total correlation left after the triangular map."""
P = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/lib/vrlib.py'
src = open(P).read()
i0 = src.index("            if ti % refit_every == 0 or ti == len(t_grid) - 1:")
i1 = src.index("            out[m].append(rec)")
new = '''            if ti % refit_every == 0 or ti == len(t_grid) - 1:
                rec.update(refit_rates(Z[m], g[m], RK[m], tc=tc))
                rec['rate_refit'] = rec['rate_refit_tri']
'''
src = src[:i0] + new + src[i1:]
helper = '''

def ldl_unit(C):
    """Unit lower-triangular L with L C L^T diagonal (from the Cholesky factor of C)."""
    Ch = torch.linalg.cholesky(C)
    return torch.diag(torch.diagonal(Ch)) @ torch.linalg.inv(Ch)


def refit_rates(Zm, gm, rk, tc=True, J=8):
    """Rates (bits per sample) of fresh priors fitted on one half of the held-out codes Zm (P, K) and scored on the
    other half (both ways, averaged). gm (K,) the gains (standardisation zs = z / sqrt(1 + g^2)), rk (K,) per-latent
    trained rates (for the active set of the copula statistic)."""
    P, K = Zm.shape
    h2 = P // 2
    sd = torch.sqrt(gm * gm + 1.0)
    zs = (Zm / sd).double()
    jac = float(torch.log(sd.double()).sum())
    out = {k: [] for k in ('tri', 'fact', 'gauss', 'tc')}
    for (A_, B_) in ((zs[:h2], zs[h2:]), (zs[h2:], zs[:h2])):
        # factorised mixture on zs
        mu, var, lw = fit_mixture(A_.float(), J=J, var_floor=1e-4)
        lp = mix_logpdf(B_.float(), mu, var, lw).double().sum(-1).mean() - jac
        out['fact'].append(float((-0.5 * K * LOG2PIE - lp) / LN2))
        # unit lower-triangular map (LDL of the held-out covariance) + factorised mixture
        mA = A_.mean(0)
        CA = torch.cov((A_ - mA).T) + 1e-9 * torch.eye(K, device=A_.device, dtype=A_.dtype)
        Lu = ldl_unit(CA)
        wA, wB = (A_ - mA) @ Lu.T, (B_ - mA) @ Lu.T
        mu, var, lw = fit_mixture(wA.float(), J=J, var_floor=1e-6)
        lpB = mix_logpdf(wB.float(), mu, var, lw)
        lp = lpB.double().sum(-1).mean() - jac
        out['tri'].append(float((-0.5 * K * LOG2PIE - lp) / LN2))
        # full Gaussian on zs
        dB = B_ - mA
        sign, logdet = torch.linalg.slogdet(CA)
        quad = (dB @ torch.linalg.inv(CA) * dB).sum(-1).mean()
        lp = -0.5 * quad - 0.5 * logdet - 0.5 * K * math.log(2 * math.pi) - jac
        out['gauss'].append(float((-0.5 * K * LOG2PIE - lp) / LN2))
        act = rk > 0.01
        ka = int(act.sum())
        if tc and ka >= 2:
            u = mix_cdf(wB[:, act].float(), mu[act], var[act], lw[act]).clamp(1e-6, 1 - 1e-6)
            gq = math.sqrt(2.0) * torch.erfinv(2 * u - 1)
            Cc = torch.corrcoef(gq.T.double())
            s_, ld = torch.linalg.slogdet(Cc)
            out['tc'].append(float((-0.5 * ld - ka * (ka - 1) / (4.0 * B_.shape[0])) / LN2))
    res = dict(rate_refit_tri=float(np.mean(out['tri'])), rate_refit_fact=float(np.mean(out['fact'])),
               rate_refit_gauss=float(np.mean(out['gauss'])))
    if out['tc']:
        res['tc_copula_after_tri'] = float(np.mean(out['tc']))
    return res
'''
j = src.index("@torch.no_grad()\ndef evaluate(")
src = src[:j] + helper.lstrip('\n') + '\n\n' + src[j:]
open(P, 'w').write(src)
print('ok')
