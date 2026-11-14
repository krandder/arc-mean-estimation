"""Descriptive (not registered): is there an exact linear tail at 256 x 32? For 4096 inputs, compare each input's gate
pattern in the last k layers with the per-neuron majority pattern: fraction of inputs with no mismatch in the last k
layers (k = 1, 2, 4, 8) and the mean fraction of mismatched gates per layer."""
import sys, json, numpy as np, torch
sys.path.insert(0, 'lib'); import rnd
out = {}
for s in range(200, 205):
    net = rnd.Net(s, 256, 32); rng = np.random.default_rng(s)
    X = torch.as_tensor(rng.standard_normal((4096, 256))).float()
    pats = []
    with torch.no_grad():
        h = X
        for l in range(32):
            z = h @ net.Wt[l]; pats.append((z > 0).numpy()); h = torch.relu(z)
    P = np.stack(pats, 1)                       # (4096, 32, 256)
    maj = P.mean(0) > 0.5
    mism = P != maj[None]
    frac = mism.mean(axis=(0, 2))
    res = {k: float(np.mean(~mism[:, 32 - k:, :].any(axis=(1, 2)))) for k in (1, 2, 4, 8)}
    out[s] = dict(no_mismatch_last_k=res, mismatch_frac_by_layer=frac.tolist())
    print(s, 'P(no mismatch in last k layers)', res, 'mismatch fraction at layers 1,8,16,24,32:', [round(float(frac[i]), 3) for i in (0, 7, 15, 23, 31)])
json.dump(out, open('runs/tail_check_n256_L32.json', 'w'))
