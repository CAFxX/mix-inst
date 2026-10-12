"""Affine search minimizing MAX BIAS (SAC and BIC), not violation count.
Target: beat-or-match AES level (16/16)."""
import numpy as np, pickle
from sbox_math import INV, apply_affine, rand_invertible, sac_report, bic_report
from sbox_math import comp_nonlinearity, comp_degree, diff_uniformity, influence

def main():
    rng = np.random.default_rng(999)
    best = None  # (sac_bias, bic_bias, S, params)
    N = 20000
    for t in range(N):
        A = rand_invertible(rng); b = int(rng.integers(0, 256))
        C = rand_invertible(rng); d = int(rng.integers(0, 256))
        S = apply_affine(INV, A, b, C, d)
        sv, sb = sac_report(S)
        bb = bic_report(S)
        key = (max(sb, bb), sb, bb)
        if best is None or key < best[0]:
            best = (key, S, (A, b, C, d))
            print(f"trial {t}: maxbias={key[0]} (sac {sb}, bic {bb})", flush=True)
            if key[0] == 0:
                break
    key, S, params = best
    A, b, C, d = params
    print("BEST maxbias:", key[0])
    nl, _ = comp_nonlinearity(S)
    print("NL =", nl, "degree =", comp_degree(S), "DU =", diff_uniformity(S))
    print("bijective:", sorted(S.tolist()) == list(range(256)))
    print("influence full:", all(len(s) == 8 for s in influence(S)))
    with open('best_bias.pkl', 'wb') as f:
        pickle.dump({'A': A, 'b': b, 'C': C, 'd': d, 'S': S,
                     'sac_maxbias': key[1], 'bic_maxbias': key[2]}, f)
    np.save('S_best.npy', S)
    print("saved best_bias.pkl, S_best.npy")

if __name__ == '__main__':
    main()
