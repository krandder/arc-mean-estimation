"""Patch vrlib.py (amendment A3): local init 'h1' = the hidden ReLU layer computes h_{l+1} = relu(W_{l+1} h_l) exactly
(a genuinely nonlinear one-ReLU-layer encoder: one layer of look-ahead, BA-FORMAL 3.1) and the code is the reference
code of h_{l+1} (eigen-directions of G_{l+1} = E[J^T J] of the future from l+1, whitened h_{l+1}); the decoder's
linear path is the MMSE inverse of that code pulled back through W_{l+1}^{-1}; analytic gains over G_{l+1}.
Needs stats['h1'] (frames of h_{l+1}) and stats['G1'] (G at l+1) from run_vr.py."""
P = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/lib/vrlib.py'
src = open(P).read()
a = """        elif mode == 'random':
            A1 = rng.standard_normal((n, n)) * math.sqrt(2.0 / n)"""
b = """        elif mode == 'h1':
            f1 = stt['h1']
            g1, U1 = eig_desc(stt['G1'])                     # whitened h_{l+1} coordinates
            ev[:kk] = g1[:kk]
            U = U1[:, :kk]
            Wn = Ws[l]                                       # W_{l+1}
            A1 = fh['S12'] @ Wn.T                            # y -> W_{l+1} h_l (pre-activation of layer l+1)
            b1 = fh['m'] @ Wn.T
            A2 = np.zeros((n, K))
            A2[:, :kk] = f1['Sm12'] @ U                      # u = h_{l+1} -> nu = (u - m_{l+1}) Sm12 U
            b2 = -f1['m'] @ A2
            d.update(A1=A1, b1=b1, A2=A2, b2=b2)
            Winv = np.linalg.inv(Wn)                         # h_l = W^{-1} h_{l+1}
            B[:kk] = U.T @ f1['T'] @ Winv.T @ fh['Tinv']     # z~ -> y_{l+1} -> h_{l+1} - m_{l+1} -> y_l
            bias = (f1['m'] @ Winv.T - fh['m']) @ fh['Tinv']
        elif mode == 'random':
            A1 = rng.standard_normal((n, n)) * math.sqrt(2.0 / n)"""
assert src.count(a) == 1
src = src.replace(a, b)
a = """        ys = (stt['h_star'] - fh['m']) @ fh['Tinv'] if (mode in ('ref', 'refu') and l < L) else np.zeros(n)"""
b = """        ys = (stt['h_star'] - fh['m']) @ fh['Tinv'] if (mode in ('ref', 'refu') and l < L) else np.zeros(n)
        if mode == 'h1':                                     # zero-rate offset relative to the linear decoder's bias
            ys = (stt['h_star'] - fh['m']) @ fh['Tinv'] - bias"""
assert src.count(a) == 1
src = src.replace(a, b)
open(P, 'w').write(src)
print('ok')
