"""Patch vrlib.py: lambda-dependent decoder offset for the reference-anchored codes. At zero rate the linear MMSE decoder
returns the mean state m_l, whose output is not E a (deep ReLU futures); the offset frac(t) y_star + delta(t) moves the
zero-information reconstruction to the state whose output is nearest E a, by the analytic fraction of the anchor
spectrum NOT transmitted at t (0 at high budget, 1 where nothing is sent); delta anchored in t (zero at init)."""
P = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/lib/vrlib.py'
src = open(P).read()
a = """        self.Blin = nn.Parameter(init['B'])                                       # (M, K, n)
"""
b = """        self.Blin = nn.Parameter(init['B'])                                       # (M, K, n)
        self.register_buffer('ystar', init['ystar'])                              # (M, n) analytic zero-rate offset
        self.dbias = nn.Parameter(torch.zeros(M, Jt, n, device=DEV))
"""
assert a in src
src = src.replace(a, b)
a = """    def gains(self, t, phi):                  # t (M, G), phi (M, G, Jt) -> g (M, G, K)"""
b = """    def offset(self, t, phi):                 # (M, G, n): frac(t) * ystar + delta(t)
        th = torch.pow(10.0, t).unsqueeze(-1) * self.Vb / (2 * LN2)              # (M, G, 1)
        ev = self.ev.unsqueeze(1)
        frac = torch.minimum(ev, th).sum(-1, keepdim=True) / ev.sum(-1, keepdim=True).clamp(min=1e-30)
        return frac * self.ystar.unsqueeze(1) + torch.einsum('mgj,mjn->mgn', phi, self.dbias)

    def gains(self, t, phi):                  # t (M, G), phi (M, G, Jt) -> g (M, G, K)"""
assert a in src
src = src.replace(a, b)
a = """        yhat = self.dec(zt, phi) + torch.matmul(zt, self.Blin.unsqueeze(1))
        ex = dict(z=z, nu=nu, g=g, rate_k=rate_k)"""
b = """        yhat = self.dec(zt, phi) + torch.matmul(zt, self.Blin.unsqueeze(1)) + self.offset(t, phi).unsqueeze(2)
        ex = dict(z=z, nu=nu, g=g, rate_k=rate_k)"""
assert a in src
src = src.replace(a, b)
# init: ystar for ref/refu modes (whitened state nearest E a, decoder frame), zero otherwise
a = """        Bh = np.zeros((K, n))
        if mode == 'outpca':"""
b = """        ys = (stt['h_star'] - fh['m']) @ fh['Tinv'] if (mode in ('ref', 'refu') and l < L) else np.zeros(n)
        d['ystar'] = ys
        Bh = np.zeros((K, n))
        if mode == 'outpca':"""
assert a in src
src = src.replace(a, b)
a = """    init = dict(B=t('B'), dec_bias=t('bias'), Plin=t('Plin'), ev=t('ev'), V=t('V'), mode=mode, Bhead=t('Bhead'))"""
b = """    init = dict(B=t('B'), dec_bias=t('bias'), Plin=t('Plin'), ev=t('ev'), V=t('V'), mode=mode, Bhead=t('Bhead'),
                ystar=t('ystar'))"""
assert a in src
src = src.replace(a, b)
a = """    if model.tri:
        out.append((model.Ltri, 1, model.anch_t))"""
b = """    if model.tri:
        out.append((model.Ltri, 1, model.anch_t))
    out.append((model.dbias, 1, model.anch_t))
    if model.has_head:
        out.append((model.head.film, 2, model.anch_t))"""
assert a in src
src = src.replace(a, b)
open(P, 'w').write(src)
print('ok')
