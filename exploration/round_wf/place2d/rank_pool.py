#!/usr/bin/env python3
"""Rank the diffusion-first P-box pool by 2D placeability (round_wf, 2026-10-04).

Pool: O37-style affine validated P-boxes + high-S SA tours (Dreq=4).
Metric: min 2D Manhattan wirelength over 4x4 lane-grid SA placements.
Output: place2d/ranked.json (checkpoint).
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from place2d import (baseline_P, affine_pool, sa_highS_pool, placeability,
                     index_metrics, NLANE)

FRONTIER = os.path.join(HERE, "..", "pareto", "frontier.json")
OUT = os.path.join(HERE, "ranked.json")

def main():
    t0 = time.time()
    cands = []
    bP = baseline_P()
    cands.append({"name": "baseline_(5i+27)%64", "P": bP, "src": "baseline"})
    aff = affine_pool()
    print(f"affine validated pool: {len(aff)}", flush=True)
    cands.extend(aff)
    sa = sa_highS_pool(FRONTIER, s_min=320)
    print(f"SA high-S pool: {len(sa)}", flush=True)
    cands.extend(sa)
    # dedupe vs baseline
    btp = tuple(bP)
    cands = [c for c in cands if tuple(c["P"]) != btp or c["src"] == "baseline"]
    print(f"total candidates: {len(cands)}", flush=True)

    ranked = []
    for i, c in enumerate(cands):
        m = index_metrics(c["P"])
        w2d = placeability(c["P"], seeds=(1, 2), iters=8000)
        ranked.append({"name": c["name"], "src": c["src"], "S": m["S"],
                       "W1d": m["W1d"], "W2d": w2d})
        if i % 20 == 0:
            print(f"  [{i}/{len(cands)}] {c['name']}: W2d={w2d} "
                  f"({time.time()-t0:.0f}s)", flush=True)
    ranked.sort(key=lambda r: r["W2d"])
    json.dump({"v_pitch": 4, "grid": "4x4", "ranked": ranked,
               "elapsed_s": round(time.time() - t0, 1)},
              open(OUT, "w"), indent=1)
    print(f"done in {time.time()-t0:.0f}s -> {OUT}", flush=True)
    print("top 8 by W2d:")
    for r in ranked[:8]:
        print(f"  {r['name']}: W2d={r['W2d']} S={r['S']} W1d={r['W1d']}")
    b = [r for r in ranked if r["src"] == "baseline"][0]
    print(f"baseline: W2d={b['W2d']} (W1d=1450)")

if __name__ == "__main__":
    main()
