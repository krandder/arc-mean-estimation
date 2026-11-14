"""Score the registered B-ARC predictions (PREREG.md, Part B-ARC) -> results/BARC_scores.json. Implements the registered
rules literally; written after partial logs of net 4000 (pair lines) were seen, before either final JSON existed.
'Pairs with l >= 16' = pairs whose source layer is >= 16 (16-20 ... 31-32, 16-24, 24-32, 16-32).
BA.1 R2_lin_w >= 0.9 and R2_mlp_w - R2_lin_w <= 0.05 for every such pair, on both nets.
BA.2 acc_mlp_w - acc_ltf_w <= 0.03 for every such pair, on both nets.
BA.3 at rho = 0.999: bit_flip_frac(l = 31) <= 2 * bit_flip_frac(l = 8), on both nets."""
import json
import os

S = {}
nets = {s: (json.load(open(f'runs/B_arc_{s}.json')) if os.path.exists(f'runs/B_arc_{s}.json') else None)
        for s in (4000, 4001)}
dev = json.load(open('runs_dev/B_arc_9100.json')) if os.path.exists('runs_dev/B_arc_9100.json') else None


def late(d):
    return {k: v for k, v in d['pairs'].items() if int(k.split('-')[0]) >= 16}


def ba1(d):
    rows = {k: (round(v['R2_lin_w'], 3), round(v['R2_mlp_w'] - v['R2_lin_w'], 3)) for k, v in late(d).items()}
    return rows, all(a >= 0.9 and b <= 0.05 for a, b in rows.values())


def ba2(d):
    rows = {k: round(v['acc_mlp_w'] - v['acc_ltf_w'], 4) for k, v in late(d).items()}
    return rows, all(x <= 0.03 for x in rows.values())


def ba3(d):
    a = d['avalanche']['0.999']
    f8, f31 = a['8']['bit_flip_frac'], a['31']['bit_flip_frac']
    return dict(f8=f8, f31=f31, ratio=f31 / f8), f31 <= 2 * f8


for name, fn in (('BA.1', ba1), ('BA.2', ba2), ('BA.3', ba3)):
    ent, hits = {}, []
    for s, d in nets.items():
        if d is None:
            continue
        rows, h = fn(d)
        ent[str(s)] = dict(rows=rows, hit=h)
        hits.append(h)
    if dev is not None:
        ent['dev9100'] = dict(zip(('rows', 'hit'), fn(dev)))
    ent['hit'] = (all(hits) if len(hits) == 2 else (False if (hits and not all(hits)) else None))
    S[name] = ent
os.makedirs('results', exist_ok=True)
json.dump(S, open('results/BARC_scores.json', 'w'), indent=1)
for k, v in S.items():
    h = v['hit']
    print(k, 'HIT' if h is True else ('MISS' if h is False else 'n/a'), json.dumps({kk: vv for kk, vv in v.items() if kk != 'hit'})[:600])
