"""Timing benchmark: forward+backward through a fixed 256x256 ReLU future of t layers, float32, 2 threads."""
import sys
import time

import torch

torch.set_num_threads(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
n = 256
for dt in [torch.float32, torch.bfloat16]:
    Ws = [torch.randn(n, n, dtype=dt) * (2.0 / n) ** 0.5 for _ in range(32)]
    for B in [512, 2048]:
        for t in [1, 16, 32]:
            x = torch.randn(B, n, dtype=dt, requires_grad=True)
            for rep in range(2):
                t0 = time.time()
                for _ in range(5):
                    h = x
                    for k in range(t):
                        h = torch.relu(h @ Ws[k].T)
                    loss = (h.float() ** 2).mean()
                    loss.backward()
                el = (time.time() - t0) / 5
            print(f"{dt} B={B} t={t}: {el*1000:.1f} ms/step, {3*2*B*n*n*t/el/1e9:.1f} GFLOP/s", flush=True)
# encoder/decoder MLP cost
dt = torch.float32
for width in [1024, 2048]:
    enc = torch.nn.Sequential(torch.nn.Linear(n, width), torch.nn.ReLU(), torch.nn.Linear(width, width), torch.nn.ReLU(),
                              torch.nn.Linear(width, 256))
    dec = torch.nn.Sequential(torch.nn.Linear(256, width), torch.nn.ReLU(), torch.nn.Linear(width, width), torch.nn.ReLU(),
                              torch.nn.Linear(width, n))
    opt = torch.optim.Adam(list(enc.parameters()) + list(dec.parameters()), 1e-3)
    B = 1024
    x = torch.randn(B, n)
    t0 = time.time()
    for _ in range(5):
        y = dec(torch.sign(enc(x)))
        loss = (y ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    el = (time.time() - t0) / 5
    print(f"MLP width {width} B={B}: {el*1000:.1f} ms/step", flush=True)
