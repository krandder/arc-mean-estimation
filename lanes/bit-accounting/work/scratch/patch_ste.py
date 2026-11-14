"""Patch gpu_src/lib/smallnets.py: straight-through gradient of the sign bits through tanh(z / s), s = the batch
standard deviation of z (detached). The forward code is unchanged (sign z, thresholds free); the surrogate no longer
saturates when z is large, which left some 1- to 4-bit models with dead (constant) codes in the dev runs."""
p = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/lib/smallnets.py'
s = open(p).read()
old = """        if self.kind == 'bin':
            t = torch.tanh(z)
            c = t + (torch.sign(z) - t).detach()
            return c * self.mask"""
new = """        if self.kind == 'bin':
            sd = z.detach().std(1, keepdim=True).clamp(min=1e-3) if z.shape[1] > 1 else 1.0
            t = torch.tanh(z / sd)
            c = t + (torch.sign(z) - t).detach()
            return c * self.mask"""
assert old in s
s = s.replace(old, new)
open(p, 'w').write(s)
print('patched smallnets')
p2 = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_chain.py'
s = open(p2).read()
old2 = """def ste_sign(z):
    t = torch.tanh(z)
    return t + (torch.sign(z) - t).detach()"""
new2 = """def ste_sign(z):
    sd = z.detach().std(1, keepdim=True).clamp(min=1e-3) if z.shape[1] > 1 else 1.0
    t = torch.tanh(z / sd)
    return t + (torch.sign(z) - t).detach()"""
assert old2 in s
s = s.replace(old2, new2)
open(p2, 'w').write(s)
print('patched run_chain')
