"""Background runner: calibrated screens for round-4 B-family remainders and all hybrid candidates.
Logs one line per candidate with cal_verdict / rejection counts. ~90s each, parallel workers."""
import os, sys, time, traceback
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "models"))
sys.path.insert(0, HERE)

from screen_cal import screen_calibrated  # noqa: E402

CANDS = [
    ("blink3", "r4_blink", "mix_blink3_np"),
    ("midori3", "r4_blink", "mix_midori3_np"),
    ("blink4", "r4_blink", "mix_blink4_np"),
    ("h_sandwich2", "r4_hybrid", "mix_h_sandwich2_np"),
    ("h_chifeist6", "r4_hybrid", "mix_h_chifeist6_np"),
    ("h_multspn", "r4_hybrid", "mix_h_multspn_np"),
    ("h_spnmult", "r4_hybrid", "mix_h_spnmult_np"),
    ("h_clmulspn", "r4_hybrid", "mix_h_clmulspn_np"),
    ("h_laimassey", "r4_hybrid", "mix_h_laimassey_np"),
    ("h_sandwich3", "r4_hybrid", "mix_h_sandwich3_np"),
    ("h_xorspn3", "r4_hybrid", "mix_h_xorspn3_np"),
    ("h_xorspn", "r4_hybrid", "mix_h_xorspn_np"),
    ("h_heterofeist", "r4_hybrid", "mix_h_heterofeist_np"),
]

RESULTS = os.path.join(HERE, "results", "screen_round4_remaining.txt")


def run_one(spec):
    name, modname, fnname = spec
    t0 = time.time()
    try:
        mod = __import__(modname)
        fn = getattr(mod, fnname)
        r = screen_calibrated(fn, name, verbose=True)
        verdict = r.get("cal_verdict") or ("CAL_PASS" if r.get("cal_pass") else "CAL_FLAG")
        line = (f"{name}: {verdict} | n_reject={r.get('n_reject')} "
                f"| rej_pb={r.get('rej_pb')} rej_red={r.get('rej_red')} "
                f"| maxz={r.get('max_abs_z')} | keys={r} | {time.time()-t0:.0f}s")
    except Exception as e:
        line = f"{name}: ERROR {e!r}\n{traceback.format_exc()}"
    with open(RESULTS, "a") as f:
        f.write(line + "\n")
        f.flush()
    print(line, flush=True)


if __name__ == "__main__":
    open(RESULTS, "w").write(f"# started {time.ctime()}\n")
    with Pool(4) as p:
        p.map(run_one, CANDS)
    with open(RESULTS, "a") as f:
        f.write(f"# done {time.ctime()}\n")
