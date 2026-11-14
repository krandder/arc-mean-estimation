"""Narrow-deep 8 x 256 weights for the GPU worker: nd.make_weights('plain', seed, 8, 256) rescaled per layer by
constants with the sibling lane's bitlib.rescale_weights (nMSE-invariant by positive homogeneity), saved float64."""
import sys
import numpy as np
sys.path.insert(0, '/home/agent/workspaces/mats/work/bit-accounting-arc/lib')
import bitlib  # noqa: E402  (copy of the sibling lane's library)
out = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/weights'
for seed in [111, 203, 216, 217, 220, 221, 223]:
    Ws = bitlib.rescale_weights(bitlib.nd_weights(seed))
    np.save(f'{out}/nd_{seed}.npy', np.stack(Ws))
    print(seed, len(Ws), Ws[0].shape, float(np.linalg.norm(Ws[0])), float(np.linalg.norm(Ws[-1])))
