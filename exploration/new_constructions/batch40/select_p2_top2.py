#!/usr/bin/env python3
"""Select top-2 NEW ormM6 p2 keeps for S0: lowest z, excluding any schedule
identical to the already-S0'd t6_ormM6a (pilot rank-0) or to each other.
Prints JSON lines with jsonl index (for gen_b40_bundle.py), z, stages."""
import json, sys

p2 = [json.loads(l) for l in open("keeps_ormM6_p2.jsonl") if l.strip()]
pilot = [json.loads(l) for l in open("keeps_ormM6.jsonl") if l.strip()]
s0_done = {tuple(tuple(s) for s in pilot[0]["stages"])}  # t6_ormM6a
picked, seen = [], set(s0_done)
for i, e in enumerate(p2):
    st = tuple(tuple(s) for s in e["stages"])
    if st in seen:
        continue
    seen.add(st)
    picked.append({"jsonl_index": i, "z": e["z"], "stages": e["stages"],
                   "also_in_pilot": st in {tuple(tuple(s) for s in p["stages"]) for p in pilot}})
    if len(picked) == 2:
        break
print(json.dumps({"n_p2_keeps": len(p2), "top2_new": picked}, indent=1))
