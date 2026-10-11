#!/usr/bin/env python3
"""Batch-34 hill-climb: mutate top exact-DIFF schedules (track 6).

Starts from a random population, keeps the best, mutates rotations.
Used when random draws get CLOSE (min z within ~2x of the KEEP bar <10)
but don't clear it -- hill-climbing exploits the promising basin instead
of blind more-draws.

Usage: t6_b34_hillclimb.py <form> <nstages> <generations> <seed>
Forms: see t6_b34_screen.py (and1/a3/aoi/d2a3).
"""
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions/batch34")
from t6_b34_screen import eval_sched, draw_stage


def mutate(rng, form, stages):
    stages = [tuple(s) for s in stages]
    i = int(rng.integers(0, len(stages)))
    s = list(stages[i])
    j = int(rng.integers(0, len(s)))
    # rotation j of stage i: perturb or resample (keep AND-operand rule:
    # positions 0,1,2 distinct and nonzero)
    if rng.random() < 0.7:
        s[j] = (s[j] + int(rng.integers(-8, 9))) % 64
    else:
        s[j] = int(rng.integers(0, 64))
    if j < 3 and (s[j] == 0 or s[j] in (s[k] for k in range(3) if k != j)):
        return mutate(rng, form, stages)  # retry (bounded in practice)
    stages[i] = tuple(s)
    return stages


def main():
    form = sys.argv[1]
    nstages = int(sys.argv[2])
    gens = int(sys.argv[3]) if len(sys.argv) > 4 else 10
    seed = int(sys.argv[4], 0) if len(sys.argv) > 5 else 0xB34 + 0x100
    rng = np.random.default_rng(seed)
    pop = []
    while len(pop) < 24:
        st = []
        seen = set()
        while len(st) < nstages:
            s = draw_stage(rng, form)
            if s in seen:
                continue
            seen.add(s)
            st.append(s)
        pop.append(st)
    best = (1e18, None)
    for g in range(gens):
        scored = []
        for st in pop:
            wz, _ = eval_sched(form, st)
            scored.append((wz, st))
            if wz < best[0]:
                best = (wz, st)
                print("gen %d NEW BEST z=%.2f %s" % (g, wz, st), flush=True)
                if wz < 10:
                    print("=== KEEP FOUND z=%.2f ===" % wz, flush=True)
        scored.sort(key=lambda t: t[0])
        print("gen %d done: best=%.1f med=%.1f" %
              (g, scored[0][0], scored[len(scored)//2][0]), flush=True)
        if best[0] < 10:
            break
        elites = [st for _, st in scored[:8]]
        nxt = list(elites)
        while len(nxt) < 20:
            parent = elites[int(rng.integers(0, len(elites)))]
            nxt.append(mutate(rng, form, parent))
        while len(nxt) < 24:  # fresh blood
            st, seen = [], set()
            while len(st) < nstages:
                s = draw_stage(rng, form)
                if s in seen:
                    continue
                seen.add(s)
                st.append(s)
            nxt.append(st)
        pop = nxt
    print("=== HILLCLIMB %s-%d gens=%d: best z=%.2f ===" %
          (form, nstages, gens, best[0]), flush=True)
    if best[1]:
        print("BEST_SCHED", best[1], flush=True)


if __name__ == "__main__":
    main()
