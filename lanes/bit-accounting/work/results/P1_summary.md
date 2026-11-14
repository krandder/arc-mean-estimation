# Phase 1 summary: bits needed per layer (median over seeds, [min, max]); slope = bits per halving of the output error between D = 0.1 and 0.01 (median)

| net | l | class | R*(0.1) | R*(0.01) | R*(0.001) | slope 0.1->0.01 | seeds | flagged cells |
|---|---|---|---|---|---|---|---|---|
| relu 16x4 | 0 | local | 12.5 [9.1, 20.1] | 34.6 [31.4, 46.4] | unreached | 6.70 | 3 | 3 |
| relu 16x4 | 0 | unres | 7.2 [4.9, 7.4] | 21.6 [15.3, 47.5] | unreached | 4.26 | 3 | 3 |
| relu 16x4 | 1 | local | 9.7 [6.1, 11.7] | 26.5 [22.8, 32.6] | unreached | 5.05 | 3 | 3 |
| relu 16x4 | 1 | unres | 7.0 [4.7, 7.3] | 19.7 [14.8, 21.0] | unreached | 3.73 | 3 | 3 |
| relu 16x4 | 2 | local | 8.0 [5.3, 8.1] | 22.4 [18.6, 24.5] | unreached | 4.32 | 3 | 3 |
| relu 16x4 | 2 | unres | 6.7 [4.7, 7.2] | 17.9 [14.6, 18.8] | 28.4 (2 unreached) | 3.37 | 3 | 3 |
| relu 16x4 | 3 | local | 7.3 [4.8, 7.7] | 20.7 [15.7, 21.0] | 31.8 (2 unreached) | 3.91 | 3 | 3 |
| relu 16x4 | 3 | unres | 6.5 [4.6, 7.2] | 17.0 [14.4, 18.5] | 31.8 [26.9, 33.9] | 3.16 | 3 | 1 |
| relu 16x4 | out | unres | 6.6 [4.6, 7.2] | 17.4 [14.6, 18.7] | 27.1 (2 unreached) | 3.24 | 3 | 2 |
| relu 16x16 | 0 | local | 17.2 [15.7, 29.9] | 48.8 [46.9, 60.8] | unreached | 9.30 | 3 | 3 |
| relu 16x16 | 0 | unres | 2.5 [1.8, 2.6] | 6.9 [6.7, 7.0] | unreached | 1.36 | 3 | 3 |
| relu 16x16 | 4 | local | 3.3 [3.2, 3.9] | 11.9 [11.6, 18.7] | unreached | 2.60 | 3 | 3 |
| relu 16x16 | 4 | unres | 2.4 [1.8, 2.5] | 6.5 [6.4, 6.6] | 12.6 [12.3, 12.8] (1 unreached) | 1.26 | 3 | 1 |
| relu 16x16 | 8 | local | 2.6 [1.8, 2.7] | 7.4 [7.2, 8.0] | 17.6 [16.6, 18.4] | 1.44 | 3 | 3 |
| relu 16x16 | 8 | unres | 2.4 [1.7, 2.5] | 6.2 [6.0, 6.6] | 12.0 [11.7, 12.5] | 1.25 | 3 | 1 |
| relu 16x16 | 12 | local | 2.5 [1.7, 2.6] | 6.5 [5.8, 6.8] | 12.8 [12.4, 13.3] | 1.23 | 3 | 3 |
| relu 16x16 | 12 | unres | 2.4 [1.7, 2.5] | 6.1 [5.6, 6.6] | 11.3 [11.2, 12.3] | 1.18 | 3 | 0 |
| relu 16x16 | 15 | local | 2.5 [1.7, 2.5] | 6.6 [5.7, 6.8] | 12.5 [11.7, 12.9] | 1.23 | 3 | 1 |
| relu 16x16 | 15 | unres | 2.4 [1.7, 2.5] | 6.1 [5.6, 6.6] | 11.8 [11.1, 12.4] | 1.17 | 3 | 1 |
| relu 16x16 | out | unres | 2.4 [1.7, 2.5] | 6.1 [5.6, 6.5] | 12.0 [11.2, 12.3] | 1.17 | 3 | 0 |
| relu 32x8 | 0 | local | 29.4 [22.0, 36.9] | 86.7 [78.2, 96.3] | unreached | 17.24 | 3 | 3 |
| relu 32x8 | 0 | unres | 7.1 [6.0, 7.5] | 88.7 [66.8, 100.3] | unreached | 24.91 | 3 | 3 |
| relu 32x8 | 2 | local | 10.9 [8.2, 13.3] | 45.2 [40.6, 51.8] | unreached | 10.35 | 3 | 3 |
| relu 32x8 | 2 | unres | 7.1 [5.8, 7.4] | 23.2 [21.6, 29.0] | unreached | 5.22 | 3 | 3 |
| relu 32x8 | 4 | local | 7.7 [6.3, 9.1] | 27.9 [26.1, 32.4] | unreached | 6.48 | 3 | 3 |
| relu 32x8 | 4 | unres | 7.0 [5.8, 7.2] | 21.3 [21.0, 24.2] | unreached | 4.69 | 3 | 3 |
| relu 32x8 | 6 | local | 7.2 [6.1, 7.5] | 23.7 [21.8, 26.1] | unreached | 5.31 | 3 | 3 |
| relu 32x8 | 6 | unres | 6.9 [5.7, 6.9] | 20.8 [20.3, 23.1] | unreached | 4.53 | 3 | 3 |
| relu 32x8 | 7 | local | 7.1 [5.9, 7.2] | 22.5 [21.4, 25.7] | unreached | 5.00 | 3 | 3 |
| relu 32x8 | 7 | unres | 6.9 [5.7, 6.9] | 20.7 [20.2, 22.9] | unreached | 4.52 | 3 | 3 |
| relu 32x8 | out | unres | 6.9 [5.7, 6.9] | 20.8 [20.4, 23.1] | unreached | 4.57 | 3 | 3 |
| relu 32x32 | 0 | local | 41.3 [37.4, 46.8] | 112.0 [111.1, 118.0] | unreached | 21.43 | 3 | 3 |
| relu 32x32 | 0 | unres | 1.9 [1.6, 2.4] | 5.6 [4.2, 6.2] | unreached | 1.13 | 3 | 3 |
| relu 32x32 | 8 | local | 2.0 [1.7, 2.7] | 12.6 [6.1, 16.8] | unreached | 2.98 | 3 | 3 |
| relu 32x32 | 8 | unres | 1.8 [1.6, 2.4] | 5.5 [4.2, 6.1] | 11.9 [9.2, 12.0] | 1.11 | 3 | 0 |
| relu 32x32 | 16 | local | 1.9 [1.7, 2.5] | 6.3 [4.3, 6.5] | 14.7 [11.0, 17.6] | 1.21 | 3 | 3 |
| relu 32x32 | 16 | unres | 1.9 [1.6, 2.4] | 5.5 [4.1, 6.0] | 11.5 [8.8, 11.7] | 1.10 | 3 | 0 |
| relu 32x32 | 24 | local | 1.9 [1.6, 2.4] | 5.6 [4.1, 6.2] | 11.9 [9.0, 12.2] | 1.11 | 3 | 0 |
| relu 32x32 | 24 | unres | 1.9 [1.6, 2.4] | 5.5 [4.1, 6.0] | 11.3 [8.7, 11.6] | 1.09 | 3 | 0 |
| relu 32x32 | 31 | local | 1.9 [1.6, 2.4] | 5.5 [4.1, 6.1] | 11.7 [8.8, 12.4] | 1.09 | 3 | 0 |
| relu 32x32 | 31 | unres | 1.9 [1.6, 2.4] | 5.5 [4.1, 6.0] | 11.3 [8.6, 11.8] | 1.08 | 3 | 0 |
| relu 32x32 | out | unres | 1.9 [1.6, 2.4] | 5.4 [4.1, 6.0] | 11.3 [8.7, 11.9] | 1.08 | 3 | 0 |
| feistel 16x16 | 0 | local | unreached | unreached | unreached | - | 1 | 0 |
| feistel 16x16 | 0 | unres | unreached | unreached | unreached | - | 1 | 0 |
| feistel 16x16 | 4 | local | unreached | unreached | unreached | - | 1 | 0 |
| feistel 16x16 | 4 | unres | unreached | unreached | unreached | - | 1 | 0 |
| feistel 16x16 | 8 | local | unreached | unreached | unreached | - | 1 | 0 |
| feistel 16x16 | 8 | unres | unreached | unreached | unreached | - | 1 | 0 |
| feistel 16x16 | 12 | local | 14.5 | 15.9 | 16.0 | 0.42 | 1 | 1 |
| feistel 16x16 | 12 | unres | 15.7 | 16.0 | 16.0 | 0.08 | 1 | 0 |
| feistel 16x16 | 15 | local | 16.6 | 21.0 | 22.8 | 1.31 | 1 | 1 |
| feistel 16x16 | 15 | unres | 16.5 | 18.2 | 22.4 | 0.50 | 1 | 1 |
| feistel 16x16 | out | unres | 16.6 | 22.9 | 26.8 | 1.88 | 1 | 1 |
| linear 16x16 | 0 | local | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| linear 16x16 | 0 | unres | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| linear 16x16 | 4 | local | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| linear 16x16 | 4 | unres | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| linear 16x16 | 8 | local | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| linear 16x16 | 8 | unres | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| linear 16x16 | 12 | local | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| linear 16x16 | 12 | unres | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| linear 16x16 | 15 | local | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| linear 16x16 | 15 | unres | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| linear 16x16 | out | unres | 4.2 | 11.5 | 20.3 | 2.20 | 1 | 0 |
| tanh4 16x16 | 0 | local | 65.7 | 99.2 | unreached | 10.09 | 1 | 1 |
| tanh4 16x16 | 0 | unres | 64.6 | 98.5 | unreached | 10.20 | 1 | 1 |
| tanh4 16x16 | 4 | local | 34.4 | 67.9 | unreached | 10.10 | 1 | 1 |
| tanh4 16x16 | 4 | unres | 9.0 | 67.0 | unreached | 17.45 | 1 | 1 |
| tanh4 16x16 | 8 | local | 18.2 | 47.5 | unreached | 8.81 | 1 | 1 |
| tanh4 16x16 | 8 | unres | 7.6 | 38.5 | unreached | 9.30 | 1 | 1 |
| tanh4 16x16 | 12 | local | 10.3 | 26.6 | unreached | 4.90 | 1 | 1 |
| tanh4 16x16 | 12 | unres | 7.0 | 17.0 | unreached | 3.02 | 1 | 1 |
| tanh4 16x16 | 15 | local | 7.8 | 21.5 | unreached | 4.11 | 1 | 1 |
| tanh4 16x16 | 15 | unres | 6.9 | 16.5 | unreached | 2.89 | 1 | 1 |
| tanh4 16x16 | out | unres | 6.6 | 16.8 | unreached | 3.05 | 1 | 1 |
