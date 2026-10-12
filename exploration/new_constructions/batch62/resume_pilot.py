#!/usr/bin/env python3
"""Batch-62 pilot RESUME after VM reboot.

The pilot (80 draws, seed 0xB622) was killed by the reboot after try 20
(pilot.log tail; 8 keeps recorded). This wrapper resumes tries 21..79.

Determinism argument: main() created rng = np.random.default_rng(0xB622)
and the ONLY consumer of that rng is draw_perturbed(rng) (evals use no
shared rng; verified by grep). So calling draw_perturbed(rng) 21 times
reproduces exactly the RNG state at the start of try 21, and the
remaining draws are byte-identical to an uninterrupted run. Keeps append
to pilot_keeps.jsonl (existing 8 lines preserved); binary/log tags
t021..t079 never collide with the completed tries' tags.
"""
import sys
import os
import json
import datetime
import subprocess

START, N_TRY, SEED = 21, 80, 0xB622
WORKREG = os.path.expanduser("~/workspace/system/bin/workreg.py")
WR_ID = "track6-batch62"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_b62_screen as S  # noqa: E402

B62 = S.B62
keep_path = os.path.join(B62, "pilot_keeps.jsonl")


def utc():
    return datetime.datetime.now(datetime.timezone.utc)


def heartbeat(try_no):
    open(os.path.join(B62, "heartbeat.txt"), "w").write(
        utc().strftime("%Y-%m-%d %H:%M:%S") + " b62-pilot-resume alive try %d\n" % try_no)
    try:
        subprocess.run([sys.executable, WORKREG, "heartbeat", "--id", WR_ID],
                       capture_output=True, timeout=60)
    except Exception:
        pass


rng = __import__("numpy").random.default_rng(SEED)
for _ in range(START):
    S.draw_perturbed(rng)  # advance past completed tries 0..START-1

kills = 0
gkills = [0, 0, 0, 0]
minz = float("inf")
nkeep = 0
print("[%s] b62-pilot RESUME: tries %d-%d (seed=%#x)" % (
    utc().strftime("%Y-%m-%dT%H:%M:%SZ"), START, N_TRY - 1, SEED), flush=True)
heartbeat(START)

for t in range(START, N_TRY):
    stages, m = S.draw_perturbed(rng)
    tag = "t%03d" % t
    # G1: fisher
    nrej, wz, key, flp = S.eval_fisher(stages)
    minz = min(minz, wz)
    if nrej > 0:
        kills += 1
        gkills[0] += 1
        print("try %3d m=%d G1-fisher KILL n_reject=%d z=%.1f" %
              (t, m, nrej, wz), flush=True)
        continue
    # G2: inner DIFF-SEQ/LIN
    v2, r2, d2, _ = S.eval_inner(stages, name="b62-%s" % tag)
    if v2 != "CAL_PASS":
        kills += 1
        gkills[1] += 1
        print("try %3d m=%d G2-inner KILL rej=%d diffworstz=%.1f" %
              (t, m, r2, d2), flush=True)
        continue
    # G3: RD-SEQ
    n3, wk3, f3, rej3 = S.eval_rdseq(stages)
    if n3 > 0:
        kills += 1
        gkills[2] += 1
        print("try %3d m=%d G3-rdseq KILL n_reject=%d rej=%s" %
              (t, m, n3, rej3), flush=True)
        continue
    # G4: Low1/64 PractRand prescreen
    k4, d4 = S.eval_low1(stages, tag)
    if not k4:
        kills += 1
        gkills[3] += 1
        print("try %3d m=%d G4-low1 KILL %s" % (t, m, d4), flush=True)
        continue
    print("try %3d m=%d KEEP fisher z=%.1f inner diffz=%.1f %s" %
          (t, m, wz, d2, d4), flush=True)
    nkeep += 1
    rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
           "inner_diffz": d2,
           "stages": [list(s) for s in stages],
           "form": "muxD5f", "seed": SEED, "is_324": False,
           "base": "t6_b59_47", "n_perturb": m}
    with open(keep_path, "a") as f:
        f.write(json.dumps(rec) + "\n")
    if (t - START + 1) % 10 == 0:
        heartbeat(t)

print("=== b62-pilot RESUME: tries %d-%d: %d KEEP minz=%.1f gkills=%s "
      "(seed=%#x) ===" % (START, N_TRY - 1, nkeep, minz, gkills, SEED), flush=True)
heartbeat(N_TRY - 1)
