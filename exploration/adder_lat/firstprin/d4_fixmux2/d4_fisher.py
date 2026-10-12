#!/usr/bin/env python3
"""Fisher triage (screen_lin_diff verbatim) for D4 variants.
Usage: d4_fisher.py {A|C} <p1> <p2> <label>
"""
import os, sys, time, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import screen_lin_diff
from screen_lib import KEYS, N
import d4_model as M

def main():
    kind, p1, p2, label = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    fn = (lambda x: M.apply_A(x, p1, p2)) if kind == "A" else (lambda x: M.apply_C(x, p1, p2))
    keys = [int(k) for k in KEYS]
    print(f"D4 Fisher triage: {label} kind={kind} p1={p1} p2={p2}", flush=True)
    t0 = time.time()
    seq = M.gen_seq(fn, keys, N)
    print(f"seq gen: {time.time()-t0:.1f}s", flush=True)
    t0 = time.time()
    res = screen_lin_diff(seq, verbose=False)
    print(f"screen: {time.time()-t0:.1f}s", flush=True)
    ld = [res["lin_detail"][k]["D"] for k in res["lin_detail"]]
    dz = [res["diff_detail"][k]["worst_z"] for k in res["diff_detail"]]
    print(f"LIN D range: {min(ld)}..{max(ld)} nrej={len(res['lin_rejected'])}", flush=True)
    print(f"DIFF worst|z| range: {min(dz):.1f}..{max(dz):.1f} nrej={len(res['diff_rejected'])}", flush=True)
    print(f"VERDICT lin={res['lin_verdict']} diff={res['diff_verdict']}", flush=True)
    json.dump({"label": label, "kind": kind, "p1": p1, "p2": p2,
               "lin_verdict": res["lin_verdict"], "diff_verdict": res["diff_verdict"],
               "nrej_lin": len(res["lin_rejected"]), "nrej_diff": len(res["diff_rejected"]),
               "lin_D": ld, "diff_worstz": dz},
              open(f"fisher_{label}.json", "w"), indent=1)
    print(f"wrote fisher_{label}.json", flush=True)

if __name__ == "__main__":
    main()
