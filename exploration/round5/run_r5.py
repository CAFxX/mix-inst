"""Round 5 screen runner: bijectivity spot-check (600k) + calibrated screen
for all r5 candidates. ~90s each; use 2 workers to respect box load."""
import os
import sys
import time
import traceback
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "models"))
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")

from screen_cal import screen_calibrated  # noqa: E402
from screen_lib import bijectivity_spotcheck  # noqa: E402
from r5 import CANDIDATES  # noqa: E402

RESULTS = os.path.join(HERE, "results", "screen_r5.txt")


def run_one(spec):
    name, fn, track, comp = spec
    t0 = time.time()
    try:
        bc = bijectivity_spotcheck(fn, name, n=600000, seed=99)
        r = screen_calibrated(fn, name, verbose=False)
        verdict = r.get("cal_verdict") or ("CAL_PASS" if r.get("cal_pass")
                                           else "CAL_FLAG")
        line = (f"{name}: {verdict} | bij={bc} "
                f"| rej_pb={r.get('rej_pb')} rej_red={r.get('rej_red')} "
                f"| maxz={r.get('max_abs_z')} | {time.time()-t0:.0f}s")
    except Exception as e:
        line = f"{name}: ERROR {e!r}\n{traceback.format_exc()}"
    with open(RESULTS, "a") as f:
        f.write(line + "\n")
        f.flush()
    print(line, flush=True)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    done = set()
    if os.path.exists(RESULTS):
        with open(RESULTS) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and ":" in line:
                    done.add(line.split(":")[0].strip())
    else:
        open(RESULTS, "w").write("# round5 screens\n")
    todo = [c for c in CANDIDATES if c[0] not in done]
    print(f"skipping {len(done)} done, screening {len(todo)}", flush=True)
    with Pool(2) as p:
        p.map(run_one, todo)
    with open(RESULTS, "a") as f:
        f.write("# done\n")
