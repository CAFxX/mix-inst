"""Round 5 delay probes: Yosys/ABC unit-delay synthesis per candidate RTL.

Serialized, one at a time; checks ps for competing openroad/yosys jobs and
backs off. Usage: python3 probe_r5.py [name ...]  (default: all in rtl/)
Appends RESULT lines to results/probe_r5.txt.
"""
import os
import subprocess
import sys
import time

R5 = "/home/hatch/workspace/mix/exploration/round5"
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from run_synth import synth_one, REF_V  # noqa: E402

RESULTS = os.path.join(R5, "results", "probe_r5.txt")


def busy():
    # count real processes by executable name (comm), so wrapper shells
    # whose -c string mentions openroad are not double-counted
    r = subprocess.run(["ps", "-eo", "comm"], capture_output=True, text=True)
    comms = r.stdout.split()
    n = 0
    n += 2 * sum(1 for c in comms if c == "openroad")
    n += 1 * sum(1 for c in comms if c in ("yosys", "abc"))
    return n


def main():
    names = sys.argv[1:] or sorted(
        f[:-2] for f in os.listdir(os.path.join(R5, "rtl")) if f.endswith(".v"))
    with open(RESULTS, "a") as f:
        f.write(f"# probe run {time.ctime()}\n")
    print("measuring mul64 reference...", flush=True)
    ref = synth_one(REF_V, "mul64", os.path.join(R5, "results", "_probe_ref"))
    ref_crit = ref["crit"]
    print(f"REF mul64: cells={ref['cells']} crit={ref_crit:.1f}", flush=True)
    with open(RESULTS, "a") as f:
        f.write(f"# ref_crit={ref_crit:.2f}\n")
    for v in names:
        # file stem: accept 'r5_gift' or 'r5_r5_gift' -> file r5_r5_gift.v
        stem = v if v.startswith("r5_r5_") else "r5_" + v
        # module name: file r5_r5_gift.v -> module r5_gift
        top = stem[3:] if stem.startswith("r5_r5_") else stem
        src = os.path.join(R5, "rtl", stem + ".v")
        while busy() >= 3:
            print(f"[{v}] box busy (openroad running), backing off 60s",
                  flush=True)
            time.sleep(60)
        t0 = time.time()
        try:
            r = synth_one(src, top, os.path.join(R5, "results", f"_probe_{v}"))
            line = (f"{v}: cells={r['cells']} area={r['area']:.0f} "
                    f"crit={r['crit']:.1f} xmult={r['crit']/ref_crit:.3f} "
                    f"gate={'PASS' if r['crit'] <= 44.3 else 'OUT'} "
                    f"({time.time()-t0:.0f}s)")
        except Exception as e:
            line = f"{v}: SYNTH_ERROR {str(e)[:200]}"
        print(line, flush=True)
        with open(RESULTS, "a") as f:
            f.write(line + "\n")
            f.flush()


if __name__ == "__main__":
    main()
