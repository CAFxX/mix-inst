"""Affine search over inversion class for SAC/BIC-optimal 8x8 S-box.
S'(x) = C.inv(A.x+b)+d.  NL/deg/DU are affine-invariant (112/7/4); search on SAC/BIC."""
import numpy as np, sys, pickle
from sbox_math import INV, apply_affine, rand_invertible, sac_report, bic_report
from sbox_math import comp_nonlinearity, comp_degree, diff_uniformity, influence

def main():
    rng = np.random.default_rng(12345)
    best = None  # (sac_viol, bic_bias, sac_maxbias, params, S)
    N = 3000
    for t in range(N):
        A = rand_invertible(rng)
        b = int(rng.integers(0, 256))
        C = rand_invertible(rng)
        d = int(rng.integers(0, 256))
        S = apply_affine(INV, A, b, C, d)
        sv, sb = sac_report(S)
        bb = bic_report(S)
        key = (sv, bb, sb)
        if best is None or key < best[0]:
            best = (key, (A, b, C, d), S)
            print(f"trial {t}: NEW BEST sac_viol={sv} bic_maxbias={bb} sac_maxbias={sb}", flush=True)
            if sv == 0 and bb == 0:
                print("PERFECT found, stopping early", flush=True)
                break
    key, params, S = best
    A, b, C, d = params
    print("BEST:", key)
    # verify invariants on winner
    nl, _ = comp_nonlinearity(S)
    print("NL =", nl, " degree =", comp_degree(S), " DU =", diff_uniformity(S))
    print("influence:", influence(S))
    print("bijective:", sorted(S.tolist()) == list(range(256)))
    with open('best_affine.pkl', 'wb') as f:
        pickle.dump({'A': A, 'b': b, 'C': C, 'd': d, 'S': S,
                     'sac_viol': key[0], 'bic_maxbias': key[1]}, f)
    np.save('S_table.npy', S)
    print("saved best_affine.pkl, S_table.npy")

if __name__ == '__main__':
    main()
