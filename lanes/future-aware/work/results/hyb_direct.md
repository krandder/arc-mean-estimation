# H1 hybrid estimates scored directly (POST HOC; scratch/run_hyb_direct.py, scratch/score_hyb_direct.py)

Direct error = |E_Q[c] + mean_RQMC(h_L - c) - Y|^2 / V, mean over 8 scrambles; Q = exact Gaussian recursion unless stated. Gains: plain RQMC error at C over the hybrid's direct error at N = (C - B) / a; "paired" = plain RQMC on the same scrambles in the same run (measured to 2^16, no extrapolation); "arc" = arc-update's curve (the registered comparator). Ledgers (see the script header): reg = registered (historical); exp = expanded (closure charged for the mean used, plus the uncharged linear algebra and the quadratic control's 2^16-sample cloud); sum = exp with the sum-based evaluation that run_hyb_direct.py v2 performs (an approximate cost of one selected control; see the script header for what it leaves out). Best = max over controls per net (the registered rule), median over nets; best fixed = the single control with the highest median.

## n = 64 (8 nets)
Reproduction of the registered runs (max relative difference): eta 8.9e-16, beta 3.2e-14, residual metric 1.5e-12, plain RQMC 1.1e-16.
(direct - (residual metric + beta)) / direct over all controls, scrambles sizes and nets: median -0.002, 5-95% -0.224 to 0.081.

| l = 1 control (exact mean) | eta | direct residual / plain RQMC at 2^14 | at 2^16 |
|---|---|---|---|
| jac | 0.525 | 0.93 | 0.952 |
| jacmf | 0.531 | 0.931 | 0.958 |
| reg | 0.468 | 0.939 | 0.948 |
| regq16 | 0.319 | 0.748 | 0.81 |

| budget, ledger, closure mean | best per net vs paired plain (median; range) | best fixed control | vs arc-update curve (median) |
|---|---|---|---|
| 10000, reg, eg | 0.846 (0.792-0.976) | 1/jacmf: 0.846 | 0.793 |
| 10000, exp, eg | 0.849 (0.797-0.981) | 1/jacmf: 0.849 | 0.798 |
| 10000, sum, eg | 0.95 (0.926-1.1) | 1/jacmf: 0.95 | 0.901 |
| 65000, reg, eg | 0.957 (0.868-1) | 1/jacmf: 0.957 | 0.99 |
| 65000, exp, eg | 0.958 (0.868-1) | 1/jacmf: 0.958 | 0.991 |
| 65000, sum, eg | 1.03 (0.975-1.15) | 1/jacmf: 1.03 | 1.1 |
| 65000, reg, k2 | 0.957 (0.868-1) | 1/jacmf: 0.957 | 0.99 |
| 65000, exp, k2 | 0.958 (0.868-1) | 1/jacmf: 0.958 | 0.991 |
| 65000, sum, k2 | 1.03 (0.975-1.15) | 1/jacmf: 1.03 | 1.1 |

## n = 128 (8 nets)
Reproduction of the registered runs (max relative difference): eta 3.4e-15, beta 2.5e-13, residual metric 1.9e-12, plain RQMC 0.0e+00.
(direct - (residual metric + beta)) / direct over all controls, scrambles sizes and nets: median 0.000, 5-95% -0.223 to 0.120.

| l = 1 control (exact mean) | eta | direct residual / plain RQMC at 2^14 | at 2^16 |
|---|---|---|---|
| jac | 0.62 | 0.936 | 0.983 |
| jacmf | 0.607 | 0.936 | 0.976 |
| reg | 0.546 | 0.908 | 0.979 |
| regq16 | 0.447 | 0.914 | 0.882 |

| budget, ledger, closure mean | best per net vs paired plain (median; range) | best fixed control | vs arc-update curve (median) |
|---|---|---|---|
| 10000, reg, eg | 0.866 (0.841-0.906) | 1/jacmf: 0.866 | 0.932 |
| 10000, exp, eg | 0.859 (0.834-0.898) | 1/jacmf: 0.859 | 0.925 |
| 10000, sum, eg | 0.914 (0.897-0.966) | 1/jacmf: 0.914 | 0.983 |
| 65000, reg, eg | 0.98 (0.874-1.03) | 1/jacmf: 0.98 | 0.729 |
| 65000, exp, eg | 0.979 (0.873-1.03) | 1/jacmf: 0.979 | 0.729 |
| 65000, sum, eg | 1.02 (0.949-1.07) | 1/jacmf: 1.02 | 0.745 |
| 65000, reg, k2 | 0.98 (0.874-1.03) | 1/jacmf: 0.98 | 0.729 |
| 65000, exp, k2 | 0.979 (0.872-1.03) | 1/jacmf: 0.979 | 0.729 |
| 65000, sum, k2 | 1.02 (0.949-1.07) | 1/jacmf: 1.02 | 0.745 |

## n = 256 (5 nets)
Reproduction of the registered runs (max relative difference): eta 1.0e-08, beta 2.8e-09, residual metric 2.7e-08, plain RQMC 0.0e+00.
(direct - (residual metric + beta)) / direct over all controls, scrambles sizes and nets: median 0.000, 5-95% -0.203 to 0.128.

| l = 1 control (exact mean) | eta | direct residual / plain RQMC at 2^14 | at 2^16 |
|---|---|---|---|
| jac | 0.757 | 0.99 | 0.988 |
| jacmf | 0.699 | 0.991 | 0.981 |
| reg | 0.614 | 0.963 | 0.975 |
| regq16 | 0.546 | 0.968 | 0.966 |

| budget, ledger, closure mean | best per net vs paired plain (median; range) | best fixed control | vs arc-update curve (median) |
|---|---|---|---|
| 10000, reg, eg | 0.85 (0.827-1) | 1/jacmf: 0.84 | 0.911 |
| 10000, exp, eg | 0.826 (0.806-0.985) | 1/jacmf: 0.818 | 0.888 |
| 10000, sum, eg | 0.855 (0.832-1.01) | 1/jacmf: 0.845 | 0.917 |
| 65000, reg, eg | 0.977 (0.949-1.02) | 1/jacmf: 0.977 | 1 |
| 65000, exp, eg | 0.974 (0.946-1.02) | 1/jacmf: 0.974 | 0.997 |
| 65000, sum, eg | 0.998 (0.981-1.04) | 1/jacmf: 0.998 | 1.02 |
| 65000, reg, k2 | 0.977 (0.949-1.02) | 1/jacmf: 0.977 | 1 |
| 65000, exp, k2 | 0.974 (0.946-1.02) | 1/jacmf: 0.974 | 0.997 |
| 65000, sum, k2 | 0.997 (0.981-1.04) | 1/jacmf: 0.997 | 1.02 |

