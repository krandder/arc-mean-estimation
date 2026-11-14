"""Report changes after review r2b: single-model counts next to R*, unrestricted exceptions, certificate counts,
coverage breakdown, softer control wording, provisional framing."""
W = '/home/agent/workspaces/mats/work/bit-accounting'
# ---- summary_fill: exceptions, counts, coverage
p = f'{W}/scratch/summary_fill.py'
s = open(p).read()
old = """    d['UDEV1'] = f'{np.median(dev[0.1]):.2f} (max {max(dev[0.1]):.2f})' if dev[0.1] else 'pending'"""
new = """    exc = []
    for n, L in ((16, 4), (32, 8), (16, 16), (32, 32)):
        for sd in (5000, 5001, 5002):
            o = cells.get(f'relu_{n}_{L}_{sd}_{L}_unres')
            if o is None:
                continue
            for l in sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1])):
                c = cells.get(f'relu_{n}_{L}_{sd}_{l}_unres')
                for D in (0.1, 0.01):
                    a, b = (c or {}).get('R', {}).get(str(D)), o['R'].get(str(D))
                    if a is not None and b is not None and abs(a - b) > max(0.5, 0.15 * b):
                        exc.append((f'{n}x{L} s{sd} l={l} at {int(D * 100)}%', a, b))
    exc.sort(key=lambda e: -(e[1] - e[2]))
    d['UEXC'] = (f'{len(exc)} exceptions; the largest: ' + '; '.join(f'{e[0]}: {e[1]:.1f} against {e[2]:.1f}' for e in exc[:4])
                 if exc else 'no exceptions')
    d['UDEV1'] = f'{np.median(dev[0.1]):.2f} (max {max(dev[0.1]):.2f})' if dev[0.1] else 'pending'"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """    pct = lambda k: ('-' if sc.get(k, {}).get('frac') is None else f'{100 * sc[k]["frac"]:.0f}%')  # noqa: E731"""
new = """    pct = lambda k: ('-' if sc.get(k, {}).get('frac') is None else  # noqa: E731
                     f'{round(sc[k]["frac"] * sc[k]["n"])}/{sc[k]["n"]}')"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, 'w').write(s)
# ---- summary text
p = f'{W}/notes/report_v2_summary.txt'
s = open(p).read()
old = s[s.index("2. **An encoder that can compute anything"):s.index("3. **A local encoder")]
new = """2. **An encoder that can compute anything usually needs about the output's own bits at every layer.** Across layers
   and nets the median gap between the unrestricted curve and the output's own curve of the same net is {UDEV1} bit at
   10% error and {UDEV2} bit at 1% ({NUDEV} layer-net pairs). There are {UEXC} bits. In these cases the trained
   decoders did not find precise enough preimages; the theory (FORMAL 4.1) only bounds reachability, so these
   gaps are observations, not proofs that the shortcut fails. The bits are small: {U16_1} for 10% and {U16_2} for 1% on
   16x16 (output {O16_1} / {O16_2}).
"""
s = s.replace(old, new)
s = s.replace("""3. **A local encoder (one ReLU layer as wide as the net) needs more bits the closer the layer is to the input:
   a little more at L/2, clearly more at L/4, and very many more at the input.** Bits for 10% / 1% error (median over
   seeds): {LOCAL_LINES}""", """3. **A local encoder (one ReLU layer as wide as the net) needs more bits the closer the layer is to the input:
   a little more at L/2, clearly more at L/4, and very many more at the input** (best-found curves; on all 12 ReLU
   nets the count does not rise with depth, P1.3). Bits for 10% / 1% error (median over seeds; the single registered
   model r0 is in section 2): {LOCAL_LINES}""")
a = s.index("6. **How sure we are**")
b = s.index("7. **Controls.**")
new6 = """6. **How sure we are (best-found curves; the requirement of one model for all prices is not met everywhere).**
   On every curve: three restarts, a model trained twice as long, a model twice as wide, refitted priors, an
   output-space centroid, the linear reference, and three separately trained single-price models (section 3).
   Restarts agree on {C1} points. A model trained twice as long is better by more than the tolerance on only the
   remaining points of {C2}, but it is the best code at many cells, so the single registered model sits a few tenths
   of a bit above the reported counts there (section 2). The 2x-wide unrestricted model is within tolerance on {C3}.
   Refitted priors are no better on {C4} (the few exceptions are up to 10% lower). The learned code is at or below
   the linear reference on {C7} of the points where it reaches the error level. Known answers: the output codes are
   within 0.3 bit of the Gaussian bound or below it ({KA1}); unrestricted matches output on {KA2} points; the
   linear net gives the Gaussian answer within 0.1 bit at every layer for both classes ({KA3}). Limits:
   (a) A local encoder twice as wide (outside the class; decoder and prior also doubled) needs fewer bits on
   {C3L_FAIL} of points, mostly at L/4 to L/2. The amendment separates the encoder's width from the decoder's.
   (b) One model for all prices is within 3% of the separately trained single-price models on {C6R0} spot checks
   ({C6LONG} for the 2x-steps model). Your requirement is therefore not met everywhere. The reported counts take the
   lower envelope of both, as registered; section 2 shows the single model too.
   (c) {NCOV} (target, cell) points are not covered: the learned curves stop before the target within the trained
   price range (breakdown in section 3).
   (d) Uncertainty: the spread between restarts (median {SPREAD} bit) is the only measured one. The selection over
   about ten curves per cell is not corrected for.
   The independent review (gpt-6-astra) asked for three more checks: encoders whose ReLU gates start inside the data
   cloud, a converged output-space centroid, and the encoder's width separated from the decoder's. {CERT2}
"""
s = s[:a] + new6 + s[b:]
s = s.replace("""   error at l = 15, 12, 8, 4, 0; output {TANH_OUT}). Even the unrestricted encoder follows the output's curve only down
   to an error that grows toward the input: a decoder cannot invert a chaotic map precisely, so the shortcut breaks
   (figs/P1_curves_tanh4_16x16.png).""", """   error at l = 15, 12, 8, 4, 0; output {TANH_OUT}). The trained unrestricted codes follow the output's curve only down
   to an error that grows toward the input; below it they need about the local bits (the decoders did not find
   precise preimages in the chaotic map; figs/P1_curves_tanh4_16x16.png).""")
s = s.replace("""   itself ({FEI}), and at l <= 8 no real-valued code reaches 10% error within the price range. In the linear net
   every layer, in both classes, needs exactly the Gaussian answer ({LIN}).""", """   itself ({FEI}), and at l <= 8 none of the trained real-valued codes reached 10% error within the price range. In
   the linear net every layer, in both classes, needs the Gaussian answer to within 0.1 bit ({LIN}). One seed per
   control.""")
open(p, 'w').write(s)
print('ok')
