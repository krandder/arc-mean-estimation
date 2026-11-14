"""Extend gpu_src/scripts/run_entropy.py (Kelvin 02:10Z): primary arm 'gfix' = real-valued code with FIXED unit Gaussian
noise and an encoder-chosen scale, rate = information estimate E[log2 q(z|h) - log2 p(z)] with a learned prior p (per
latent a mixture of 3 Gaussians); comparison arm 'bern' = Bernoulli bits with encoder-predicted p, straight-through
relaxed sampling, rate = sum_j [H(mean p_j) - mean H(p_j)] (the information each bit carries under the matched
prior; NOT H(p)). 'ent' and 'vib' kept for comparison."""
p = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_entropy.py'
s = open(p).read()


def sub(old, new):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, 1)


sub("""class Arm(nn.Module):""", '''class GPrior(nn.Module):
    """Per (model, latent) mixture of 3 Gaussians; log2 density."""

    def __init__(self):
        super().__init__()
        self.mu = nn.Parameter(torch.randn(M, 1, K, 3, device=DEV))
        self.ls = nn.Parameter(torch.full((M, 1, K, 3), 0.7, device=DEV))
        self.lw = nn.Parameter(torch.zeros(M, 1, K, 3, device=DEV))

    def log2p(self, z):
        ze = z.unsqueeze(-1)
        s = torch.exp(self.ls).clamp(min=1e-2)
        lp = -0.5 * ((ze - self.mu) / s) ** 2 - torch.log(s) - 0.5 * math.log(2 * math.pi)
        lw = torch.log_softmax(self.lw, -1)
        return torch.logsumexp(lp + lw, -1) / LOG2


def hbits(p):
    p = p.clamp(1e-6, 1 - 1e-6)
    return -(p * torch.log2(p) + (1 - p) * torch.log2(1 - p))


class Arm(nn.Module):''')
sub("""        d_out = K if kind == 'ent' else 2 * K""", """        d_out = 2 * K if kind == 'vib' else K""")
sub("""        self.prior = Prior() if kind == 'ent' else None""",
    """        self.prior = Prior() if kind == 'ent' else (GPrior() if kind == 'gfix' else None)""")
sub("""        mu, ls = y[..., :K], y[..., K:].clamp(-8, 4)""", """        if self.kind == 'gfix':
            z = y + torch.randn(y.shape, generator=g, device=DEV)            # fixed unit noise, encoder-chosen scale
            logq = (-0.5 * (z - y) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2
            rate = (logq - self.prior.log2p(z)).sum(-1)                     # MC estimate of KL(q || p), bits
            return self.dec(z), rate, z
        if self.kind == 'bern':
            pr = torch.sigmoid(y)
            if train:
                u = torch.rand(y.shape, generator=g, device=DEV).clamp(1e-6, 1 - 1e-6)
                soft = torch.sigmoid((y + torch.log(u) - torch.log1p(-u)) / 0.5)
                hard = (soft > 0.5).to(DT)
                b = hard + soft - soft.detach()
            else:
                b = (torch.rand(y.shape, generator=g, device=DEV) < pr).to(DT)
            pbar = pr.mean(1, keepdim=True)
            info = (hbits(pbar) - hbits(pr).mean(1, keepdim=True)).sum(-1)  # (M, 1): sum_j I(h; b_j) estimate
            return self.dec(2 * b - 1), info.expand(-1, y.shape[1]), pr
        mu, ls = y[..., :K], y[..., K:].clamp(-8, 4)""")
sub("""                arms = [Arm(n, cls, fr, fr_a, h_star_w, kind) for kind in ('ent', 'vib')]""",
    """                arms = [Arm(n, cls, fr, fr_a, h_star_w, kind) for kind in KINDS]""")
sub("""ap.add_argument('--tag', default='')""", """ap.add_argument('--tag', default='')
ap.add_argument('--kinds', default='gfix,bern,ent,vib')""")
sub("""LAMS = [float(v) for v in args.lambdas.split(',')]""", """LAMS = [float(v) for v in args.lambdas.split(',')]
KINDS = args.kinds.split(',')""")
# evaluation extras for gfix (refit prior on held-out z) and bern (bit usage)
sub("""                    if arm.kind == 'ent':
                        half = args.P_eval // 2""", """                    half = args.P_eval // 2
                    if arm.kind == 'gfix':
                        zA, zB = codes[:, :half].detach(), codes[:, half:].detach()
                        mu_e = arm.enc(arm.inp(He[l], Ae)).detach()
                        gp2 = GPrior()
                        o2 = torch.optim.Adam(gp2.parameters(), lr=0.05)
                        for _ in range(600):
                            lo = -gp2.log2p(zA).sum(-1).mean()
                            o2.zero_grad()
                            lo.backward()
                            o2.step()
                        with torch.no_grad():
                            logqB = (-0.5 * (zB - mu_e[:, half:]) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2
                            cur['rate_refit'] = (logqB - gp2.log2p(zB)).sum(-1).mean(1).tolist()
                            cur['scale'] = mu_e.std(1).mean(-1).tolist()
                    if arm.kind == 'bern':
                        pr = codes.detach()
                        pbar = pr.mean(1)
                        info_j = (hbits(pbar) - hbits(pr).mean(1))                  # (M, K)
                        cur['bit_info'] = info_j.tolist()
                        cur['bits_half'] = ((pr - 0.5).abs() < 0.05).float().mean(1).tolist()  # per bit: share of samples with p ~ 0.5
                        cur['bits_det'] = ((pr < 0.05) | (pr > 0.95)).float().mean(1).tolist()
                    if arm.kind == 'ent':""")
sub("""                torch.save({k: v for k, v in arms[0].state_dict().items()}, path.replace('.json', '_ent.pt'))
                ce, cv = res['curves']['ent'], res['curves']['vib']""", """                torch.save({kk: a.state_dict() for kk, a in zip(KINDS, arms)}, path.replace('.json', '.pt'))
                ce, cv = res['curves'][KINDS[0]], res['curves'][KINDS[1]]""")
sub("""                print(f'{tag}: {res["seconds"]:.0f}s | ent (rate, nMSE) ' +""", """                print(f'{tag}: {res["seconds"]:.0f}s | {KINDS[0]} (rate, nMSE) ' +""")
sub("""' '.join(f'({r:.1f},{e:.3f})' for r, e in zip(ce['rate'], ce['nmse'])) + ' | vib ' +""",
    """' '.join(f'({r:.1f},{e:.3f})' for r, e in zip(ce['rate'], ce['nmse'])) + f' | {KINDS[1]} ' +""")
open(p, 'w').write(s)
print('patched run_entropy.py')
