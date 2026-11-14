"""score_P1v2.py fixes after review r2b: C5v2 requires convergence; source attribution; same candidates for the
log-linear secondary; table shows the source."""
p = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/score_P1v2.py'
s = open(p).read()
old = """            conv = abs(q['train_loss_q4'] - q['train_loss_q3']) <= 0.02 * max(q['train_loss_q3'], 1e-12)
            ok = q['nmse_model'] <= 1.05 * q['nmse_corrected'] + 0.002
            C['C5v2'].append(ok)
            if not ok:
                flags.append(f'C5v2@{q["lam"]}')
            if not conv:
                flags.append(f'C5v2conv@{q["lam"]}')"""
new = """            conv = abs(q['train_loss_q4'] - q['train_loss_q3']) <= 0.02 * max(q['train_loss_q3'], 1e-12)
            ok = q['nmse_model'] <= 1.05 * q['nmse_corrected'] + 0.002
            if not conv:                                  # unconverged comparator: neither pass nor fail
                NC['C5v2'] += 1
                flags.append(f'C5v2conv@{q["lam"]}')
                continue
            C['C5v2'].append(ok)
            if not ok:
                flags.append(f'C5v2@{q["lam"]}')"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """    for D in DGRID:
        s = str(D)
        per = {nm: cross(c[nm]['rate'], c[nm]['nmse'], D) for nm in names}
        best = min((r for r in per.values() if r is not None), default=None)
        pooled = cross([p[0] for p in pts + fx], [p[1] for p in pts + fx], D)
        R[s] = min((r for r in (best, pooled) if r is not None), default=None)
        src[s] = ('fixed' if (fallback and pooled is not None and (best is None or pooled < best - 1e-9)) else
                  (min((k for k in per if per[k] is not None), key=lambda k: per[k]) if best is not None else None))
        R_ll[s] = min((r for r in (cross(c[nm]['rate'], c[nm]['nmse'], D, 'll') for nm in names) if r is not None), default=None)"""
new = """    for D in DGRID:
        s = str(D)
        per = {nm: cross(c[nm]['rate'], c[nm]['nmse'], D) for nm in names}
        best = min((r for r in per.values() if r is not None), default=None)
        pooled_vr = cross([p[0] for p in pts], [p[1] for p in pts], D)
        pooled = cross([p[0] for p in pts + fx], [p[1] for p in pts + fx], D)
        cands = [r for r in (best, pooled_vr, pooled) if r is not None]
        R[s] = min(cands) if cands else None
        if R[s] is None:
            src[s] = None
        elif fallback and pooled is not None and pooled < min(r for r in (best, pooled_vr) if r is not None) - 1e-9 \\
                if any(r is not None for r in (best, pooled_vr)) else (pooled is not None):
            src[s] = 'fixed'
        elif pooled_vr is not None and (best is None or pooled_vr < best - 1e-9):
            src[s] = 'pooled'
        else:
            src[s] = min((k for k in per if per[k] is not None), key=lambda k: per[k])
        per_ll = [cross(c[nm]['rate'], c[nm]['nmse'], D, 'll') for nm in names]
        per_ll += [cross([p[0] for p in pts], [p[1] for p in pts], D, 'll'),
                   cross([p[0] for p in pts + fx], [p[1] for p in pts + fx], D, 'll')]
        R_ll[s] = min((r for r in per_ll if r is not None), default=None)"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """         '| net | seed | l | class | R*(0.3) | R*(0.1) | R*(0.03) | R*(0.01) | R*(0.003) | R*(0.001) | R_r0(0.1) / (0.01) | '
         'lin(0.1) / (0.01) | slope .1->.03 | .03->.01 | .01->.003 | R_G(0.1) / (0.01) | flags |', '|' + '---|' * 17]"""
new = """         '| net | seed | l | class | R*(0.3) | R*(0.1) | R*(0.03) | R*(0.01) | R*(0.003) | R*(0.001) | R_r0(0.1) / (0.01) | '
         'lin(0.1) / (0.01) | slope .1->.03 | .03->.01 | .01->.003 | R_G(0.1) / (0.01) | source of R*(0.1) / (0.01) | flags |',
         '|' + '---|' * 18]"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """                 f' | {v["d"]["RG"]["0.1"]:.1f} / {v["d"]["RG"]["0.01"]:.1f} | {" ".join(sorted(set(v["flags"]))) or "ok"} |')"""
new = """                 f' | {v["d"]["RG"]["0.1"]:.1f} / {v["d"]["RG"]["0.01"]:.1f} | {v["src"]["0.1"]} / {v["src"]["0.01"]} | '
                 f'{" ".join(sorted(set(v["flags"]))) or "ok"} |')"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, 'w').write(s)
print('patched')
