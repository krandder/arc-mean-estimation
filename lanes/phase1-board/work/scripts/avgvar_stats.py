# usage: python3 -I avgvar_stats.py TSV [TSV...]
# Expected full-budget plain-MC raw MSE per MLP = avg_variance / N, N = 64,280.96 (whestbench ROUNDS v1-phase1, k=4)
import sys, statistics as st
N_K4 = 272e9 / (2*32*256**2 + 17*256 + 4*32*256)   # 4,231,424 FLOPs/sample (dtype-aware billing)
N_ARITH = 272e9 / (2*32*256**2)                       # 4,194,304 FLOPs/sample (arithmetic count)
for f in sys.argv[1:]:
    rows = [l.rstrip('\n').split('\t') for l in open(f)][1:]
    v = sorted(float(r[3]) for r in rows)
    ids = [int(r[1]) for r in rows]
    n = len(v)
    q = lambda p: v[min(n-1, int(p*(n-1)+0.5))]
    print('%s: n=%d unique ids=%d id range %d-%d' % (f, n, len(set(ids)), min(ids), max(ids)))
    print('  avg_variance: mean %.5f median %.5f sd %.5f min %.5f p5 %.5f p95 %.5f max %.5f' % (st.mean(v), st.median(v), st.pstdev(v), v[0], q(.05), q(.95), v[-1]))
    for lab, N in (('N=64,281 (k=4)', N_K4), ('N=64,850 (2dw^2)', N_ARITH)):
        m = [x/N for x in v]
        print('  MC raw MSE @ %s: mean %.4g median %.4g min %.4g p5 %.4g p95 %.4g max %.4g' % (lab, st.mean(m), st.median(m), m[0], q(.05)/N, q(.95)/N, m[-1]))
print('N_K4 = %.2f, N_ARITH = %.2f' % (N_K4, N_ARITH))
