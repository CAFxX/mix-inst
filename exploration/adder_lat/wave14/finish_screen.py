#!/usr/bin/env python3
"""Dedup-safe completion of the wave-14 screen (post-reboot).

The original screen died at 557/602 (VM reboot 2026-10-11 05:24 UTC).
wave14_screen.py appends blindly with no dedup, so it must NOT be relaunched.
This script regenerates the deterministic task list, subtracts the tags
already present in work/screen_wave14.jsonl, and runs ONLY the missing
tasks, writing to a SEPARATE file work/screen_wave14_rest.jsonl.
The original JSONL is never touched.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")

import wave14_screen as ws  # noqa: E402

WORK = os.path.join(HERE, "work")
ORIG = os.path.join(WORK, "screen_wave14.jsonl")
REST = os.path.join(WORK, "screen_wave14_rest.jsonl")


def main():
    done_tags = set()
    with open(ORIG) as f:
        for line in f:
            line = line.strip()
            if line:
                done_tags.add(json.loads(line)["tag"])
    tasks = ws.gen_w1(400, 0x714E) + ws.gen_w3(200, 0x314159)
    all_tags = [ws.sched_tag(fam, s) for fam, s in tasks]
    assert len(all_tags) == 602, len(all_tags)
    assert len(set(all_tags)) == 602, "task tags not unique!"
    missing = [(fam, s) for (fam, s), t in zip(tasks, all_tags)
               if t not in done_tags]
    print(f"total=602 done={len(done_tags)} missing={len(missing)}",
          flush=True)
    for fam, s in missing:
        print("  MISSING", ws.sched_tag(fam, s), flush=True)
    if os.path.exists(REST):
        # idempotence: never double-run
        existing = {json.loads(l)["tag"] for l in open(REST) if l.strip()}
        missing = [(f, s) for f, s in missing
                   if ws.sched_tag(f, s) not in existing]
        print(f"rest file exists; {len(missing)} still missing", flush=True)
    if not missing:
        print("NOTHING TO DO", flush=True)
        return
    t0 = time.time()
    from multiprocessing import Pool
    n = 0
    keeps = 0
    with open(REST, "a") as f, Pool(3) as pool:
        for res in pool.imap_unordered(ws.run_one, missing, chunksize=1):
            n += 1
            f.write(json.dumps(res) + "\n")
            f.flush()
            if res["keep"]:
                keeps += 1
                print(f"  KEEP {res['tag']} zseq={res['z_seq']:.1f} "
                      f"zrnd={res['z_rnd']:.1f}", flush=True)
            print(f"  ... {n}/{len(missing)} done", flush=True)
    print(f"=== rest done: {n} triaged, {keeps} new KEEPs "
          f"in {(time.time()-t0)/60:.1f}min ===", flush=True)


if __name__ == "__main__":
    main()
