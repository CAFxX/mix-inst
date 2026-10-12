#!/usr/bin/env python3
"""Batch-62 pre-pilot RESUME: tries 4..11 of the 12-draw pre-pilot (seed 0xB621).

The original pre-pilot (run_b62_prepilot.sh) died after try 3 with no live
processes left (2026-10-12 ~07:08Z). Re-running with the same seed reproduces
the draw sequence; the first 4 draws are consumed to advance the RNG past the
completed tries 0-3, then tries 4-11 run the identical pipeline (G1 fisher ->
G2 inner DIFF-SEQ/LIN -> G3 RD-SEQ -> G4 Low1/64 PractRand prescreen).
Keeps append to the same prepilot_keeps.jsonl (3 lines already present);
log lines match the original "try %3d" format.
"""
import sys, json
import numpy as np

import t6_b62_screen as S

SEED = 0xB621
SKIP = 4          # tries 0..3 completed (log-verified)
N_TRY = 12
KEEP_PATH = "prepilot_keeps.jsonl"

def main():
    rng = np.random.default_rng(SEED)
    for _ in range(SKIP):
        S.draw_perturbed(rng)  # advance past completed tries
    keep = []
    kills = 0
    gkills = [0, 0, 0, 0]
    minz = float("inf")
    for t in range(SKIP, N_TRY):
        stages, m = S.draw_perturbed(rng)
        tag = "t%03d" % t
        nrej, wz, key, flp = S.eval_fisher(stages)
        minz = min(minz, wz)
        if nrej > 0:
            kills += 1
            gkills[0] += 1
            print("try %3d m=%d G1-fisher KILL n_reject=%d z=%.1f" %
                  (t, m, nrej, wz), flush=True)
            continue
        v2, r2, d2, _ = S.eval_inner(stages, name="b62-%s" % tag)
        if v2 != "CAL_PASS":
            kills += 1
            gkills[1] += 1
            print("try %3d m=%d G2-inner KILL rej=%d diffworstz=%.1f" %
                  (t, m, r2, d2), flush=True)
            continue
        n3, wk3, f3, rej3 = S.eval_rdseq(stages)
        if n3 > 0:
            kills += 1
            gkills[2] += 1
            print("try %3d m=%d G3-rdseq KILL n_reject=%d rej=%s" %
                  (t, m, n3, rej3), flush=True)
            continue
        k4, d4 = S.eval_low1(stages, tag)
        if not k4:
            kills += 1
            gkills[3] += 1
            print("try %3d m=%d G4-low1 KILL %s" % (t, m, d4), flush=True)
            continue
        print("try %3d m=%d KEEP fisher z=%.1f inner diffz=%.1f %s" %
              (t, m, wz, d2, d4), flush=True)
        keep.append((wz, stages, m))
        rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
               "inner_diffz": d2,
               "stages": [list(s) for s in stages],
               "form": "muxD5f", "seed": SEED, "is_324": False,
               "base": "t6_b59_47", "n_perturb": m}
        with open(KEEP_PATH, "a") as f:
            f.write(json.dumps(rec) + "\n")
    print("=== muxD5fweakgated RESUME: tries %d-%d: %d KEEP minz=%.1f "
          "gkills=%s (seed=%#x) ===" % (SKIP, N_TRY - 1, len(keep), minz,
                                        gkills, SEED), flush=True)

if __name__ == "__main__":
    main()
