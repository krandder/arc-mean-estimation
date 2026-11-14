"""Registered prediction checks for the scale-mode lane (PREREG.md section 5; hashed with score.py before scoring).
verdicts(res) -> list of dict(id, text, result in {HOLDS, FAILS, UNDETERMINED}, measured)."""
import math


def _s(res, setname, method):
    return res['per_set'].get(setname, {}).get(method)


def _rows(res, setname):
    return res['per_net'].get(setname, [])


def _count(rows, method, pred):
    n_ok, n_all = 0, 0
    for r in rows:
        m = r['m'].get(method)
        if m is None:
            continue
        v = pred(m, r)
        if v is None:
            continue
        n_all += 1
        n_ok += int(bool(v))
    return n_ok, n_all


def V(id_, text, ok, measured):
    if ok is None:
        return dict(id=id_, text=text, result='UNDETERMINED', measured=measured)
    return dict(id=id_, text=text, result='HOLDS' if ok else 'FAILS', measured=measured)


def verdicts(res):
    out = []
    E2 = ('E2_n32', 'E2_n64', 'E2_n128')
    E3 = [k for k in ('E3_n64', 'E3_n128', 'E3_n256', 'E3_n512', 'E3_n1024') if res['per_net'].get(k)]

    # ---------------- the claim's own predictions, transferred to our sets
    # C1: LVTV2 beats naive MC at equal FLOPs (the claim's statistic: MC at the mean cost / mean nMSE > 1) in every cell.
    for sets, tag in ((('E1',) + E2, 'L=n/8'), (tuple(E3), 'L=n/4'), (('E4',), '1024x16')):
        vals = {s: (_s(res, s, 'LVTV2') or {}).get('G_MC_of_mean') for s in sets}
        ok = None if (not vals or any(v is None for v in vals.values())) else all(v > 1 for v in vals.values())
        out.append(V(f'C1 {tag}', 'claim: LVTV2 beats naive MC at its own FLOPs in every cell (MC / mean nMSE > 1)', ok,
                     {s: v for s, v in vals.items()}))
    # C2: the scale-law ladder improves with order: SL3 < LVTV2 on >= 80% of nets in each set where SL3 ran.
    for s in ('E1',) + E2 + tuple(E3) + ('E4',):
        k, n = _count(_rows(res, s), 'SL3', lambda m, r: (m['e'] < r['m']['LVTV2']['e']) if 'LVTV2' in r['m'] else None)
        if n:
            out.append(V(f'C2 {s}', 'claim: SL3 < LVTV2 on >= 80% of nets', k >= 0.8 * n, f'{k}/{n}'))
    # C3: the scale law helps ARC's factored K3: SL3 < ARC k3f on >= 80% of nets.
    for s in ('E1',) + E2 + tuple(E3) + ('E4',):
        k, n = _count(_rows(res, s), 'SL3', lambda m, r: (m['e'] < r['m']['ARC-k3f']['e']) if 'ARC-k3f' in r['m'] else None)
        if n:
            out.append(V(f'C3 {s}', 'claim: SL3 < ARC k3f on >= 80% of nets', k >= 0.8 * n, f'{k}/{n}'))
    # C4: LVTV2 more accurate than ARC's best at <= its cost (median R_ARC > 1) on the diagonal cells.
    for s in E3:
        r = (_s(res, s, 'LVTV2') or {}).get('med_R_ARC')
        out.append(V(f'C4 {s}', 'claim: LVTV2 beats the best ARC variant at <= its cost (median ratio > 1)',
                     None if r is None else r > 1, r))
    # C5: at 1024x16 LVTV2 is worse than ARC k2a on >= 9 of 12 nets.
    k, n = _count(_rows(res, 'E4'), 'LVTV2', lambda m, r: (m['e'] > r['m']['ARC-k2a']['e']) if 'ARC-k2a' in r['m'] else None)
    out.append(V('C5 E4', 'claim scope: LVTV2 worse than ARC k2a at 1024x16 on >= 9/12 nets', (k >= 9) if n == 12 else None,
                 f'{k}/{n}'))
    # C6: on the diagonal the margin over naive MC narrows with width (slope of log median G_MC on log n < 0).
    w = res['width'].get('L=n/4 LVTV2 G_MC')
    out.append(V('C6 L=n/4', 'claim: LVTV2 margin over naive MC narrows with width (exponent < 0)',
                 None if (w is None or len(w['widths']) < 3) else w['slope'] < 0, w))

    # ---------------- our predictions
    # P1 (E1): the K = 2-type window. LVTV2 beats RQMC at its own cost on >= 4/5 nets, and RQMC reaches LVTV2's error
    # at <= 5x LVTV2's cost on >= 4/5 nets.
    a, n1 = _count(_rows(res, 'E1'), 'LVTV2', lambda m, r: m.get('G_RQ', 0) > 1)
    b, n2 = _count(_rows(res, 'E1'), 'LVTV2', lambda m, r: m.get('X_RQ', 1e9) <= 5)
    out.append(V('P1a E1', 'LVTV2 beats RQMC at its own cost on >= 4/5 nets', (a >= 4) if n1 == 5 else None, f'{a}/{n1}'))
    out.append(V('P1b E1', 'RQMC reaches LVTV2 error at <= 5x its cost on >= 4/5 nets', (b >= 4) if n2 == 5 else None, f'{b}/{n2}'))
    # P2 (E1): at the Phase 1 budget (64,850 passes) RQMC is >= 20x below the best affordable scale-law method, 5/5 nets.
    rat = []
    for r in _rows(res, 'E1'):
        cands = [r['m'][k]['e'] for k in ('LVTV2', 'LVT', 'LVTV2f1', 'SL3') if k in r['m'] and r['m'][k]['C'] <= 64850]
        if cands and 'rqmc' in r:
            Ns, es = r['rqmc']['N'], r['rqmc']['e']
            import numpy as np
            if 64850 >= Ns[-1]:
                rq = es[-1] * Ns[-1] / 64850
            else:
                rq = float(np.exp(np.interp(math.log(64850), np.log(Ns), np.log(es))))
            rat.append(min(cands) / rq)
    out.append(V('P2 E1', 'at 64,850 passes RQMC >= 20x below the best affordable scale-law method on 5/5 nets',
                 (len(rat) == 5 and min(rat) >= 20) if len(rat) == 5 else None, [round(x, 1) for x in rat]))
    # P3: the scale-law ladder exponent gamma_SL (LVTV2 -> SL3, median over nets) < 1 at n = 64, 128, 256 (L = n/8),
    # and < 0.6 at n = 256.
    g = {s: (res['per_set'].get(s, {}).get('gamma_SL') or {}).get('median') for s in ('E2_n64', 'E2_n128', 'E1')}
    ok = None if any(v is None for v in g.values()) else (all(v < 1 for v in g.values()) and g['E1'] < 0.6)
    out.append(V('P3 L=n/8', 'gamma_SL median < 1 at n = 64, 128, 256 and < 0.6 at n = 256', ok, g))
    # P4: along L = n/8 the gain of LVTV2 over MC at its own cost does not grow with width (slope < 0).
    w = res['width'].get('L=n/8 LVTV2 G_MC')
    out.append(V('P4 L=n/8', 'width exponent of median G_MC(LVTV2) along L = n/8 (n = 32-256) < 0',
                 None if w is None else w['slope'] < 0, w))
    # P5: along L = n/8 the gain over RQMC does not grow fast: width exponent of median G_RQ(LVTV2) < 0.5.
    w = res['width'].get('L=n/8 LVTV2 G_RQ')
    out.append(V('P5 L=n/8', 'width exponent of median G_RQ(LVTV2) along L = n/8 < 0.5', None if w is None else w['slope'] < 0.5, w))
    # P6: SL3 loses to RQMC at its own cost on >= 4/5 E1 nets and on >= 6/8 nets at n = 128.
    a, n1 = _count(_rows(res, 'E1'), 'SL3', lambda m, r: m.get('G_RQ', 9) < 1)
    b, n2 = _count(_rows(res, 'E2_n128'), 'SL3', lambda m, r: m.get('G_RQ', 9) < 1)
    out.append(V('P6', 'SL3 loses to RQMC at its own cost on >= 4/5 nets at 256x32 and >= 6/8 at 128x16',
                 (a >= 4 and b >= 6) if (n1 == 5 and n2 == 8) else None, f'{a}/{n1}, {b}/{n2}'))
    out.extend(verdicts_e3(res, E3))
    out.extend(verdicts_e4(res))
    out.extend(escape(res))
    return out


