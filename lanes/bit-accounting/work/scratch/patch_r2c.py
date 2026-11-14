"""Apply review r2c: primary (time-sharing) crossings for the post-pass comparisons, measured extrema and counts,
envelope wording, coverage from the manifest, softer certificate and width claims."""
W = '/home/agent/workspaces/mats/work/bit-accounting'
p = f'{W}/scratch/summary_fill.py'
s = open(p).read()
old = """    for k, val in d.items():
        text = text.replace('{' + k + '}', val)
    return text"""
new = """    # ---- review r2c: primary crossings for post-pass comparisons, extrema, gaps, coverage
    def ts(rates, nmse, D):
        pts = sorted((r, e) for r, e in zip(rates, nmse) if r is not None and e is not None and np.isfinite(r) and np.isfinite(e))
        env, best = [], float('inf')
        for r, e in pts:
            if e < best:
                env.append((max(r, 0.0), e))
                best = e
        for i, (r, e) in enumerate(env):
            if e <= D:
                if i == 0:
                    return r
                r0, e0 = env[i - 1]
                return r0 + (e0 - D) / (e0 - e) * (r - r0)
        return None
    gain2, wd2, gaps = _dd(list), [], _dd(list)
    nomark = 0
    for f in _g2.glob(f'{W}/runs/P1X/X_*.json'):
        x = json.load(open(f))
        if 'explorer_init_data' not in x:
            nomark += 1
        if x['cls'] != 'local' or 'explorer' not in x:
            continue
        dd = json.load(open(f'{W}/runs/P1/P_' + f.split('X_')[1]))
        if dd['netkind'] != 'relu':
            continue
        L, l = dd['L'], dd['l']
        pos = 'input' if l == 0 else ('L/4' if l == L // 4 else ('L/2' if l == L // 2 else 'late'))
        cv = {}
        for g in dd['groups'].values():
            cv.update(g['curves'])
        if 'refit' in dd:
            cv['r0_refit'] = dict(rate=[min(q['rate_trained_B'], q['rate_refit_mix8'], q['rate_refit_fullgauss'])
                                        for q in dd['refit']], nmse=cv['r0']['nmse'])
        for D in (0.1, 0.01):
            an = [ts(cv[k]['rate'], cv[k]['nmse'], D) for k in ('r0', 'r1', 'r2', 'long', 'r0_refit') if k in cv]
            an = [a for a in an if a is not None]
            ex = [ts(c['rate'], c['nmse'], D) for c in x['explorer'].values()]
            ex = [e for e in ex if e is not None]
            if an and ex:
                gain2[(pos, D)].append(1.0 - min(ex) / min(an))
            w, b = ts(x['wdec']['rate'], x['wdec']['nmse'], D), ts(cv['r0']['rate'], cv['r0']['nmse'], D)
            if w is not None and b is not None:
                wd2.append(w - b)
    parts = []
    for pos in ('input', 'L/4', 'L/2', 'late'):
        g1, g2 = gain2.get((pos, 0.1), []), gain2.get((pos, 0.01), [])
        if g1 and g2:
            parts.append(f'{pos} {100 * np.median(g1):.0f}% / {100 * np.median(g2):.0f}% (n = {len(g1)})')
    d['EXPL'] = '; '.join(parts) if parts else 'pending'
    d['WDEC'] = (f'median {np.median(wd2):+.2f} bit, range {min(wd2):+.2f} to {max(wd2):+.2f} ({len(wd2)} points)'
                 if wd2 else 'pending')
    d['NOMARK'] = str(nomark)
    for k, c in cells.items():
        kind, n, L, sd, l, cls = k.split('_')
        if kind == 'relu' and cls == 'local':
            L, l = int(L), int(l)
            pos = 'input' if l == 0 else ('L/4' if l == L // 4 else ('L/2' if l == L // 2 else 'late'))
            for D in ('0.1', '0.01'):
                a, b = c['R_r0'].get(D), c['R'].get(D)
                if a is not None and b is not None:
                    gaps[pos].append(a - b)
    d['R0GAP'] = '; '.join(f'{pos} {np.median(gaps[pos]):.1f}' for pos in ('input', 'L/4', 'L/2', 'late') if gaps[pos])
    red = []
    import glob as _g3
    for f in _g3.glob(f'{W}/runs/P1/P_*.json'):
        for q in json.load(open(f)).get('refit', []):
            if q['rate_trained_B'] > 1.0:
                red.append(1.0 - min(q['rate_refit_mix8'], q['rate_refit_fullgauss']) / q['rate_trained_B'])
    d['C4MAX'] = f'{100 * max(red):.0f}%' if red else '-'
    exc7 = []
    for c in cells.values():
        for D in ('0.3', '0.1', '0.03', '0.01', '0.003', '0.001'):
            a, b = c['R'].get(D), c['R_linref'].get(D)
            if a is not None and b is not None and a > b + 1e-9:
                exc7.append(a - b)
    d['C7EXC'] = (f'{len(exc7)} points exceed it within that tolerance (by up to {max(exc7):.1f} bits)' if exc7 else
                  'none exceeds it')
    lg = [abs(c['R'][D] - c['RG'][D]) for k, c in cells.items() if k.startswith('linear_') for D in ('0.1', '0.03', '0.01')
          if c['R'].get(D) is not None]
    d['LINMAX'] = f'{max(lg):.2f}' if lg else '-'
    man_local = 0
    done_local = 0
    xs = {f.split('X_')[1][:-5] for f in _g2.glob(f'{W}/runs/P1X/X_*.json')}
    for k in cells:
        kind, n, L, sd, l, cls = k.split('_')
        if kind == 'relu' and cls == 'local':
            man_local += 1
            done_local += f'relu_n{n}_L{L}_s{sd}_l{l}_local' in xs
    d['XCOV'] = f'{done_local} of the {man_local} ReLU local cells'
    for k, val in d.items():
        text = text.replace('{' + k + '}', val)
    return text"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """    d['CERT2'] = (f'Coverage of these extra checks: {sc["coverage"]["certificates"]} cells (58 of the 60 ReLU local '
                  'cells; the controls\\' local cells and all unrestricted cells were not reached within the GPU budget).')"""
