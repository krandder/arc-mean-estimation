"""S11 control nets (Kelvin 02:40Z): smallnets.Net gains kind in {relu (default), tanh4, linear, feistel}; the S2, S7, S9
and S10 scripts gain --netkind. relu: W ~ N(0, 2/n), relu (unchanged). tanh4: W ~ N(0, 4/n) (sigma_w^2 = 4, chaotic
phase of a bias-free tanh net), tanh. linear: W ~ N(0, 1/n), identity activation. feistel: inputs uniform on {+-1}^n;
each layer is a Feistel round (L, R) -> (R, L * g(R)) with g_j(R) = product of 3 fixed random coordinates of R (a
degree-3 parity), a reversible Boolean mixing circuit written as polynomials so that decoded real states can be run."""
W = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/'
p = W + 'lib/smallnets.py'
s = open(p).read()
old = """class Net:
    def __init__(self, seed, n, L):
        self.seed, self.n, self.L = seed, n, L
        self.W64 = [st.W_layer(seed, n, k) for k in range(1, L + 1)]
        self.WT = [torch.tensor(np.ascontiguousarray(W.T), dtype=DT, device=DEV) for W in self.W64]

    def run(self, h, l0, l1=None):
        l1 = self.L if l1 is None else l1
        for k in range(l0, l1):
            h = torch.relu(h @ self.WT[k])
        return h

    @torch.no_grad()
    def sample(self, P, layers, gen):
        x = torch.randn(P, self.n, generator=gen, device=DEV, dtype=DT)"""
new = """class Net:
    def __init__(self, seed, n, L, kind='relu'):
        self.seed, self.n, self.L, self.kind = seed, n, L, kind
        scale = {'relu': 1.0, 'tanh4': math.sqrt(2.0), 'linear': math.sqrt(0.5), 'feistel': 1.0}[kind]
        self.W64 = [st.W_layer(seed, n, k) * scale for k in range(1, L + 1)]
        self.WT = [torch.tensor(np.ascontiguousarray(W.T), dtype=DT, device=DEV) for W in self.W64]
        if kind == 'feistel':
            rng = np.random.default_rng([777, seed, n, L])
            hn = n // 2
            self.trip = [torch.tensor(np.stack([rng.choice(hn, 3, replace=False) for _ in range(hn)]), device=DEV)
                         for _ in range(L)]

    def layer(self, h, k):
        if self.kind == 'relu':
            return torch.relu(h @ self.WT[k])
        if self.kind == 'tanh4':
            return torch.tanh(h @ self.WT[k])
        if self.kind == 'linear':
            return h @ self.WT[k]
        hn = self.n // 2
        Lh, Rh = h[..., :hn], h[..., hn:]
        t = self.trip[k]
        g = Rh[..., t[:, 0]] * Rh[..., t[:, 1]] * Rh[..., t[:, 2]]
        return torch.cat([Rh, Lh * g], -1)

    def run(self, h, l0, l1=None):
        l1 = self.L if l1 is None else l1
        for k in range(l0, l1):
            h = self.layer(h, k)
        return h

    @torch.no_grad()
    def sample(self, P, layers, gen):
        x = torch.randn(P, self.n, generator=gen, device=DEV, dtype=DT)
        if self.kind == 'feistel':
            x = torch.sign(x + 1e-12)"""
assert old in s
s = s.replace(old, new)
old2 = """            if k < self.L:
                h = torch.relu(h @ self.WT[k])
        return H, h


def frame("""
new2 = """            if k < self.L:
                h = self.layer(h, k)
        return H, h


def frame("""
assert old2 in s
s = s.replace(old2, new2)
open(p, 'w').write(s)
for script in ['scripts/run_entropy.py', 'scripts/run_chain_real.py', 'scripts/run_sim.py', 'scripts/run_chain.py']:
    q = W + script
    t = open(q).read()
    t = t.replace("ap.add_argument('--out', required=True)",
                  "ap.add_argument('--netkind', default='relu')\nap.add_argument('--out', required=True)", 1)
    n_calls = t.count('sn.Net(seed, n, L)') + t.count('sn.Net(args.seed, n, L)')
    t = t.replace('sn.Net(seed, n, L)', 'sn.Net(seed, n, L, kind=args.netkind)')
    t = t.replace('sn.Net(args.seed, n, L)', 'sn.Net(args.seed, n, L, kind=args.netkind)')
    assert n_calls >= 1, script
    open(q, 'w').write(t)
    print('patched', script, n_calls)
print('patched smallnets')