P7B_MAX = 1.5      # registered in PREREG 5.3
P7C_MAX = 0.25
CLAIM_GMC = {'E3_n64': 2.17, 'E3_n128': 1.52, 'E3_n256': 1.51, 'E3_n512': 1.41, 'E3_n1024': 1.21}   # claim, L accounting


def verdicts_e3(res, E3):
    """PREREG section 5.3 (the claim's diagonal L = n/4, fresh nets)."""
    out = []
    # P7a: the claim's margin over naive MC replicates within a factor 2 at every E3 width run (median G_MC).
    vals = {s: (_s(res, s, 'LVTV2') or {}).get('med_G_MC') for s in E3}
    ok = None if (not E3 or any(v is None for v in vals.values())) else all(0.5 * CLAIM_GMC[s] <= v <= 2 * CLAIM_GMC[s] for s, v in vals.items())
    out.append(V('P7a L=n/4', "the claim's margin over naive MC replicates within 2x at every E3 width (median G_MC(LVTV2))", ok, vals))
    # P7b: against RQMC the margin is at most marginal at n >= 256: median G_RQ(LVTV2) < P7B_MAX at every E3 width >= 256.
    big = [s for s in E3 if int(s.split('_n')[1]) >= 256]
    vals = {s: (_s(res, s, 'LVTV2') or {}).get('med_G_RQ') for s in big}
    ok = None if (not big or any(v is None for v in vals.values())) else all(v < P7B_MAX for v in vals.values())
    out.append(V('P7b L=n/4', f'median G_RQ(LVTV2) < {P7B_MAX} at every E3 width >= 256', ok, vals))
    # P7c: the width exponent of median G_RQ(LVTV2) along E3 is < P7C_MAX (point estimate; needs >= 3 widths).
    w = res['width'].get('L=n/4 LVTV2 G_RQ')
    out.append(V('P7c L=n/4', f'width exponent of median G_RQ(LVTV2) along L = n/4 < {P7C_MAX}',
                 None if (w is None or len(w['widths']) < 3) else w['slope'] < P7C_MAX, w))
    # P7d: SL3 loses to RQMC at its own cost on >= 75% of nets at 128x32 and 256x64.
    res_d = []
    for s in ('E3_n128', 'E3_n256'):
        k, n = _count(_rows(res, s), 'SL3', lambda m, r: m.get('G_RQ', 9) < 1)
        res_d.append((s, k, n))
    ok = None if any(n == 0 for _, _, n in res_d) else all(k >= 0.75 * n for _, k, n in res_d)
    out.append(V('P7d L=n/4', 'SL3 loses to RQMC at its own cost on >= 75% of nets at 128x32 and 256x64', ok,
                 {s: f'{k}/{n}' for s, k, n in res_d}))
    return out


