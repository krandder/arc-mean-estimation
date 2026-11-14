"""EXPLORATORY check (not registered): LVTV2 on net 640 (1024 x 256) on the CPU vs the GPU run's estimate.
usage: check_gpu_cpu_1024.py TP_ROOT GPU_LV_JSON"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import smlib
lv = smlib.load_lvlib(os.path.join(sys.argv[1], 'estimator', 'lvlib.py'))
W = [w.double() for w in smlib.au.weights(640, 1024, 256)]
r = smlib.run_lv(lv, W, 24, 6.5, 'full', 'v2f')
g = json.load(open(sys.argv[2]))['arms']['LVTV2']
a = np.array(g['mean'])
print(f"CPU vs GPU LVTV2 on net 640: max rel diff {np.abs(r['mean'] - a).max() / np.abs(a).max():.2e}; V_L cpu {r['Vs'][-1]:.6f} gpu {g['Vs'][-1]:.6f}; "
      f"flops cpu {r['flops']:.6e} gpu {g['flops']:.6e}; secs {r['secs']:.0f}", flush=True)
