"""Patch vrlib.py: (1) an output-space head on the (detached) code, trained jointly with its own normalised loss: its
nMSE is the centroid test (free output reconstruction E[a | z] estimate) and its output is the target of (2) an
evaluation-time preimage refinement of the decoded state: Adam on the whitened state minimising |g_l(h) - a_head|^2
from the decoder's proposal (an unrestricted decoder may invert the future numerically; FORMAL 1.2's construction).
The refined reconstruction is reported beside the plain one; both are decoders of the same code."""
P = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/lib/vrlib.py'
src = open(P).read()

# --- model: head
a = """        self.Blin = nn.Parameter(init['B'])                                       # (M, K, n)
"""
b = """        self.Blin = nn.Parameter(init['B'])                                       # (M, K, n)
        self.has_head = cls != 'out'
        if self.has_head:                         # output-space head on the detached code (PCA-whitened a)
            self.head = FiLMMLP(M, K, n, max(256, W // 2), 2, Jt)
            self.Bhead = nn.Parameter(init['Bhead'])                              # (M, K, n)
"""
assert a in src
src = src.replace(a, b)
a = """        yhat = self.dec(zt, phi) + torch.matmul(zt, self.Blin.unsqueeze(1))
        return yhat, rate, dict(z=z, nu=nu, g=g, rate_k=rate_k)"""
b = """        yhat = self.dec(zt, phi) + torch.matmul(zt, self.Blin.unsqueeze(1))
        ex = dict(z=z, nu=nu, g=g, rate_k=rate_k)
        if self.has_head:
            ztd = zt.detach()
            ex['xa_head'] = self.head(ztd, phi) + torch.matmul(ztd, self.Bhead.unsqueeze(1))
        return yhat, rate, ex"""
assert a in src
src = src.replace(a, b)

# --- init: Bhead
a = """        d.update(B=B, bias=bias, Plin=Plin, ev=ev)
        per.append(d)"""
b = """        Bh = np.zeros((K, n))
        if mode == 'outpca':
            Bh[:kk, :kk] = np.eye(kk)             # z~ ~ PCA-whitened a: the exact linear output decoder
        d.update(B=B, bias=bias, Plin=Plin, ev=ev, Bhead=Bh)
        per.append(d)"""
assert a in src
src = src.replace(a, b)
a = """    init = dict(B=t('B'), dec_bias=t('bias'), Plin=t('Plin'), ev=t('ev'), V=t('V'), mode=mode)"""
b = """    init = dict(B=t('B'), dec_bias=t('bias'), Plin=t('Plin'), ev=t('ev'), V=t('V'), mode=mode, Bhead=t('Bhead'))"""
assert a in src
src = src.replace(a, b)

# --- frames: inverse PCA map
a = """    def pca_a(self, a):"""
b = """    def from_pca_a(self, xa):
        return self.ma + torch.bmm(xa, self.Pa_inv)

    def pca_a(self, a):"""
assert a in src
src = src.replace(a, b)
a = """        self.V = T(lambda s: np.array(s['V']))"""
b = """        self.V = T(lambda s: np.array(s['V']))
        self.Pa_inv = T(lambda s: np.sqrt(np.maximum(s['a']['evals'], 0.0))[:, None] * s['a']['U'].T)"""
assert a in src
src = src.replace(a, b)

# --- training: head loss
a = """        yhat, rate, _ = model(y.view(M, G, Bg, -1), xa.view(M, G, Bg, -1), t, gen)"""
b = """        yhat, rate, ex = model(y.view(M, G, Bg, -1), xa.view(M, G, Bg, -1), t, gen)"""
assert a in src
src = src.replace(a, b)
a = """        loss = (Lg / norm).sum() / G"""
b = """        loss = (Lg / norm).sum() / G
        if model.has_head:
            ahd = fr.from_pca_a(ex['xa_head'].reshape(M, B, -1))
            Dh = (((ahd - a) ** 2).sum(-1) / fr.V.view(M, 1)).view(M, G, Bg).mean(-1)
            with torch.no_grad():
                curh = Hbar.gather(1, bi)
                normh = torch.where(torch.isnan(curh), Dh.detach(), curh).clamp(min=1e-7)
            loss = loss + (Dh / normh).sum() / G"""
assert a in src
src = src.replace(a, b)
a = """            Lbar = torch.where(cnts > 0, new, Lbar)"""
b = """            Lbar = torch.where(cnts > 0, new, Lbar)
            if model.has_head:
                sh = torch.zeros(M, nbins, device=DEV).scatter_add_(1, bi, Dh.detach()) / cnts.clamp(min=1)
                Hbar = torch.where(cnts > 0, torch.where(torch.isnan(Hbar), sh, 0.95 * Hbar + 0.05 * sh), Hbar)"""
