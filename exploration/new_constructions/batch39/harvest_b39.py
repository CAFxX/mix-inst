#!/usr/bin/env python3
"""Harvest KEEP schedules from batch-39 andnM6 screen logs by RNG replay.

The screen logs record (try, z, killkey, KEEP/kill) but not schedules.
Draws are deterministic given the seed (np.random.default_rng), so replaying
the exact draw logic recovers every schedule. The replay is VERIFIED: each
replayed z must match the log's z to <0.05, else the seed is wrong and we
fail loud (no silent schedule corruption).
"""
import json
import re
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions/batch39")
from t6_b39_screen import draw_stage, eval_sched


def parse_log(path):
    rows = []
    pat = re.compile(r"try\s+(\d+)\s+maxworst\|z\|=\s*([\d.]+)\s+killkey=(0x[0-9a-f]+)\s+(KEEP|kill)")
    with open(path) as f:
        for line in f:
            m = pat.search(line)
            if m:
                rows.append((int(m.group(1)), float(m.group(2)), m.group(3),
                             m.group(4) == "KEEP"))
    return rows


def harvest(log_path, seed, nstages, out_path):
    rows = parse_log(log_path)
    rng = np.random.default_rng(seed)
    keeps = []
    for (t, z_log, key_log, is_keep) in rows:
        stages, seen = [], set()
        while len(stages) < nstages:
            s = draw_stage(rng, "andnM")
            if s in seen:
                continue
            seen.add(s)
            stages.append(s)
        assert all(s[0] != s[1] for s in stages)
        z, key = eval_sched("andnM", stages)
        if abs(z - z_log) > max(0.05, 0.001 * z_log):
            print("SEED-MISMATCH at try %d: replay z=%.1f vs log z=%.1f "
                  "(seed=%#x wrong?)" % (t, z, z_log, seed), flush=True)
            sys.exit(3)
        if is_keep:
            assert z < 10, "log says KEEP but replay z=%.1f" % z
            keeps.append((z, stages))
    keeps.sort(key=lambda k: k[0])
    with open(out_path, "w") as f:
        for z, stages in keeps:
            f.write(json.dumps({"z": z, "stages": [list(s) for s in stages],
                                "form": "andnM", "nstages": nstages,
                                "seed": seed, "src": log_path}) + "\n")
    print("harvested %d KEEPs -> %s (seed=%#x verified on %d tries)"
          % (len(keeps), out_path, seed, len(rows)), flush=True)
    if keeps:
        print("best z=%.1f stages=%s" % (keeps[0][0], keeps[0][1]), flush=True)


if __name__ == "__main__":
    # usage: harvest_b39.py <log> <seed> <nstages> <out.jsonl>
    harvest(sys.argv[1], int(sys.argv[2], 0), int(sys.argv[3]), sys.argv[4])
