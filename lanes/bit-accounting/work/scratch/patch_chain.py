"""Patch gpu_src/scripts/run_chain.py: record mean errors, save models, add the part-C deductive estimator.
The S2 measurements themselves (training, statistics) are unchanged."""
p = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_chain.py'
s = open(p).read()
old = """                own, chain, agree = [], [], []
                chat = cs[0]
                for i, l in enumerate(layers):
                    own.append((((net.run(ch.decode(i, cs[i]), l) - Ae) ** 2).sum(-1).mean(-1) / V).tolist())
                    chain.append((((net.run(ch.decode(i, chat), l) - Ae) ** 2).sum(-1).mean(-1) / V).tolist())"""
new = """                own, chain, agree = [], [], []
                own_me, chain_me = [], []
                chat = cs[0]
                for i, l in enumerate(layers):
                    ro = net.run(ch.decode(i, cs[i]), l)
                    rc = net.run(ch.decode(i, chat), l)
                    own.append((((ro - Ae) ** 2).sum(-1).mean(-1) / V).tolist())
                    chain.append((((rc - Ae) ** 2).sum(-1).mean(-1) / V).tolist())
                    own_me.append((((ro - Ae).mean(1)) ** 2).sum(-1).div(V).tolist())
                    chain_me.append((((rc - Ae).mean(1)) ** 2).sum(-1).div(V).tolist())"""
assert old in s
s = s.replace(old, new)
old2 = """                ent = dict(own_nmse=[o[mi] for o in own], chain_nmse=[c[mi] for c in chain],
                           bit_agreement=[a[mi] for a in agree], transitions=[])"""
new2 = """                ent = dict(own_nmse=[o[mi] for o in own], chain_nmse=[c[mi] for c in chain],
                           own_mean_err=[o[mi] for o in own_me], chain_mean_err=[c[mi] for c in chain_me],
                           bit_agreement=[a[mi] for a in agree], transitions=[])
                ent['deductive'] = deductive(ch, net, layers, cr, Ar, mi, b, V)"""
assert old2 in s
s = s.replace(old2, new2)
old3 = """            res['seconds'] = time.time() - t1
            with open(path, 'w') as f:
                json.dump(res, f)"""
new3 = """            res['seconds'] = time.time() - t1
            with open(path, 'w') as f:
                json.dump(res, f)
            torch.save(ch.state_dict(), path.replace('.json', '.pt'))"""
assert old3 in s
s = s.replace(old3, new3)
old4 = """for cfg in args.configs.split(','):"""
new4 = '''@torch.no_grad()
def deductive(ch, net, layers, cr, Ar, mi, b, V):
    """Part C: estimate E a by propagating code laws through the learned transitions over all 2^b codes.
    exact0: the empirical law of c_0 (reach sample) pushed forward exactly (isolates the chain's own bias);
    fact0: product of c_0's bit marginals, pushed forward exactly; mf: the product law re-factorised after every
    transition (propagates b marginals only). Truth: the mean output on the reach sample (noise floor 1/P in nMSE).
    Errors |est - E a|^2 / V; MC at equal cost (2^b decoder + future evaluations) has error about 2^-b."""
    allc = torch.cat([all_codes(b), torch.zeros(2 ** b, K - b, device=DEV)], 1)
    Mx = lambda c: c.unsqueeze(0).expand(M, *c.shape)  # noqa: E731
    nxt = []
    for i in range(len(layers) - 1):
        F = torch.sign(ch.trans(i, Mx(allc))[mi][:, :b] + 1e-9)
        nxt.append(code_index(F, b))
    Ea = Ar.double().mean(0)
    out_all = net.run(ch.decode(len(layers) - 1, Mx(allc))[mi], layers[-1]).double()
    idx0 = code_index(cr[0][mi], b)
    emp = torch.bincount(idx0, minlength=2 ** b).double()
    emp = emp / emp.sum()
    bits = (all_codes(b) < 0).double()
    pm = ((cr[0][mi][:, :b] < 0).double()).mean(0)

    def prod_law(p):
        return torch.exp((bits * torch.log(p.clamp(min=1e-12)) +
                          (1 - bits) * torch.log((1 - p).clamp(min=1e-12))).sum(1))

    res = {}
    for name in ['exact0', 'fact0', 'mf']:
        mu = emp.clone() if name == 'exact0' else prod_law(pm)
        for i in range(len(layers) - 1):
            mu = torch.zeros(2 ** b, device=DEV, dtype=torch.float64).index_add_(0, nxt[i], mu)
            if name == 'mf':
                mu = prod_law((mu[:, None] * bits).sum(0))
        est = (mu[:, None] * out_all).sum(0)
        res[name] = float(((est - Ea) ** 2).sum() / V)
    res['mc_equal_cost'] = 2.0 ** (-b)
    res['truth_floor'] = 1.0 / Ar.shape[0]
    return res


for cfg in args.configs.split(','):'''
assert old4 in s
s = s.replace(old4, new4, 1)
open(p, 'w').write(s)
print('patched')
