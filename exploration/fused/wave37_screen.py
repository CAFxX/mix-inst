#!/usr/bin/env python3
"""Wave-37 screen: two-lane repair (intra-linear + AND-cross).

Pipeline per candidate (wave35_lib, recalibrated):
  marg proxy (PB single-bit + RD SEQ/PTR-j8/RND64; bars anchored to S1-clean
      frontiers) -> SEQ exact-DIFF (lin_diff, all 10 keys, KEEP bar max|z|<10)
      -> RND64 exact-DIFF confirmation on SEQ-KEEPs.
Controls: wave-35 committed pair (b33c KEEP z~3.3 / V0 try-1 KILL z=739994)
  -- run fused/wave35_controls.py before trusting results.

Logs per-try JSONL (wave-35 lesson: aggregates+HITs alone leave no evidence).
Fail-loud: asserts on shapes, try counts, non-vacuous gates (screen must be
  capable of killing: controls prove it).

Usage: wave37_screen.py <NSTAGES> <NLIN_X> <N_TRY> [NLIN_Y] [SEED] [OUTPREFIX]
  NLIN_Y defaults to NLIN_X (symmetric). 37d: 3 3 40 1 (x:L=3, y:L=1).
"""
import json
import random
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from wave37_lib import sample_candidate, make_mix37
from wave35_lib import _marg_proxy, seq_exact_diff, rnd64_exact_diff

NSTAGES = int(sys.argv[1])
NLIN_X = int(sys.argv[2])
N_TRY = int(sys.argv[3])
assert N_TRY >= 1, "fail-loud: vacuous screen"
assert NLIN_X >= 1, "fail-loud: need >=1 linear term"
INIT_AND = "--no-init-and" not in sys.argv
# positional args, excluding flags
_pos = [a for a in sys.argv[1:] if not a.startswith("--")]
NLIN_Y = int(_pos[3]) if len(_pos) > 3 else NLIN_X
assert NLIN_Y >= 0, "fail-loud: y-lane L must be >=0"
DEFSEED = {(3, 3, 3): 0x3731, (3, 3, 1): 0x37D1, (3, 1, 1): 0x3711}
SEED = int(_pos[4], 0) if len(_pos) > 4 else DEFSEED[(NSTAGES, NLIN_X, NLIN_Y)]
OUTP = _pos[5] if len(_pos) > 5 else f"wave37_{NSTAGES}st_L{NLIN_X}x{NLIN_Y}y_diag"
if not INIT_AND:
    OUTP += "_noinitand"


def main():
    rng = random.Random(SEED)
    t0 = time.time()
    seq_zs, marg_pass, n_keep = [], 0, 0
    with open(f"{OUTP}.jsonl", "w") as jf:
        for tried in range(1, N_TRY + 1):
            cand = sample_candidate(rng, NSTAGES, NLIN_X, NLIN_Y, INIT_AND)
            assert cand["n_lin"] == NLIN_X and cand["n_lin_y"] == NLIN_Y, \
                "fail-loud: screen sampled wrong L"
            assert cand["init_and"] == INIT_AND, "fail-loud: wrong init_and"
            mix_fn = make_mix37(cand)
            rec = {"try": tried, "cand": cand}
            ok_m, worst = _marg_proxy(mix_fn)
            rec["marg_ok"] = bool(ok_m)
            rec["marg_margin"] = worst[0]
            rec["marg_desc"] = worst[1]
            z = zr = None
            keep = False
            if ok_m:
                marg_pass += 1
                z, _ = seq_exact_diff(mix_fn)
                rec["z"] = z
                seq_zs.append(z)
                if z < 10.0:
                    zr, _ = rnd64_exact_diff(mix_fn)
                    rec["zr"] = zr
                    keep = zr < 10.0
                    if keep:
                        n_keep += 1
            status = ("KEEP" if keep else
                      ("SEQ-KILL" if (z is not None and z >= 10.0) else
                       ("RND64-KILL" if (zr is not None and zr >= 10.0) else "MARG-KILL")))
            rec["status"] = status
            jf.write(json.dumps(rec) + "\n")
            jf.flush()
            zs = f" z={z:.1f}" if z is not None else ""
            zrs = f" zr={zr:.1f}" if zr is not None else ""
            print(f"[w37-{NSTAGES}st-L{NLIN_X}x{NLIN_Y}y] TRY {tried}: marg={worst[0]:+.1f}{zs}{zrs} "
                  f"{status} ({time.time()-t0:.0f}s)", flush=True)
    seq_zs.sort()
    n = len(seq_zs)
    print(f"DONE [w37-{NSTAGES}st-L{NLIN_X}x{NLIN_Y}y]: {N_TRY} tries, marg-pass {marg_pass}/{N_TRY}, "
          f"KEEP {n_keep}", flush=True)
    if seq_zs:
        print(f"  seq-z dist: min={seq_zs[0]:.1f} med={seq_zs[n//2]:.1f} "
              f"max={seq_zs[-1]:.1f}", flush=True)
    print(f"  raw: {OUTP}.jsonl", flush=True)


if __name__ == "__main__":
    main()
