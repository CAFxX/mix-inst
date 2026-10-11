#!/usr/bin/env python3
"""S0 screen for wave-1 candidates via authorized run_synth.py, sequential + polite.
Usage: s0_wave1.py <cand> [cand ...]
Appends RESULT records to adder_lat/s0_results.txt
"""
import os, re, subprocess, sys, time

EXP = "/home/hatch/workspace/mix/exploration"
AL = os.path.join(EXP, "adder_lat")
FB = os.path.join(EXP, "fast_battery", "candidates")
OUT = os.path.join(AL, "s0_results.txt")

def load_ok():
    try:
        with open("/proc/loadavg") as f:
            l1 = float(f.read().split()[0])
        return l1
    except Exception:
        return 99.0

def main():
    for cand in sys.argv[1:]:
        # polite: wait while box is heavily loaded (round_tweak has priority)
        while load_ok() > 22.0:
            print(f"[{cand}] load high, backing off 60s", flush=True)
            time.sleep(60)
        rtl = os.path.join(FB, cand, "rtl.v")
        workdir = os.path.join(AL, "s0_work", cand)
        t0 = time.time()
        r = subprocess.run(
            [sys.executable, os.path.join(EXP, "run_synth.py"), rtl, cand, workdir],
            capture_output=True, text=True, timeout=1200, cwd=EXP)
        dt = time.time() - t0
        m = re.search(r"^RESULT .*$", r.stdout, re.M)
        rec = m.group(0) if m else f"RESULT name={cand} SYNTH-FAIL rc={r.returncode}"
        line = f"{rec} wall_s={dt:.0f}"
        print(line, flush=True)
        with open(OUT, "a") as f:
            f.write(f"# {time.strftime('%Y-%m-%d %H:%M %Z')} {line}\n")
        if r.returncode != 0:
            print(r.stdout[-1500:], flush=True)
            print(r.stderr[-1500:], flush=True)

if __name__ == "__main__":
    main()
