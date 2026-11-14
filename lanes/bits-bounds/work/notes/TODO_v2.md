# Items for theory v2 and the report

1. Hash proposition (main's request, 21:40Z): name the model exactly. Prop 9.1's gain comes from the ENSEMBLE prior
   (iid values with a known ensemble mean m; ARC's criterion is averaged over instances), not from structure inside
   the function. State both settings:
   - average case (random hash, known m): the Bayes estimator is partial enumeration (observed values + m for the
     rest), MSE s^2 2^{-N} (1 - x), x = T/2^N; against MC with replacement (s^2/T) the gain is 1/(x(1 - x)) >= 4 at
     every T <= 2^N; against sampling without replacement with the plain average (s^2 (1 - x)/T) the gain is 1/x.
   - worst case over a fixed function, black box: sampling without replacement is minimax, gain only 1/(1 - x) over
     sampling with replacement (main's point; the hardness lane's black-box theorems are of this kind).
   So "hash" in Kelvin's argument must say which: a random hash self-averages (easy under ARC's averaged criterion);
   a worst-case hash is black-box hard but is not what random weights produce. For the nets, the self-averaging part
   can only be exploited by methods that predict cloud averages directly (closures), not by anchoring at reference
   points (each reference is one sample of the rough field).
2. Use the relevance lane's N (DEFINITIONS v1) as THE N; cell bits N_cell ~ N x bits per direction; mean-specific
   N_>=2.
3. Forward-only vs two-sided for linear features: the relevance lane's Theorem 1 / Cor 1b (cite), with their dev
   numbers; my contribution is the cell-class separation (Thm 6.3) and the sweep model.
