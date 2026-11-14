"""Local weight checksums (anet.make_weights, numpy RandomState stream) for the GPU cell's nets. usage: local_checksums.py OUT_JSON"""
import json, sys
sys.path.insert(0, '/home/agent/workspaces/mats/work/arc-noisy')
import anet
out = {}
for seed, n, L in [(s, 1024, 256) for s in range(640, 648)] + [(s, 512, 128) for s in range(634, 638)] + [(699, 128, 32)]:
    W = anet.make_weights(seed, n, L)
    out[f'au{seed}_n{n}_L{L}'] = float(anet.weights_checksum(W))
    print(seed, n, L, out[f'au{seed}_n{n}_L{L}'], flush=True)
    del W
json.dump(out, open(sys.argv[1], 'w'), indent=1)
