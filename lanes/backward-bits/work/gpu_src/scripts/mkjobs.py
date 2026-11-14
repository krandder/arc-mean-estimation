import sys
# usage: mkjobs.py <phase> <out> <seeds> -> prints job lines
phase, out, seeds = sys.argv[1], sys.argv[2], [int(s) for s in sys.argv[3].split(',')]
cfgs = [(16, 16, 0.1), (8, 16, 0.0003), (16, 8, 0.2), (8, 8, 0.01)]
py = 'cd /root/soup && /root/venv/bin/python'
for seed in seeds:
    for n, L, s in cfgs:
        base = f'--n {n} --L {L} --seed {seed} --sigma {s} --KL 64 --device cuda --out {out}'
        if phase == 'outcode':
            print(f'{py} scripts/run_chain.py {base} --chain K --outcode_only 1')
        elif phase == 'chains':
            print(f'{py} scripts/run_chain.py {base} --chain K --cert 1')
            print(f'{py} scripts/run_chain.py {base} --chain PR --cert 1 --lookahead 0')
            print(f'{py} scripts/run_chain.py {base} --chain R --lookahead 0')
            print(f'{py} scripts/run_chain.py {base} --chain P --lookahead 0')
        elif phase == 'post':
            print(f'{py} scripts/run_truth.py {base} --chains K,R,P,PR')
        elif phase == 'extra':
            mid = [L - 2, (3 * (L - 1)) // 4, (L - 1) // 2, (L - 1) // 4, 0]
            print(f'{py} scripts/run_gauss.py {base} --chain K --layers ' + ','.join(str(x) for x in mid))
            print(f'{py} scripts/run_fwd.py {base} --layers ' + ','.join(str(x) for x in mid))
        elif phase == 'conv':
            print(f'{py} scripts/conv_check.py {base} --chain K --layers {L - 2},{(L - 1) // 2},0')
