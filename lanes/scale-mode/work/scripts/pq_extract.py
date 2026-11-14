"""Extract MLPs from a WhestBench public parquet file (untrusted data) into npz files.
usage: pq_extract.py PARQUET OUT_DIR MAX_ID [MIN_ID]
Writes OUT_DIR/p2_mlp_XX.npz with weights (depth, width, width) float32 in the dataset's (in, out) convention
(h_l = relu(h_{l-1} @ W_l)), all_layer_means (depth, width) float32 (1e9-sample truth), avg_variance (final layer, mean
over neurons), mlp_seed, mlp_id, plus the per-row JSON budget breakdown string."""
import os, sys, json
import numpy as np
import pyarrow.parquet as pq

src, out, max_id = sys.argv[1], sys.argv[2], int(sys.argv[3]); min_id = int(sys.argv[4]) if len(sys.argv) > 4 else 0
os.makedirs(out, exist_ok=True)
pf = pq.ParquetFile(src)
print('schema', pf.schema_arrow)
done = []
for rg in range(pf.num_row_groups):
    t = pf.read_row_group(rg, columns=['mlp_id', 'mlp_name', 'mlp_seed', 'weights', 'all_layer_means', 'final_means',
                                       'avg_variance', 'sampling_budget_breakdown'])
    ids = t.column('mlp_id').to_pylist()
    for i, mid in enumerate(ids):
        if mid >= max_id or mid < min_id:
            continue
        row = {c: t.column(c)[i].as_py() for c in ('mlp_name', 'mlp_seed', 'avg_variance', 'sampling_budget_breakdown')}
        W = np.asarray(t.column('weights')[i].as_py(), dtype=np.float32)
        M = np.asarray(t.column('all_layer_means')[i].as_py(), dtype=np.float32)
        F = np.asarray(t.column('final_means')[i].as_py(), dtype=np.float32)
        assert W.ndim == 3 and W.shape[1] == W.shape[2] and M.shape == (W.shape[0], W.shape[1]), (W.shape, M.shape)
        assert np.array_equal(F, M[-1])
        np.savez(os.path.join(out, f'p2_mlp_{mid:02d}.npz'), weights=W, all_layer_means=M, avg_variance=float(row['avg_variance']),
                 mlp_seed=int(row['mlp_seed']), mlp_id=int(mid), mlp_name=str(row['mlp_name']),
                 budget_breakdown=str(row['sampling_budget_breakdown']))
        done.append(mid)
        print('mlp', mid, row['mlp_name'], W.shape, 'avg_var', row['avg_variance'], flush=True)
print('extracted', sorted(done))
