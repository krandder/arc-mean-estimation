"""score_P1.py: implement the registered C6 fallback (if C6 fails on > 10% of points, R* is the lower envelope of the
variable-rate curves and the fixed-lambda points). Written before any P1 evaluation result was seen."""
p = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/score_P1.py'
s = open(p).read()
old = """    info[key] = dict(R=R, slope=slopes(R), flags=flags, RG=d['RG'], curves=c)"""
new = """    info[key] = dict(R=R, slope=slopes(R), flags=flags, RG=d['RG'], curves=c, d=d)"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """S['C6_fallback_triggered'] = (S['C6']['frac'] is not None and S['C6']['frac'] < 0.9)
"""
new = """S['C6_fallback_triggered'] = (S['C6']['frac'] is not None and S['C6']['frac'] < 0.9)
if S['C6_fallback_triggered']:
    # registered fallback: R* = lower envelope of the variable-rate curves (class's codes) and the fixed-lambda points
    for key, v in info.items():
        d = v['d']
        pts = []
        for g in d['groups'].values():
            for name, cv in g['curves'].items():
                if name == 'wide' and d['cls'] == 'local':
                    continue
                pts += list(zip(cv['rate'], cv['nmse']))
        pts += [(x['rate'], x['nmse']) for x in d['groups'].get('G1', {}).get('fixed', [])]
        R2 = {str(D): rate_at([p[0] for p in pts], [p[1] for p in pts], D) for D in DGRID}
        v['R'] = {k: (min(x for x in (v['R'][k], R2[k]) if x is not None) if (v['R'][k] is not None or R2[k] is not None)
                      else None) for k in v['R']}
        v['slope'] = slopes(v['R'])
"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, 'w').write(s)
print('patched')
