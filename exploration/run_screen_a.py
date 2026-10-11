"""Run screen() on one Batch-A candidate; save JSON to results/<name>/screen.json.
Usage: python3 run_screen_a.py <name>   (model = models.<name>, fn = mix_<name>_np)
"""
import sys, os, json
import numpy as np

EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP)
from screen_lib import screen


def conv(o):
    if isinstance(o, dict):
        return {k: conv(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [conv(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    return o


def main():
    name = sys.argv[1]
    mod = __import__("models." + name, fromlist=["x"])
    fn = getattr(mod, "mix_%s_np" % name)
    res = screen(fn, name, verbose=True)
    outdir = os.path.join(EXP, "results", name)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "screen.json"), "w") as f:
        json.dump(conv(res), f, indent=1)
    print("[%s] screen.json written" % name)


if __name__ == "__main__":
    main()
