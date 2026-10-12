#!/usr/bin/env python3
"""Re-run batch-62 pilot try 35 (seed 0xB622), killed on INFRA at G4
(RNG_test did not reach 256MB). Draws 0..34 are advanced past so the
draw is byte-identical to the pilot's. Writes any KEEP to
try35_rerun_keeps.jsonl (separate from the live pilot's
pilot_keeps.jsonl to avoid a concurrent-append race).
"""
import sys, json
import numpy as np
sys.path.insert(0, ".")
from t6_b62_screen import draw_perturbed, eval_fisher, eval_inner, eval_rdseq, eval_low1

SEED = 0xB622
TRY = 35
KEEP_PATH = "try35_rerun_keeps.jsonl"

rng = np.random.default_rng(SEED)
for _ in range(TRY):
    draw_perturbed(rng)
stages, m = draw_perturbed(rng)
tag = "t%03d" % TRY
print("try %3d m=%d draw-reproduced stages=%s" % (TRY, m, [list(s) for s in stages]), flush=True)

nrej, wz, key, flp = eval_fisher(stages)
if nrej > 0:
    print("try %3d m=%d G1-fisher KILL n_reject=%d z=%.1f" % (TRY, m, nrej, wz), flush=True)
    sys.exit(0)
v2, r2, d2, _ = eval_inner(stages, name="b62-rerun-%s" % tag)
if v2 != "CAL_PASS":
    print("try %3d m=%d G2-inner KILL rej=%d diffworstz=%.1f" % (TRY, m, r2, d2), flush=True)
    sys.exit(0)
n3, wk3, f3, rej3 = eval_rdseq(stages)
if n3 > 0:
    print("try %3d m=%d G3-rdseq KILL n_reject=%d rej=%s" % (TRY, m, n3, rej3), flush=True)
    sys.exit(0)
k4, d4 = eval_low1(stages, "b62-rerun-%s" % tag)
if not k4:
    print("try %3d m=%d G4-low1 KILL %s" % (TRY, m, d4), flush=True)
    sys.exit(0)
print("try %3d m=%d KEEP fisher z=%.1f inner diffz=%.1f %s" % (TRY, m, wz, d2, d4), flush=True)
rec = {"z": wz, "n_reject": nrej, "min_fisher": flp, "inner_diffz": d2,
       "stages": [list(s) for s in stages], "form": "muxD5f", "seed": SEED,
       "is_324": False, "base": "t6_b59_47", "n_perturb": m, "try": TRY}
with open(KEEP_PATH, "a") as f:
    f.write(json.dumps(rec) + "\n")
print("KEEP appended -> %s" % KEEP_PATH, flush=True)