def verdicts_e4(res):
    """PREREG section 5.4 (Phase 2 public MLPs 0-11, 1024 x 16)."""
    import numpy as np
    out = []
    rows = _rows(res, 'E4')
    full = 65536.0
    # P8a: COV and ARC k2 give the same estimate (relative max difference <= 1e-9) on 12/12.
    k, n = 0, 0
    for r in rows:
        if 'COV' in r['m'] and 'ARC-k2' in r['m']:
            n += 1
            k += int(abs(r['m']['COV']['e'] - r['m']['ARC-k2']['e']) <= 1e-6 * r['m']['ARC-k2']['e'])
    out.append(V('P8a E4', 'COV (starter kit) and ARC k2 give the same error (to 1e-6 relative) on 12/12', (k == 12) if n == 12 else None, f'{k}/{n}'))
    s = _s(res, 'E4', 'COV') or {}
    v = s.get('mean_raw_mse')
    out.append(V('P8b E4', 'COV mean raw final-layer MSE in [3.0e-6, 5.5e-6]', None if v is None else 3.0e-6 <= v <= 5.5e-6, v))
    k, n = _count(rows, 'COV', lambda m, r: m.get('G_RQ', 0) >= 3)
    out.append(V('P8c E4', 'COV beats RQMC at its own cost by >= 3x on 12/12', (k == 12) if n == 12 else None, f'{k}/{n}'))
    k1, n1 = _count(rows, 'COV', lambda m, r: (r['rqmc_full_raw'] < m['raw_mse']) if 'rqmc_full_raw' in r else None)
    k2, n2 = _count(rows, 'ARC-k2a', lambda m, r: (r['rqmc_full_raw'] < m['raw_mse']) if 'rqmc_full_raw' in r else None)
    out.append(V('P8d E4', 'full-budget RQMC (2^16) below COV in raw MSE on 12/12 and below ARC k2a on >= 9/12',
                 (k1 == 12 and k2 >= 9) if (n1 == 12 and n2 == 12) else None, f'COV {k1}/{n1}, k2a {k2}/{n2}'))
    k, n = _count(rows, 'COV', lambda m, r: 0.1 * m['raw_mse'] < r['mc_full_raw'])
    out.append(V('P8e E4', "claim (b) in the contest metric: COV's adjusted score (0.1 x raw) below full-budget MC's on >= 11/12",
                 (k >= 11) if n == 12 else None, f'{k}/{n}'))
    k3 = [r for r in rows if 'ARC-k3f' in r['m']]
    ok = None
    meas = None
    if len(k3) == 6:
        a = all(r['m']['ARC-k3f']['raw_mse'] <= 1e-7 for r in k3)
        b = all(r['rqmc_full_raw'] >= 5 * r['m']['ARC-k3f']['raw_mse'] for r in k3 if 'rqmc_full_raw' in r)
        c = all(r['m']['ARC-k3f']['C'] > full for r in k3)
        ok = a and b and c
        meas = dict(raw=[r['m']['ARC-k3f']['raw_mse'] for r in k3], rqmc_full_over_k3f=[r['rqmc_full_raw'] / r['m']['ARC-k3f']['raw_mse'] for r in k3 if 'rqmc_full_raw' in r],
                    C=[r['m']['ARC-k3f']['C'] for r in k3])
    out.append(V('P8f E4', 'ARC k3f (MLPs 0-5): raw MSE <= 1e-7, >= 5x below full-budget RQMC, and costs > 65,536 passes, on 6/6', ok, meas))
    g = [r['gamma_ARC'] for r in k3 if 'gamma_ARC' in r]
    out.append(V('P8g E4', 'gamma_ARC (k2a -> k3f) median over MLPs 0-5 in [0.6, 1.0]', (0.6 <= float(np.median(g)) <= 1.0) if len(g) == 6 else None,
                 g))
    # N2 (decision for claim (b), PREREG section 6): full-budget RQMC beats every deductive method run here that fits the
    # budget in ARC's counter, on >= 10 of 12 MLPs.
    k, n, det = 0, 0, []
    for r in rows:
        if 'rqmc_full_raw' not in r:
            continue
        aff = [(m['raw_mse'], name) for name, m in r['m'].items() if m['C'] <= full and 'raw_mse' in m]
        if not aff:
            continue
        best = min(aff)
        n += 1
        k += int(r['rqmc_full_raw'] < best[0])
        det.append((r['net'], best[1], round(best[0] / r['rqmc_full_raw'], 2)))
    out.append(V('N2 E4', 'our negative applies at Phase 2: full-budget RQMC beats every affordable deductive method run here on >= 10/12',
                 (k >= 10) if n == 12 else None, dict(count=f'{k}/{n}', best_affordable_over_rqmc=det)))
    return out


