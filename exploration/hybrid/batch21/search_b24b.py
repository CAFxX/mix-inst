#!/usr/bin/env python3
"""Batch-24b: guided hill-climb on heterogeneous lin/no-lin schedules.

The batch-24 random screen found a searchable near-miss cluster at k=4
(4 draws z<100, 9 <200, 27 <500 of 150; best 53.6, bar is 10). This is the
same situation the b33c frontier point came from: random draws near-miss,
guided schedule search clears. Multi-start stochastic hill climbing with
the EXACT S1 DIFF maxworst|z| (10 keys) as the objective -- the same
"triage = exact DIFF" methodology, now as an optimizer.

k=4 projects to ~18.8u (1.0u better than the 19.8u frontier); k=5 to
~19.3u (0.5u better). k=5 = one no-lin stage among five frontier stages;
the pure frontier 6-stage clears with guided search, so k=5 has headroom.

Moves (k fixed per run): resample one rotation in one stage, or swap the
typ of two stages (keeps k). Accept strictly-better. Seeds: top batch-24
draws (k=4) + fresh random k=5 draws.
"""
import sys, json, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/hybrid/batch21")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from search_b24 import eval_sched, draw_stages

def mutate(rng, stages, k):
    st = [list(s) for s in stages]
    if rng.random() < 0.7:
        j = int(rng.integers(0, 6))
        f = int(rng.integers(1, 4))  # which rotation: 1=a,2=b,3=c
        st[j][f] = int(rng.integers(1, 64))
    else:
        # swap typs of two stages with different typ (keeps k)
        fronts = [j for j in range(6) if st[j][0] == "front"]
        nolins = [j for j in range(6) if st[j][0] == "nolin"]
        if fronts and nolins:
            jf = fronts[int(rng.integers(0, len(fronts)))]
            jn = nolins[int(rng.integers(0, len(nolins)))]
            st[jf][0], st[jn][0] = st[jn][0], st[jf][0]
    return [tuple(s) for s in st]

def hill_climb(rng, seed_stages, k, budget, tag):
    cur = [tuple(s) for s in seed_stages]
    curz, _ = eval_sched(cur)
    best, bestz = cur, curz
    print("climb %s start z=%.1f" % (tag, curz), flush=True)
    for it in range(budget):
        cand = mutate(rng, cur, k)
        cz, _ = eval_sched(cand)
        if cz < curz:
            cur, curz = cand, cz
            if cz < bestz:
                best, bestz = cand, cz
                print("climb %s iter %d NEW BEST z=%.2f" % (tag, it, bestz),
                      flush=True)
                if bestz < 10:
                    print("climb %s CLEARED THE BAR at iter %d" % (tag, it),
                          flush=True)
                    break
    return best, bestz

def main():
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB24B
    rng = np.random.default_rng(seed)
    t0 = time.time()
    b24 = json.load(open("search_b24_results.json"))
    results = []
    # Phase 1: k=4 from top-8 seeds x 300 evals
    seeds4 = sorted([r for r in b24 if r["k"] == 4],
                    key=lambda r: r["z"])[:8]
    for i, s in enumerate(seeds4):
        st = [tuple(x) for x in s["stages"]]
        best, bestz = hill_climb(rng, st, 4, 300, "k4-s%d" % i)
        results.append({"phase": "k4", "seed_z": s["z"], "best_z": bestz,
                        "keep": bestz < 10,
                        "stages": [list(x) for x in best]})
        if bestz < 10:
            break
    # Phase 2: k=5 (only if k=4 did not clear)
    if not any(r["keep"] for r in results):
        print("k=4 did not clear; trying k=5", flush=True)
        seeds5 = []
        for t in range(60):
            st = draw_stages(rng, 5)
            z, _ = eval_sched(st)
            seeds5.append((z, st))
            print("k5 seed %d z=%.1f" % (t, z), flush=True)
        seeds5.sort(key=lambda x: x[0])
        for i, (z, st) in enumerate(seeds5[:4]):
            best, bestz = hill_climb(rng, st, 5, 300, "k5-s%d" % i)
            results.append({"phase": "k5", "seed_z": z, "best_z": bestz,
                            "keep": bestz < 10,
                            "stages": [list(x) for x in best]})
            if bestz < 10:
                break
    json.dump(results, open("search_b24b_results.json", "w"))
    nkeeps = sum(1 for r in results if r["keep"])
    print("B24B TOTAL: %d climbs, %d cleared (<10), %.1fs" % (
        len(results), nkeeps, time.time() - t0), flush=True)
    for r in sorted(results, key=lambda r: r["best_z"])[:5]:
        print("best %s seed_z=%.1f -> %.2f keep=%s" % (
            r["phase"], r["seed_z"], r["best_z"], r["keep"]), flush=True)

if __name__ == "__main__":
    main()