assert a in src
src = src.replace(a, b)
a = """    Lbar = torch.full((M, nbins), float('nan'), device=DEV)"""
b = """    Lbar = torch.full((M, nbins), float('nan'), device=DEV)
    Hbar = torch.full((M, nbins), float('nan'), device=DEV)"""
assert a in src
src = src.replace(a, b)

# --- evaluation: head nMSE and refinement
a = """def evaluate(model, bnet, fr, l, t_grid, P, seeds, chunk=4096, refit_every=1, tc=True):"""
b = """def refine_states(bnet, fr, l, yh0, a_tgt, steps=150, lr0=3e-2, lr1=3e-4):
    \"\"\"Preimage refinement: Adam on the whitened state y (h = m + y T) minimising |g_l(h) - a_tgt|^2, from yh0.\"\"\"
    y = yh0.clone().requires_grad_(True)
    opt = torch.optim.Adam([y], lr=lr0)
    for s in range(steps):
        for pg in opt.param_groups:
            pg['lr'] = lr1 + (lr0 - lr1) * 0.5 * (1 + math.cos(math.pi * s / steps))
        with torch.enable_grad():
            ah = bnet.run(fr.unwhite(y), l)
            loss = ((ah - a_tgt) ** 2).sum()
            opt.zero_grad(set_to_none=True)
            loss.backward()
        opt.step()
    return y.detach()


def evaluate(model, bnet, fr, l, t_grid, P, seeds, chunk=4096, refit_every=1, tc=True, refine_every=0, P_ref=8192,
             ref_steps=150):"""
assert a in src
src = src.replace(a, b)
a = """        rates, Ds, zs = [], [], []
        rk_sum = torch.zeros(M, K, device=DEV, dtype=torch.float64)"""
b = """        rates, Ds, zs, Dhs, yhs, ahs = [], [], [], [], [], []
        rk_sum = torch.zeros(M, K, device=DEV, dtype=torch.float64)"""
assert a in src
src = src.replace(a, b)
a = """            rk_sum += ex['rate_k'].view(M, Bc, K).double().sum(1)
        D = torch.cat(Ds, 1).double()"""
b = """            rk_sum += ex['rate_k'].view(M, Bc, K).double().sum(1)
            if model.has_head:
                ahd = fr.from_pca_a(ex['xa_head'].view(M, Bc, -1))
                if bnet.act == 'relu':
                    ahd = torch.relu(ahd)
                Dhs.append(((ahd - ac) ** 2).sum(-1) / V)
                if c0 < P_ref:
                    yhs.append(yhat.view(M, Bc, -1))
                    ahs.append(ahd)
        D = torch.cat(Ds, 1).double()"""
assert a in src
src = src.replace(a, b)
a = """            if ti % refit_every == 0 or ti == len(t_grid) - 1:
                rec.update(refit_rates(Z[m], g[m], RK[m], tc=tc))
                rec['rate_refit'] = rec['rate_refit_tri']"""
b = """            if model.has_head:
                Dh = torch.cat(Dhs, 1).double()
                rec['nmse_head'] = float(Dh[m].mean())
            if do_ref:
                rec['nmse_refined'] = float(Dref[m].mean())
                rec['nmse_plain_on_refset'] = float(D[m, :Dref.shape[1]].mean())
                rec['refine_P'] = int(Dref.shape[1])
            if ti % refit_every == 0 or ti == len(t_grid) - 1:
                rec.update(refit_rates(Z[m], g[m], RK[m], tc=tc))
                rec['rate_refit'] = rec['rate_refit_tri']"""
assert a in src
src = src.replace(a, b)
a = """        tt = torch.full((M, 1), float(tv), device=DEV)
        g = model.gains(tt, hat(tt, model.anch_t)).view(M, K)
        for m in range(M):"""
b = """        tt = torch.full((M, 1), float(tv), device=DEV)
        g = model.gains(tt, hat(tt, model.anch_t)).view(M, K)
        do_ref = bool(model.has_head and l < L and refine_every and (ti % refine_every == 0 or ti == len(t_grid) - 1))
        if do_ref:
            y0 = torch.cat(yhs, 1)[:, :P_ref].contiguous()
            at = torch.cat(ahs, 1)[:, :P_ref].contiguous()
            yr = refine_states(bnet, fr, l, y0, at, steps=ref_steps)
            with torch.no_grad():
                dr = bnet.run(fr.unwhite(yr), l) - a[:, :y0.shape[1]]
                Dref = ((dr * dr).sum(-1) / V).double()
        for m in range(M):"""
assert a in src
src = src.replace(a, b)
open(P, 'w').write(src)
print('ok')
