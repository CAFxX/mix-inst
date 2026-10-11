"""Round-2 calibrated screen runner.

Usage: python3 run_screen_cal.py <name> <dotted.model.fn>
Writes results/<name>/screen_cal.json and prints raw + calibrated verdicts.
"""
import sys, json, os, time
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_cal import screen_calibrated

name = sys.argv[1]
modname, fnname = sys.argv[2].rsplit(".", 1)
import importlib
fn = getattr(importlib.import_module(modname), fnname)

t0 = time.time()
res = screen_calibrated(fn, name, verbose=False)
dt = time.time() - t0
os.makedirs(f"results/{name}", exist_ok=True)
with open(f"results/{name}/screen_cal.json", "w") as f:
    json.dump(res, f, default=str)
print(f"[{name}] raw: perbit max|z|={res['raw_worst_perbit_z']:.2f} "
      f"@ {res['raw_perbit_loc'][0]} | red max|z|={res['raw_worst_red_z']:.2f} "
      f"@ {res['raw_red_loc'][0]} -> {res['raw_verdict']}")
print(f"[{name}] calibrated: {res['cal_verdict']} "
      f"(rej_pb={len(res['cal_rejected_perbit'])} rej_red={len(res['cal_rejected_red'])}) "
      f"[{dt:.0f}s]")
print(f"[{name}] screen_cal.json written")
