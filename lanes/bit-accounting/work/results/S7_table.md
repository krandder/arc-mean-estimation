# S7: bits the encoder chooses to use (lambda sweep), median [range] over seeds

gfix (primary) = fixed unit Gaussian noise, encoder-chosen scale, rate = information estimate with a learned prior; bern = Bernoulli bits, rate = sum_j I(h; b_j); ent = uniform noise, rounding, entropy-coded rate; vib = encoder-chosen variance, N(0, I) prior KL. R(eps) = bits per sample at which the sweep reaches nMSE eps.

## 16 x 16
| layer | class | gfix R(0.1) | bern R(0.1) | ent R(0.1) | vib R(0.1) | gfix R(0.01) | gfix refit/trained | bern bits at p~0.5 (largest lambda) |
|---|---|---|---|---|---|---|---|---|
| 0 | local | unreached | unreached | unreached | unreached | unreached | 0.984 | 0.19 |
| 0 | unres | 2.6 | unreached | 13.9 | 2.5 | unreached | 0.955 | 1.00 |
| 4 | local | 3.4 | unreached | 9.6 | 3.2 | unreached | 0.986 | 0.25 |

## 32 x 32
| layer | class | gfix R(0.1) | bern R(0.1) | ent R(0.1) | vib R(0.1) | gfix R(0.01) | gfix refit/trained | bern bits at p~0.5 (largest lambda) |
|---|---|---|---|---|---|---|---|---|
| 0 | local | unreached | unreached | unreached | unreached | unreached | 0.974 | 0.44 |
| 0 | unres | 2.0 | unreached | 13.6 | 1.9 | 8.4 | 0.928 | 1.00 |
| 8 | local | 2.3 | unreached | 11.1 | 2.7 | unreached | 0.992 | 0.31 |