new = """    d['CERT2'] = (f'Coverage of these extra checks: {sc["coverage"]["certificates"]} cells ({{XCOV}}; the controls\\' local '
                  'cells and all unrestricted cells were not reached within the GPU budget).')"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, 'w').write(s)

p = f'{W}/notes/report_v2_summary.txt'
s = open(p).read()
reps = [
    ("""   bits-versus-accuracy curve, from one model per layer that takes the bit price as an input.""",
     """   bits-versus-accuracy curve. The registered method is one model per layer that takes the bit price as an input;
   the reported count R* is the best of several codes of the class (that model's restarts, a 2x-steps version,
   explorer restarts, and single-price models where they are better), and the single registered model r0 is given
   next to it."""),
    ("""   median saving at 10% / 1% error, by layer: {EXPL}. Decoder and prior width do not matter (width-n encoder with the
   wide decoder minus the base model: {WDEC}), so the gains of the 2x-wide local encoder come from the encoder's own
   width. The counts in this report include the explorer codes; better explorations of the class could lower the
   early-layer counts further.""",
     """   median saving at 10% / 1% error, by layer: {EXPL}. Widening only the decoder and prior gave little typical
   improvement (width-n encoder with the wide decoder minus the base model: {WDEC}), which supports, but does not
   prove, that the gains of the 2x-wide local encoder come from the encoder's own width. The counts in this report
   include the explorer codes; better explorations of the class could lower the early-layer counts further."""),
    ("""6. **How sure we are (best-found curves; the requirement of one model for all prices is not met everywhere).**""",
     """6. **How sure we are: these are best-found curves, not certified optima, and the one-model requirement is not met
   everywhere.** The certificates below test the anchored models; the explorer codes that set many early-layer counts
   got only their own restarts."""),
    ("""   points; it is nevertheless the best code at many cells, so the single registered model sits a few tenths of a bit
   above the reported counts there, more at the input layers (section 2).""",
     """   points. The single registered model r0 sits above the reported counts by a median of {R0GAP} bits (input, L/4,
   L/2, later local layers; mostly because the explorer and 2x-steps codes are better)."""),
    ("""   Refitted priors are no better on {C4} (the few exceptions are up to 10% lower). The learned code is at or below
   the linear reference on {C7} of the points where it reaches the error level.""",
     """   Refitted priors are no better (within 5%) on {C4} points (the largest exception is {C4MAX} lower). The learned code
   is within 0.3 bit or 5% of the linear reference or below it on {C7} of the points where it reaches the error level;
   {C7EXC}."""),
    ("""linear net gives the Gaussian answer within 0.1 bit at every layer for both classes ({KA3}).""",
     """linear net gives the Gaussian answer within {LINMAX} bit at every layer for both classes ({KA3})."""),
    ("""   cloud (point 5), a converged output-space centroid ({CEN2}: the decoders are close to optimal for their codes),
   and the encoder's width separated from the decoder's (point 5). {CERT2}""",
     """   cloud (point 5), an output-space residual correction around r0's reconstruction ({CEN2}; a fitted correction
   improved r0 little, which is consistent with, not proof of, a near-optimal decoder), and the encoder's width
   separated from the decoder's (point 5). {CERT2} The explorer initial fit used evaluation samples in {NOMARK} of
   these cells (pilot samples afterwards)."""),
    ("""   the linear net every layer, in both classes, needs the Gaussian answer to within 0.1 bit ({LIN}). One seed per
   control.""",
     """   the linear net every layer, in both classes, needs the Gaussian answer to within {LINMAX} bit ({LIN}). One seed
   per control."""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(p, 'w').write(s)

p = f'{W}/scratch/build_report.py'
s = open(p).read()
old = """         '## 3. How we know the curves are as good as reasonably possible (certificates; registered in PREREG P1, P1-A)', '',"""
new = """         '## 3. What the certificates show, and what they do not (registered in PREREG P1, P1-A)', '',"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """         'Counts are conservative (time-sharing between achieved points) and take the best code of the class found by any '
         'variant (the registered single model r0 differs by at most a few tenths of a bit except where noted in '
         'results/P1_table.md). Every cell, seed and certificate flag: results/P1_table.md; curves: '
         'figs/P1_curves_*.png.', ''] + tab + ['',"""
new = """         'Counts are conservative (time-sharing between achieved points). "Bits" columns = R*, the best code of the class '
         'found by any variant (an envelope over several models); "single model r0" = the registered single '
         'lambda-conditioned model, which is often several bits higher at the early layers. Every cell, seed, source and '
         'certificate flag: results/P1_table.md; curves: figs/P1_curves_*.png.', ''] + tab + ['',"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, 'w').write(s)
print('patched')