def escape(res):
    """PREREG section 6: the registered decision rule."""
    out = []
    g128 = (res['per_set'].get('E2_n128', {}).get('gamma_SL') or {}).get('median')
    g256 = (res['per_set'].get('E1', {}).get('gamma_SL') or {}).get('median')
    k, n = _count(_rows(res, 'E1'), 'SL3', lambda m, r: m.get('G_RQ', 0) > 1)
    d1 = None if (g128 is None or g256 is None or n != 5) else (g128 >= 0.9 and g256 >= 0.9 and k >= 4)
    out.append(V('D1', 'ESCAPE route 1: gamma_SL >= 0.9 at n = 128 and 256 (L = n/8) AND SL3 beats RQMC at its own cost on >= 4/5 E1 nets',
                 d1, dict(gamma_SL_128=g128, gamma_SL_256=g256, SL3_beats_RQMC=f'{k}/{n}')))
    E3 = [s for s in ('E3_n64', 'E3_n128', 'E3_n256', 'E3_n512', 'E3_n1024') if res['per_net'].get(s)]
    meds = {s: (_s(res, s, 'LVTV2') or {}).get('med_G_RQ') for s in E3}
    w = res['width'].get('L=n/4 LVTV2 G_RQ')
    d2 = None
    if len(E3) >= 3 and w is not None and all(v is not None for v in meds.values()):
        d2 = all(v > 1 for v in meds.values()) and w['lo'] > 0
    out.append(V('D2', 'ESCAPE route 2: on L = n/4, median G_RQ(LVTV2) > 1 at every width AND its width exponent has bootstrap CI lower bound > 0',
                 d2, dict(med_G_RQ=meds, exponent=w)))
    if d1 is True or d2 is True:
        verdict = True
    elif d1 is False and d2 is False:
        verdict = False
    else:
        verdict = None
    out.append(V('D', 'the scale-mode claim escapes the ladder (D1 or D2)', verdict, None))
    return out
