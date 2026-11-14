"""Patch run_vr.py: analytic (water-filled linear-reference) anchor, FMLP gains, prior log-scale term."""
p = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_vr.py'
s = open(p).read()

old = """    def forward(self, x, t):
        f = self.film(t)
        w = self.width
        x0 = x
        for i in range(self.depth):
            g, c = f[..., 2 * i * w:(2 * i + 1) * w], f[..., (2 * i + 1) * w:(2 * i + 2) * w]
            x = self.act((1.0 + g) * torch.baddbmm(self.bs[i], x, self.Ws[i]) + c)
        y = torch.baddbmm(self.bs[-1], x, self.Ws[-1])
        if self.skip is not None:
            y = y + torch.bmm(x0, self.skip)
        if self.out_film:"""
new = """    def forward(self, x, t, gain=None, gain_mode=None):
        \"\"\"gain (M, B, d) multiplies: 'skip_out' the skip term's output, 'skip_in' the skip term's input, 'all' the
        whole output before the output FiLM.\"\"\"
        f = self.film(t)
        w = self.width
        x0 = x
        for i in range(self.depth):
            g, c = f[..., 2 * i * w:(2 * i + 1) * w], f[..., (2 * i + 1) * w:(2 * i + 2) * w]
            x = self.act((1.0 + g) * torch.baddbmm(self.bs[i], x, self.Ws[i]) + c)
        y = torch.baddbmm(self.bs[-1], x, self.Ws[-1])
        if self.skip is not None:
            if gain_mode == 'skip_out':
                y = y + gain * torch.bmm(x0, self.skip)
            elif gain_mode == 'skip_in':
                y = y + torch.bmm(gain * x0, self.skip)
            else:
                y = y + torch.bmm(x0, self.skip)
        if gain_mode == 'all':
            y = gain * y
        if self.out_film:"""
assert s.count(old) == 1
s = s.replace(old, new)

old = """    def log2p(self, z, t):
        M, B, K = z.shape
        T = (self.tri0 + self.tnet(t).view(M, B, K, K)) * self.mask      # strictly lower: u = z + T z, |det| = 1
        z = z + (T @ z.unsqueeze(-1)).squeeze(-1)
        d = self.net(t).view(M, B, K, self.C, 3)
        mu, ls, lw = self.mu + d[..., 0], (self.ls + d[..., 1]).clamp(-4.6, 6.0), self.lw + d[..., 2]"""
new = """    def log2p(self, z, t, ls_add=None):
        M, B, K = z.shape
        T = (self.tri0 + self.tnet(t).view(M, B, K, K)) * self.mask      # strictly lower: u = z + T z, |det| = 1
        z = z + (T @ z.unsqueeze(-1)).squeeze(-1)
        d = self.net(t).view(M, B, K, self.C, 3)
        ls = self.ls + d[..., 1] + (0.0 if ls_add is None else ls_add.unsqueeze(-1))
        mu, ls, lw = self.mu + d[..., 0], ls.clamp(-4.6, 9.0), self.lw + d[..., 2]"""
assert s.count(old) == 1
s = s.replace(old, new)

