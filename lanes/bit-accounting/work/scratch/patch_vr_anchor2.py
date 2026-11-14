"""Patch run_vr.py (v3 anchor): learned gain correction c(t) on top of the analytic water-filled gain a(t); unit-scale
encoder output; decoder input b~ * z with b~ = a~ / (a~^2 + 1); prior on the standardised code z / sqrt(a~^2 + 1)."""
p = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_vr.py'
s = open(p).read()
a = s.index("class VR(nn.Module):")
b = s.index("def rate_at(rates, nmse, eps):")
newvr = '''class VR(nn.Module):
    """Analytic anchor (Kelvin 03:20Z: identity anchor at high budget, shed the least important directions first as
    the price rises, checked against the linear reference). Code y = a~(lambda) * y~(x), z = y + N(0, I):
      y~ = unit-scale encoder output, initialised to U^T x (x = whitened h_l; U, g = eigenpairs of G = E[J^T J]);
      a~ = a + c(lambda): a_i = sqrt(max(0, g_i / theta - 1)), theta = lambda V / (2 ln 2) (the water-filled power that
      minimises the linearised Lagrangian), c a learned correction (zero at initialisation; can switch on directions
      the linear code leaves off);
      decoder input b~ * z with b~ = a~ / (a~^2 + 1) (the linear-MMSE scaling), output MLP + U b~ z (MLP zero at init);
      prior on the standardised code z / sqrt(a~^2 + 1) (unit lower-triangular map + factorised mixture), with the
      Jacobian term -sum log2 sqrt(a~^2 + 1).
    At initialisation the code at every lambda IS the linear reference code; at high budget it reconstructs every
    direction the output depends on almost perfectly. local: u = relu(x + SHIFT) (exact for x > -SHIFT), y~ =
    (u - SHIFT) U, so for every fixed lambda y = a~ * (A2 u + b2) is affine in u: the class stays L^1(n)."""

    def __init__(self, M, n, cls, K, width, C, anchor, local_width):
        super().__init__()
        self.cls = cls
        U, ev, V = anchor
        Uf = U.float().cpu()
        self.register_buffer('g', ev.float().to(DEV).view(1, 1, -1))
        self.V = V
        if cls == 'local':
            self.enc = FMLP(M, n, K, local_width, 1, act='relu')
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
        else:
            Es = torch.zeros(2 * n, K)
            Es[:n] = Uf
            self.enc = FMLP(M, 2 * n, K, width, 3, last_scale=0.0, skip=Es)
        self.cnet = sn.BMLP(M, 1, K, 64, 2, last_scale=0.0)
        self.dec = FMLP(M, K, n, width, 3, last_scale=0.0, skip=Uf.T.contiguous())
        self.prior = CPrior(M, K, C, scale0=1.0)

    def gain(self, t):
        th = (10.0 ** (2.0 * t - 2.0)) * self.V / (2.0 * LOG2)              # (M, B, 1)
        a = torch.sqrt(torch.relu(self.g / th - 1.0))                         # (M, B, K)
        return a + self.cnet(t)

    def encode(self, x, t):
        return self.gain(t) * self.enc(x, t)

    def decode(self, z, t):
        at = self.gain(t)
        return self.dec(z * (at / (at * at + 1.0)), t)

    def log2p(self, z, t):
        at = self.gain(t)
        sd = torch.sqrt(at * at + 1.0)
        return self.prior.log2p(z / sd, t) - torch.log2(sd)

    def forward(self, x, t, g):
        y = self.encode(x, t)
        z = y + torch.randn(y.shape, generator=g, device=DEV)
        logq = (-0.5 * (z - y) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2
        rate = (logq - self.log2p(z, t)).sum(-1)
        return self.decode(z, t), rate, z, logq.sum(-1)


'''
s = s[:a] + newvr + s[b:]
open(p, 'w').write(s)
print('patched v3')
