"""Patch vrlib.py (amendment A2): full fp32 for every precision-critical matmul; TF32 only inside the MLP hidden
layers. Dev 9100, unrestricted l = 31 at init: TF32 rounding in the linear decoder (which contains W_32^{-1}) gave
nMSE 0.033 at the smallest lambda against 1.6e-4 in fp32."""
P = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/lib/vrlib.py'
src = open(P).read()


def rep(a, b, count=1):
    global src
    assert src.count(a) == count, (a, src.count(a))
    src = src.replace(a, b)


rep("""# ----------------------------------------------------------------------------------------------------------------------
# Nets
# ----------------------------------------------------------------------------------------------------------------------
""", """def mm32(a, b):
    \"\"\"matmul in full fp32 (TF32 off): linear paths, frames, output layers, local encoder, prior map.\"\"\"
    with fp32():
        return torch.matmul(a, b)


def bmm32(a, b):
    with fp32():
        return torch.bmm(a, b)


# ----------------------------------------------------------------------------------------------------------------------
# Nets
# ----------------------------------------------------------------------------------------------------------------------
""")
# BLin: optional fp32
rep("""class BLin(nn.Module):
    def __init__(self, M, din, dout, scale=1.0, zero=False):
        super().__init__()""", """class BLin(nn.Module):
    def __init__(self, M, din, dout, scale=1.0, zero=False, full=False):
        super().__init__()
        self.full = full""")
rep("""    def forward(self, x):  # x (M, N, din)
        return torch.baddbmm(self.b, x, self.w)""", """    def forward(self, x):  # x (M, N, din)
        if self.full:
            with fp32():
                return torch.baddbmm(self.b, x, self.w)
        return torch.baddbmm(self.b, x, self.w)""")
rep("""        self.out = BLin(M, W, dout, zero=zero_out)""", """        self.out = BLin(M, W, dout, zero=zero_out, full=True)""")
# local encoder
rep("""        u = torch.relu(torch.matmul(y, A1) + b1.unsqueeze(2))""", """        u = torch.relu(mm32(y, A1) + b1.unsqueeze(2))""")
rep("""        return torch.matmul(u, A2) + b2.unsqueeze(2)""", """        return mm32(u, A2) + b2.unsqueeze(2)""")
# linear path of unres/out encoders
rep("""        return nu + torch.bmm(src.reshape(M, G * Bg, n), self.Plin).view(M, G, Bg, self.K)""",
    """        return nu + bmm32(src.reshape(M, G * Bg, n), self.Plin).view(M, G, Bg, self.K)""")
# prior map
rep("""            zs = zs + torch.matmul(zs, Lt.transpose(-1, -2))                  # w = (I + Lt) zs""",
    """            zs = zs + mm32(zs, Lt.transpose(-1, -2))                          # w = (I + Lt) zs""")
# decoder linear path and head linear path
rep("""        yhat = self.dec(zt, phi) + torch.matmul(zt, self.Blin.unsqueeze(1)) + self.offset(t, phi).unsqueeze(2)""",
    """        yhat = self.dec(zt, phi) + mm32(zt, self.Blin.unsqueeze(1)) + self.offset(t, phi).unsqueeze(2)""")
rep("""            ex['xa_head'] = self.head(ztd, phi) + torch.matmul(ztd, self.Bhead.unsqueeze(1))""",
    """            ex['xa_head'] = self.head(ztd, phi) + mm32(ztd, self.Bhead.unsqueeze(1))""")
# frames
rep("""    def from_pca_a(self, xa):
        return self.ma + torch.bmm(xa, self.Pa_inv)""", """    def from_pca_a(self, xa):
        return self.ma + bmm32(xa, self.Pa_inv)""")
rep("""        return torch.bmm(h - self.m, self.Sm12)""", """        return bmm32(h - self.m, self.Sm12)""")
rep("""        return self.m + torch.bmm(y, self.S12)""", """        return self.m + bmm32(y, self.S12)""")
rep("""        return torch.bmm(a - self.ma, self.Pa)""", """        return bmm32(a - self.ma, self.Pa)""")
open(P, 'w').write(src)
print('ok')
