"""score_P1v2.py: include the P1-B explorer curves (runs/P1Y/Y_*.json) as codes of the local class, and score B1, B2.
Written before any P1-B result was read."""
p = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/score_P1v2.py'
s = open(p).read()
old = """XRUNS = sys.argv[2] if len(sys.argv) > 2 else 'runs/P1X'"""
new = """XRUNS = sys.argv[2] if len(sys.argv) > 2 else 'runs/P1X'
YRUNS = sys.argv[3] if len(sys.argv) > 3 else 'runs/P1Y'"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """for p in sorted(glob.glob(f'{XRUNS}/X_*.json')):
    x = json.load(open(p))
    xcells[(x['netkind'], x['n'], x['L'], x['seed'], x['l'], x['cls'])] = x"""
new = """for p in sorted(glob.glob(f'{XRUNS}/X_*.json')):
    x = json.load(open(p))
    xcells[(x['netkind'], x['n'], x['L'], x['seed'], x['l'], x['cls'])] = x
ycells = {}
for p in sorted(glob.glob(f'{YRUNS}/Y_*.json')):
    y = json.load(open(p))
    ycells[(y['netkind'], y['n'], y['L'], y['seed'], y['l'], y['cls'])] = y"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """    x = xcells.get(key)
    c = curves_of(d, x)
    names = [k for k in ('r0', 'r1', 'r2', 'long', 'r0_refit', 'x0', 'x1', 'x2', 'wdec') if k in c]"""
new = """    x = xcells.get(key)
    c = curves_of(d, x)
    yv = ycells.get(key)
    if yv is not None:
        for k2, cv in yv['curves'].items():
            c['y' + k2] = cv
    names = [k for k in ('r0', 'r1', 'r2', 'long', 'r0_refit', 'x0', 'x1', 'x2', 'wdec') if k in c] + \\
        sorted(k for k in c if k.startswith('y'))"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """os.makedirs('results', exist_ok=True)
json.dump(dict(scores=S, cells="""
new = """b1, b2 = [], []
for key, v in info.items():
    yv = ycells.get(key)
    if yv is None:
        continue
    c = v['c']
    xa = [cross(c[k]['rate'], c[k]['nmse'], 0.1) for k in ('x0', 'x1', 'x2') if k in c]
    xa = [q for q in xa if q is not None]
    yb = [cross(c[k]['rate'], c[k]['nmse'], 0.1) for k in c if k.startswith('yx') and not k.startswith('yxl')]
    yb = [q for q in yb if q is not None]
    yl = [cross(c[k]['rate'], c[k]['nmse'], 0.1) for k in c if k.startswith('yxl')]
    yl = [q for q in yl if q is not None]
    if key[0] == 'relu' and key[4] in (0, key[2] // 4, key[2] // 2) and xa and yb:
        b1.append(min(yb) >= 0.95 * min(xa))
    if yb and yl:
        b2.append(min(yl) >= min(yb) - max(0.5, 0.05 * min(yb)))
S['B1'] = dict(n=len(b1), hits=int(sum(b1)), hit=(bool(b1) and float(np.mean(b1)) >= 0.75) if b1 else 'pending')
S['B2'] = dict(n=len(b2), hits=int(sum(b2)), hit=(bool(b2) and float(np.mean(b2)) >= 0.75) if b2 else 'pending')
os.makedirs('results', exist_ok=True)
json.dump(dict(scores=S, cells="""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, 'w').write(s)
print('patched')
