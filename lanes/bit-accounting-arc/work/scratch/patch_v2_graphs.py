"""Patch vrlib.py: optional CUDA graphs for the fixed net in training (narrow-deep's 256 tiny layers are launch-bound):
a captured no-grad sampler (x -> h_l, a) and a graphed callable for the future with autograd. Same arithmetic."""
P = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/lib/vrlib.py'
src = open(P).read()
a = """def stratified_t(M, G, t_range, gen):"""
b = """class GraphedNet:
    \"\"\"CUDA-graph replays of the fixed net for fixed shapes (M, B, n): sample() = x ~ N(0, I) -> (h_l, a) without
    grad; future(h) = layers l+1..L with autograd (torch.cuda.make_graphed_callables).\"\"\"

    def __init__(self, bnet, l, M, B):
        self.bnet, self.l, self.L = bnet, l, bnet.L
        n = bnet.n
        self.x = torch.randn(M, B, n, device=DEV, dtype=DT)
        s = torch.cuda.Stream()
        s.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(s), torch.no_grad():
            for _ in range(3):
                h = self.x if l == 0 else bnet.run(self.x, 0, l)
                if l < bnet.L:
                    bnet.run(h, l)
        torch.cuda.current_stream().wait_stream(s)
        self.g = torch.cuda.CUDAGraph()
        with torch.no_grad(), torch.cuda.graph(self.g):
            self.h = self.x * 1.0 if l == 0 else bnet.run(self.x, 0, l)
            self.a = bnet.run(self.h, l) if l < bnet.L else self.h * 1.0
        self.fut = None
        if l < bnet.L:
            class Fut(nn.Module):
                def forward(s_, hh):
                    return bnet.run(hh, l)
            prev = torch.backends.cuda.matmul.allow_tf32
            torch.backends.cuda.matmul.allow_tf32 = False
            self.fut = torch.cuda.make_graphed_callables(
                Fut(), (torch.randn(M, B, n, device=DEV, dtype=DT, requires_grad=True),))
            torch.backends.cuda.matmul.allow_tf32 = prev

    def sample(self, gen):
        with torch.no_grad():
            self.x.normal_(generator=gen)
            self.g.replay()
            return self.h.clone(), self.a.clone()

    def future(self, hh):
        return self.fut(hh)


def stratified_t(M, G, t_range, gen):"""
assert a in src
src = src.replace(a, b)
a = """def train(model, bnet, fr, l, steps, B, G, t_range, seed, lr=1e-3, lr_lin=1e-4, lr_enc=3e-4, fixed_t=None,
          log_every=500, nbins=24, clip=10.0, tf32=True, logf=None, anneal=0.4):"""
b = """def train(model, bnet, fr, l, steps, B, G, t_range, seed, lr=1e-3, lr_lin=1e-4, lr_enc=3e-4, fixed_t=None,
          log_every=500, nbins=24, clip=10.0, tf32=True, logf=None, anneal=0.4, graphs=False):"""
assert a in src
src = src.replace(a, b)
a = """        h, a = sample_batch(bnet, l, M, B, gen)"""
b = """        if gnet is not None:
            h, a = gnet.sample(gen)
        else:
            h, a = sample_batch(bnet, l, M, B, gen)"""
assert a in src
src = src.replace(a, b)
i = src.index("def train(model, bnet, fr, l, steps")
j = src.index("        ah = bnet.run(hh, l) if l < L else out_clip(bnet, hh)", i)
src = src[:j] + """        ah = (gnet.future(hh) if gnet is not None else bnet.run(hh, l)) if l < L else out_clip(bnet, hh)""" + \
    src[j + len("        ah = bnet.run(hh, l) if l < L else out_clip(bnet, hh)"):]
a = """    sp = model.anch_t[1] - model.anch_t[0]"""
b = """    gnet = GraphedNet(bnet, l, M, B) if (graphs and DEV == 'cuda') else None
    sp = model.anch_t[1] - model.anch_t[0]"""
assert a in src
src = src.replace(a, b)
open(P, 'w').write(src)
print('ok')
