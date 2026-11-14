"""Code fixes from the round-1 review (findings 7, 11, 13, 16):
- run_noisy.py: population-normalised covariances in the Gelbrich bound; unbiased cross-covariance for the memory
  share; evaluation power of every channel and the power-corrected capacity (1/2) sum log2(1 + P_i SNR_i); SE of avg.
- run_curves.py: evaluation power and power-corrected capacity for the channel models.
- smallnets.py: a helper returning (power per channel, corrected capacity) for a channel model on given inputs.
- lincodes.py: Lloyd-Max quantisers computed for every bit depth up to 12 (no uniform fallback with a wrong constant).
- rwf.py: rwf_rate returns inf for D <= 0 with a positive spectrum."""
W = '/home/agent/workspaces/mats/work/bit-accounting/'


def sub(path, old, new, count=1):
    s = open(W + path).read()
    assert s.count(old) >= 1, (path, old[:60])
    s = s.replace(old, new, count)
    open(W + path, 'w').write(s)


# smallnets: power helper
sub('gpu_src/lib/smallnets.py', """    def capacities(self):""", """    @torch.no_grad()
    def eval_power(self, h, a):
        \"\"\"Per-model, per-channel power E u_i^2 of the normalised channel inputs on (h, a) with the running statistics,
        and the power-corrected capacity (1/2) sum_i log2(1 + P_i SNR_i). Channel models only.\"\"\"
        z = self.encode(h, a)
        u = (z - self.run_mean) / torch.sqrt(self.run_var + 1e-6)
        P = (u.double() ** 2).mean(1)                                   # (M, K)
        Ci = waterfill_rows(self.eta, self.rates).double()
        snr = torch.pow(2.0, 2.0 * Ci) - 1.0
        Ceff = 0.5 * torch.log2(1.0 + P * snr).sum(1)
        return P, Ceff

    def capacities(self):""")
# run_curves: record power for gauss models
sub('gpu_src/scripts/run_curves.py', """                    cur['cross'] = {str(e): sn.crossing(rates, cur['nmse'], e) for e in EPS}""",
    """                    cur['cross'] = {str(e): sn.crossing(rates, cur['nmse'], e) for e in EPS}
                    if m.kind == 'gauss':
                        Pw, Ceff = m.eval_power(He[l][:8192], Ae[:8192])
                        cur['power_max'] = Pw.max(1).values.tolist()
                        cur['power_mean'] = Pw.mean(1).tolist()
                        cur['cap_power_corrected'] = Ceff.tolist()""")
# run_noisy: Gelbrich with population covariances
sub('gpu_src/scripts/run_noisy.py', """    mx, my = X.mean(0), Y.mean(0)
    Sx = torch.cov(X.T)
    Sy = torch.cov(Y.T)""", """    mx, my = X.mean(0), Y.mean(0)
    Xc, Yc = X - mx, Y - my
    Sx = Xc.T @ Xc / X.shape[0]          # population-normalised (the empirical coupling bound uses 1/N)
    Sy = Yc.T @ Yc / Y.shape[0]""")
# run_noisy: unbiased cross-covariance for the memory share
sub('gpu_src/scripts/run_noisy.py', """            mu = 0.5 * (a1.mean(0) + a2.mean(0))
            mem[str(l)] = float(((a1 - mu) * (a2 - mu)).sum(1).mean() / Ve)""",
    """            mem[str(l)] = float(((a1 - a1.mean(0)) * (a2 - a2.mean(0))).sum() / (a1.shape[0] - 1) / Ve)""")
# run_noisy: power and avg SE
sub('gpu_src/scripts/run_noisy.py', """                    cur['cross_crn'] = {str(e): sn.crossing(rates, cur['crn'], e) for e in EPS}""",
    """                    if avg:
                        av = torch.cat(avg, 1) / Ve
                        cur['avg_se'] = (av.std(1) / math.sqrt(av.shape[1])).tolist()
                    if m.kind == 'gauss':
                        side_p = net.g_hat(He[l][:8192], l, args.R, gev) if (cls == 'unres' and l < L) else Ae[:8192]
                        Pw, Ceff = m.eval_power(He[l][:8192], side_p)
                        cur['power_max'] = Pw.max(1).values.tolist()
                        cur['power_mean'] = Pw.mean(1).tolist()
                        cur['cap_power_corrected'] = Ceff.tolist()
                    cur['cross_crn'] = {str(e): sn.crossing(rates, cur['crn'], e) for e in EPS}""")
# lincodes: Lloyd-Max up to 12 bits
sub('lib/lincodes.py', """        if b <= 9:
            _LM[b] = _lloyd_max(b)""", """        if b <= 12:
            _LM[b] = _lloyd_max(b, grid=400001 if b > 9 else 200001)""")
# rwf: D <= 0
sub('lib/rwf.py', """def rwf_theta(lam, D):
    lam = np.sort(np.maximum(np.asarray(lam, float), 0.0))[::-1]""", """def rwf_theta(lam, D):
    lam = np.sort(np.maximum(np.asarray(lam, float), 0.0))[::-1]
    if D <= 0:
        return 0.0""")
sub('lib/rwf.py', """    th = rwf_theta(lam, D)
    if not np.isfinite(th):
        return 0.0""", """    th = rwf_theta(lam, D)
    if not np.isfinite(th):
        return 0.0
    if th <= 0:
        return float('inf') if lam.max() > 0 else 0.0""")
print('patched')
