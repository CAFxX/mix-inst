import sys, json
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import screen

name = sys.argv[1]
modname, fnname = sys.argv[2].rsplit(".", 1)
import importlib
fn = getattr(importlib.import_module(modname), fnname)
# NOTE: screen(..., verbose=True) crashes in screen_lib's own summary print
# (TypeError: 'int' object is not subscriptable on red_loc); the statistics
# themselves are unaffected. Run verbose=False and print our own summary.
# Bug + repro reported to the parent separately; screen_lib.py untouched.
res = screen(fn, name, verbose=False)
with open(f"results/{name}/screen.json", "w") as f:
    json.dump(res, f, default=str)
pl, rl = res["perbit_loc"], res["red_loc"]
pl_loc = f"in={pl[1]}" if pl[0] == "KEY-SWEEP" else f"key={pl[1]:#018x}"
print(f"[{name}] per-bit worst |z|={res['worst_perbit_z']:.2f} "
      f"(scen={pl[0]} {pl_loc} bit={pl[2]}); "
      f"reduction worst |z|={res['worst_red_z']:.2f} (scen={rl[0]} "
      f"key={rl[1]:#018x} {rl[2]}); "
      f"flagged pb: {res['flagged_pb_scenarios'] or 'none'}; "
      f"flagged red: {res['flagged_red_scenarios'] or 'none'} -> {res['verdict']}")
print(f"[{name}] screen.json written, verdict={res['verdict']}")
