#!/usr/bin/env python3
"""Analyze round_wf/pareto/frontier.json: print frontier tables, pick the
wirelength champion and the knee (max normalized distance from the
endpoints chord), and the diagnostic Dreq comparison."""
import json, math, sys

FR = "/home/hatch/workspace/mix/exploration/round_wf/pareto/frontier.json"

def main():
    fr = json.load(open(FR))
    res = fr["results"]
    print("=== Pareto frontiers (W min, S max) ===")
    picks = {}
    for D in ("4", "3", "2"):
        idx = fr["pareto_idx"][D]
        pts = [(res[i]["W"], res[i]["S"], res[i]["lam"], res[i]["seed"], i) for i in idx]
        pts.sort()
        print(f"--- Dreq={D}: {len(pts)} nondominated points ---")
        for w, s, lam, seed, i in pts:
            print(f"  W={w:5d} S={s:4d} lam={lam:3d} seed={seed} idx={i}")
        if D == "4" and pts:
            # wirelength champion = min W
            champ = min(pts)
            # knee = max perpendicular distance from endpoints chord (normalized)
            ws = [p[0] for p in pts]; ss = [p[1] for p in pts]
            w0, w1, s0, s1 = min(ws), max(ws), min(ss), max(ss)
            def norm(w, s):
                return ((w - w0) / max(1, w1 - w0), (s - s0) / max(1, s1 - s0))
            (ax, ay), (bx, by) = norm(w0, s1), norm(w1, s0)  # chord: low-W/high-S to high-W/low-S
            best, bestd = None, -1
            for w, s, lam, seed, i in pts:
                px, py = norm(w, s)
                # distance from point to line ab
                num = abs((by - ay) * px - (bx - ax) * py + bx * ay - by * ax)
                den = math.hypot(by - ay, bx - ax)
                d = num / den if den else 0
                if d > bestd:
                    bestd, best = d, (w, s, lam, seed, i)
            picks["champion"] = {"W": champ[0], "S": champ[1], "idx": champ[4]}
            picks["knee"] = {"W": best[0], "S": best[1], "idx": best[4], "dist": round(bestd, 3)}
            print(f"  >> champion: W={champ[0]} S={champ[1]} idx={champ[4]}")
            print(f"  >> knee:     W={best[0]} S={best[1]} idx={best[4]} (d={bestd:.3f})")
    print("=== Diagnostic: min W per Dreq ===")
    for D in ("4", "3", "2"):
        ws = [r["W"] for r in res if str(r["Dreq"]) == D]
        print(f"  Dreq={D}: min W = {min(ws)}")
    print("=== picks JSON ===")
    print(json.dumps(picks))

if __name__ == "__main__":
    main()
