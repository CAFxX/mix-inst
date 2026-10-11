#!/usr/bin/env python3
"""S1: amended 4-family statistical screen (fast staged battery).
Usage: s1_screen.py <candidate> <outdir>

Runs:
  (a) marginal 468-cell screen via screen_cal.screen_calibrated (PB + RD families,
      Fisher-combine + Holm-Bonferroni, alpha=0.01 each) -- existing code;
  (b) LIN + DIFF families on SEQ outputs (10 keys, N=2^18) via lin_diff.py.

Verdict CAL_PASS iff zero Holm rejections across all four families
(PB, RD, LIN, DIFF). Prints verdict line and writes s1_result.json into outdir.
Exit 0 on CAL_PASS, 2 on FLAG (stage kill).

STATISTICAL HONESTY NOTES (2026-10-02, peer review MAJOR-4/5):
- The old docstring claimed "honest FWER <= 0.04". That is overstated: 3 of the
  4 families Fisher-combine dependent p-values, which is liberal (the code
  admits this in its own docstring). Only the LIN family has a rigorous
  familywise guarantee. Treat CAL_PASS as "no gross defect detected", not a
  proven 4% false-positive rate.
- Search multiplicity: with ~17 candidates screened at ~4% nominal each, the
  chance of >=1 false CAL_PASS in a round is ~50%. Leader selection is
  post-selection inference; survivors require independent re-verification
  (audit + peer review), which is what the battery's later stages provide.
"""
import importlib.util
import json
import os
import sys
import time

FB = "/home/hatch/workspace/mix/exploration/fast_battery"
EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP)
sys.path.insert(0, FB + "/src")

import numpy as np
from screen_lib import KEYS, N
from screen_cal import screen_calibrated
from lin_diff import screen_lin_diff

ALPHA = 0.01


def load_candidate(cand):
    spec = importlib.util.spec_from_file_location(
        "model_" + cand, f"{FB}/candidates/{cand}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    meta = json.load(open(f"{FB}/candidates/{cand}/meta.json"))
    return m.mix, m.mix_np, meta


def main():
    cand, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    mix, mix_np, meta = load_candidate(cand)
    keys = [int(k) for k in KEYS]  # all 10 calibrated keys for LIN+DIFF too

    t0 = time.time()
    # (b) LIN + DIFF on SEQ outputs FIRST (10x cheaper than marginal; caught
    # every kill so far). If either flags, skip the marginal screen.
    t1 = time.time()
    seq = {}
    for k in keys:
        V = np.arange(N, dtype=np.uint64)
        seq[k] = np.asarray(mix_np(V, np.full(N, np.uint64(k), dtype=np.uint64)),
                            dtype=np.uint64)
    res_ld = screen_lin_diff(seq, verbose=True)
    t_ld = time.time() - t1
    lin_hit = bool(res_ld["lin_rejected"])
    diff_hit = bool(res_ld["diff_rejected"])

    # (a) marginal PB + RD families (existing calibrated screen, all 10 KEYS)
    # skipped on early LIN/DIFF kill
    pb_rej, rd_rej, t_marg, res_marg = [], [], 0.0, {}
    marg_skipped = lin_hit or diff_hit
    marg_kill = False  # inner LIN/DIFF gate inside screen_calibrated (MAJOR-3,
    # 2026-10-02): screen_calibrated re-runs LIN/DIFF via screen_lindiff.py and
    # on a flag returns EMPTY pb/rd lists with s1_kill=True, cal_verdict=CAL_FLAG.
    # The verdict below must honor that kill signal, not just the empty lists.
    if not marg_skipped:
        os.chdir(FB)  # screen_calibrated writes results/<name>/screen_cal.json
        res_marg = screen_calibrated(mix_np, f"{cand}_s1", verbose=False)
        t_marg = time.time() - t1
        pb_rej = res_marg["cal_rejected_perbit"]
        rd_rej = res_marg["cal_rejected_red"]
        marg_kill = bool(res_marg.get("s1_kill")) or \
            res_marg.get("cal_verdict") == "CAL_FLAG"

    verdict = "CAL_PASS" if (not pb_rej and not rd_rej and not marg_kill
                             and not res_ld["lin_rejected"]
                             and not res_ld["diff_rejected"]) else "FLAG"
    out = {
        "candidate": cand,
        "verdict": verdict,
        "pb_rejected": [str(c) for c in pb_rej],
        "red_rejected": [str(c) for c in rd_rej],
        "lin_rejected": [str(c) for c in res_ld["lin_rejected"]],
        "diff_rejected": [str(c) for c in res_ld["diff_rejected"]],
        "lin_detail": res_ld["lin_detail"],
        "diff_detail": res_ld["diff_detail"],
        "raw_worst_perbit_z": res_marg.get("raw_worst_perbit_z"),
        "raw_worst_red_z": res_marg.get("raw_worst_red_z"),
        "marginal_skipped": marg_skipped,
        "time_marginal_s": round(t_marg, 1),
        "time_lin_diff_s": round(t_ld, 1),
        "fwer": "NOT RIGOROUS: Fisher-combines dependent p-values (liberal); "
                "only LIN family has an honest familywise guarantee. "
                "See docstring MAJOR-4/5 notes.",
    }
    with open(os.path.join(outdir, "s1_result.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    marg_txt = "SKIPPED (LIN/DIFF kill)" if marg_skipped else \
        f"marginal {t_marg:.0f}s: PB rej={len(pb_rej)} RD rej={len(rd_rej)}"
    print(f"[S1 {cand}] LIN/DIFF {t_ld:.0f}s: LIN {res_ld['lin_verdict']} DIFF {res_ld['diff_verdict']}; "
          f"{marg_txt}")
    print(f"[S1 {cand}] verdict: {verdict}")
    return 0 if verdict == "CAL_PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