a = s.index("ALPHA, SHIFT = 16.0, 8.0")
b = s.index("def rate_at(rates, nmse, eps):")
newvr = '''SHIFT = 8.0


class VR(nn.Module):
    """Analytic anchor (Kelvin 03:20Z: identity anchor at high budget, shed the least important directions first as
    the price rises, checked against the linear reference): at initialisation the code at every price lambda IS the
    linear reference code: y_i = a_i(lambda) u_i^T x (x = whitened h_l; u_i, g_i = eigenpairs of G = E[J^T J]), power
    a_i^2 = max(0, g_i / theta - 1) with theta = lambda V / (2 ln 2) (the water level minimising the linearised
    Lagrangian), decoder = linear MMSE x_hat = sum_i u_i a_i / (a_i^2 + 1) z_i, prior scale sqrt(a_i^2 + 1). At high
    budget (small lambda) every direction the output depends on is sent at high SNR: a near-perfect reconstruction.
    Learned parts (MLP residuals, FiLM, prior corrections) start at zero. local: u = relu(x + SHIFT) (exact for
    x > -SHIFT), y = a(lambda) * ((u - SHIFT) U): affine in u for every fixed lambda, so the class stays L^1(n)."""

    def __init__(self, M, n, cls, K, width, C, anchor, local_width):
        super().__init__()
        self.cls = cls
        U, ev, V = anchor
        Uf = U.float().cpu()
        self.register_buffer('g', ev.float().to(DEV).view(1, 1, -1))
        self.V = V
        if cls == 'local':
            self.enc = FMLP(M, n, K, local_width, 1, act='relu', out_film=True)
            with torch.no_grad():
                W1 = torch.randn(n, local_width) * 0.01
                W1[:, :n] = torch.eye(n)
                self.enc.Ws[0].copy_(W1.to(DEV).expand(M, n, local_width))
                b1 = torch.zeros(1, local_width)
                b1[:, :n] = SHIFT
                self.enc.bs[0].copy_(b1.to(DEV).expand(M, 1, local_width))
                Wo = torch.zeros(local_width, K)
                Wo[:n, :] = Uf
                self.enc.Ws[1].copy_(Wo.to(DEV).expand(M, local_width, K))
                self.enc.bs[1].copy_((-SHIFT * Uf.sum(0, keepdim=True)).to(DEV).expand(M, 1, K))
            self.emode = 'all'
        else:
            Es = torch.zeros(2 * n, K)
            Es[:n] = Uf
            self.enc = FMLP(M, 2 * n, K, width, 3, out_film=True, last_scale=0.0, skip=Es)
            self.emode = 'skip_out'
        self.dec = FMLP(M, K, n, width, 3, last_scale=0.0, skip=Uf.T.contiguous())
        self.prior = CPrior(M, K, C, scale0=1.0)

    def gains(self, t):
        th = (10.0 ** (2.0 * t - 2.0)) * self.V / (2.0 * LOG2)              # (M, B, 1)
        a = torch.sqrt(torch.relu(self.g / th - 1.0))                         # (M, B, K)
        return a, a / (a * a + 1.0), 0.5 * torch.log(a * a + 1.0)

    def encode(self, x, t):
        a, _, _ = self.gains(t)
        return self.enc(x, t, gain=a, gain_mode=self.emode)

    def decode(self, z, t):
        _, bgain, _ = self.gains(t)
        return self.dec(z, t, gain=bgain, gain_mode='skip_in')

    def log2p(self, z, t):
        _, _, lsa = self.gains(t)
        return self.prior.log2p(z, t, ls_add=lsa)

    def forward(self, x, t, g):
        y = self.encode(x, t)
        z = y + torch.randn(y.shape, generator=g, device=DEV)
        logq = (-0.5 * (z - y) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2
        rate = (logq - self.log2p(z, t)).sum(-1)
        return self.decode(z, t), rate, z, logq.sum(-1)


'''
s = s[:a] + newvr + s[b:]
reps = [("    y = model.enc(x1.unsqueeze(0).expand(M, -1, -1), t)[mi]\n",
         "    y = model.encode(x1.unsqueeze(0).expand(M, -1, -1), t)[mi]\n"),
        ("            lp = model.prior.log2p(z.unsqueeze(0).expand(M, -1, -1), t)[mi].sum(-1)\n",
         "            lp = model.log2p(z.unsqueeze(0).expand(M, -1, -1), t)[mi].sum(-1)\n"),
        ("            zh = model.dec(z.unsqueeze(0).expand(M, -1, -1), t)[mi]\n",
         "            zh = model.decode(z.unsqueeze(0).expand(M, -1, -1), t)[mi]\n")]
for o, n2 in reps:
    assert s.count(o) == 1, o
    s = s.replace(o, n2)
# linref returns the eigenpairs for the anchor
o = """    out = dict(evals=ev.tolist(), theta=[], rate=[], nmse=[], nmse_lin=[])"""
assert s.count(o) == 1
s = s.replace(o, """    out = dict(evals=ev.tolist(), theta=[], rate=[], nmse=[], nmse_lin=[])
    anchor = (U.detach(), ev.detach(), V)""")
o = """        out['nmse_lin'].append(float(torch.minimum(ev, torch.tensor(th, device=DEV, dtype=torch.float64)).sum()) / V)
    return out"""
assert s.count(o) == 1
s = s.replace(o, """        out['nmse_lin'].append(float(torch.minimum(ev, torch.tensor(th, device=DEV, dtype=torch.float64)).sum()) / V)
    return out, anchor""")
o = """                res['linref'] = linref(net, l, L, V, fr, He, Ae, 99_000 + seed)"""
assert s.count(o) == 1
s = s.replace(o, """                res['linref'], anchor = linref(net, l, L, V, fr, He, Ae, 99_000 + seed)""")
for o, n2 in [("m1 = VR(6, n, cls, K, args.width, args.C, h_star_w, n)", "m1 = VR(6, n, cls, K, args.width, args.C, anchor, n)"),
              ("m2 = VR(1, n, cls, K, 2 * args.width, 2 * args.C, h_star_w, 2 * n)", "m2 = VR(1, n, cls, K, 2 * args.width, 2 * args.C, anchor, 2 * n)"),
              ("m3 = VR(1, n, cls, K, args.width, args.C, h_star_w, n)", "m3 = VR(1, n, cls, K, args.width, args.C, anchor, n)")]:
    assert s.count(o) == 1, o
    s = s.replace(o, n2)
# shorter anneal (first quarter), default steps 6000
o = "        ramp = min(1.0, step / max(1.0, 0.5 * steps))          # lambda annealed upward from 1e-4 (t = -1)"
assert s.count(o) == 1
s = s.replace(o, "        ramp = min(1.0, step / max(1.0, 0.25 * steps))         # lambda annealed upward from 1e-4 (t = -1)")
o = "ap.add_argument('--steps', type=int, default=4000)"
assert s.count(o) == 1
s = s.replace(o, "ap.add_argument('--steps', type=int, default=6000)")
open(p, 'w').write(s)
print('patched')
