#!/usr/bin/env python3
"""Parallel RNG-replay harvest for batch-39 andnM6 p2 screen.

Phase 1 (sequential, fast): replay np RNG draws -> stage list per try.
Phase 2 (process pool): exact-DIFF eval per try, fail-loud z-verification
against the log, collect KEEP schedules -> JSONL sorted by z.
"""
import json
import multiprocessing as mp
import re
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions/batch39")
from t6_b39_screen import draw_stage, eval_sched
from harvest_b39 import parse_log


def eval_one(args):
    t, z_log, key_log, is_keep, stages = args
    z, key = eval_sched("andnM", stages)
    if abs(z - z_log) > max(0.05, 0.001 * z_log):
        return (t, None, "SEED-MISMATCH replay z=%.1f log z=%.1f" % (z, z_log))
    if is_keep and z >= 10:
        return (t, None, "KEEP-flag mismatch z=%.1f" % z)
    return (t, (z, stages) if is_keep else None, None)


def main():
    log_path, seed_s, nstages_s, out_path = sys.argv[1:5]
    seed, nstages = int(seed_s, 0), int(nstages_s)
    rows = parse_log(log_path)
    rng = np.random.default_rng(seed)
    jobs = []
    for (t, z_log, key_log, is_keep) in rows:
        stages, seen = [], set()
        while len(stages) < nstages:
            s = draw_stage(rng, "andnM")
            if s in seen:
                continue
            seen.add(s)
            stages.append(s)
        assert all(s[0] != s[1] for s in stages)
        jobs.append((t, z_log, key_log, is_keep, stages))
    print("phase 1: %d draw sequences replayed" % len(jobs), flush=True)
    with mp.Pool(4) as pool:
        results = pool.map(eval_one, jobs)
    keeps = []
    for t, keep, err in sorted(results):
        if err:
            print("FAIL-LOUD try %d: %s" % (t, err), flush=True)
            sys.exit(3)
        if keep:
            keeps.append(keep)
    keeps.sort(key=lambda k: k[0])
    with open(out_path, "w") as f:
        for z, stages in keeps:
            f.write(json.dumps({"z": z, "stages": [list(s) for s in stages],
                                "form": "andnM", "nstages": nstages,
                                "seed": seed, "src": log_path}) + "\n")
    print("harvested %d KEEPs -> %s (%d tries verified)"
          % (len(keeps), out_path, len(jobs)), flush=True)
    if keeps:
        print("best z=%.1f stages=%s" % (keeps[0][0], keeps[0][1]), flush=True)


if __name__ == "__main__":
    main()
