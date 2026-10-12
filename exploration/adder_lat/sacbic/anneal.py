"""
Simulated annealing for SAC/BIC with incremental scoring.
"""

import random
import time
import math
import pickle
import sys
from sacbic import structured_init
from climb import SACBICState


def anneal(t=40, max_iter=2000000, seed=123, t0_temp=2.0, t1_temp=0.01):
    rng = random.Random(seed)
    funcs = structured_init(t, rng)
    st = SACBICState(funcs)
    print(f"Init: sac={st.sac}, bic={st.bic}", flush=True)

    best_sac, best_bic = st.sac, st.bic
    best_funcs = None

    it = 0
    t_start = time.time()
    # Cost function: prioritize SAC, then BIC
    # Use weighted sum: cost = sac * 10000 + bic
    def cost(s, b):
        return s * 10000 + b

    cur_cost = cost(st.sac, st.bic)
    best_cost = cur_cost

    while it < max_iter and (st.sac > 0 or st.bic > 0):
        it += 1
        # Temperature schedule: geometric
        frac = it / max_iter
        temp = t0_temp * ((t1_temp / t0_temp) ** frac)

        j = rng.randrange(64)
        p = rng.randrange(len(st.funcs[j]))
        a2 = rng.randrange(64)
        b2 = rng.randrange(64)
        if a2 == b2:
            continue
        if a2 > b2:
            a2, b2 = b2, a2
        new_pair = (a2, b2)

        (dsac, dbic), move_info = st.try_move(j, p, new_pair)
        if not move_info:
            continue
        new_sac = st.sac + dsac
        new_bic = st.bic + dbic
        new_cost = cost(new_sac, new_bic)

        delta = new_cost - cur_cost
        accept = False
        if delta <= 0:
            accept = True
        else:
            if temp > 1e-9 and rng.random() < math.exp(-delta / temp):
                accept = True

        if accept:
            changes, jj, pp, old_pair, np2 = move_info
            st.funcs[jj][pp] = np2
            for (x, old_m, new_m) in changes:
                st.M[x][jj] = new_m
                d = st.counts[x]
                d[old_m] -= 1
                if d[old_m] == 0:
                    del d[old_m]
                d[new_m] = d.get(new_m, 0) + 1
            st.sac = new_sac
            st.bic = new_bic
            cur_cost = new_cost
            if new_cost < best_cost:
                best_cost = new_cost
                best_sac, best_bic = new_sac, new_bic
                best_funcs = [list(f) for f in st.funcs]
                print(f"it={it}: sac={new_sac}, bic={new_bic} * temp={temp:.4f}", flush=True)

        if it % 100000 == 0:
            st.recompute_scores()
            # Verify consistency
            vc = cost(st.sac, st.bic)
            print(f"it={it}: sac={st.sac}, bic={st.bic}, cur_cost={cur_cost}, verified={vc}, time={time.time()-t_start:.1f}s", flush=True)

    st.recompute_scores()
    print(f"Done: it={it}, sac={st.sac}, bic={st.bic}, best=({best_sac},{best_bic}), time={time.time()-t_start:.1f}s", flush=True)
    return st, best_funcs, (best_sac, best_bic)


if __name__ == "__main__":
    t = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    max_iter = int(sys.argv[2]) if len(sys.argv) > 2 else 2000000
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 123
    st, best_funcs, best = anneal(t=t, max_iter=max_iter, seed=seed)
    if best_funcs:
        with open(f"anneal_best_t{t}_s{seed}.pkl", "wb") as f:
            pickle.dump(best_funcs, f)
        print(f"Saved best to anneal_best_t{t}_s{seed}.pkl")
