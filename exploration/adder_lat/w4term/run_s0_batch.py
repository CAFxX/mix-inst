#!/usr/bin/env python3
"""S0 batch runner for w4t keeps. Runs run_synth.py on each bundle lacking s0/RESULT.
Serial (yosys is flock-serialized anyway). Logs to s0_batch.log."""
import os, subprocess, sys, time

BASE = "/home/hatch/workspace/mix/exploration/adder_lat/w4term/bundles"
RUN = "/home/hatch/workspace/mix/exploration/run_synth.py"
LOG = "/home/hatch/workspace/mix/exploration/adder_lat/w4term/s0_batch.log"

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

bundles = sorted(d for d in os.listdir(BASE) if d.startswith("w4t_"))
todo = [b for b in bundles
        if not os.path.exists(os.path.join(BASE, b, "s0", "RESULT"))]
log(f"{len(bundles)} bundles, {len(todo)} need S0")
for b in todo:
    bdir = os.path.join(BASE, b)
    rtl = os.path.join(bdir, "rtl.v")
    workdir = os.path.join(bdir, "s0")
    log(f"START {b}")
    try:
        r = subprocess.run(
            [sys.executable, RUN, rtl, b, workdir],
            capture_output=True, text=True, timeout=1800,
            cwd="/home/hatch/workspace/mix/exploration")
        # run_synth.py prints RESULT as last data line; extract it
        result = None
        for line in r.stdout.splitlines():
            if line.startswith("RESULT "):
                result = line
        if r.returncode == 0 and result:
            with open(os.path.join(workdir, "RESULT"), "w") as f:
                f.write(result + "\n")
            log(f"DONE {b}: {result}")
        else:
            log(f"FAIL {b}: rc={r.returncode} out_tail={r.stdout[-500:]} err_tail={r.stderr[-500:]}")
    except subprocess.TimeoutExpired:
        log(f"TIMEOUT {b} after 1800s")
    except Exception as e:
        log(f"ERROR {b}: {e}")
log("BATCH COMPLETE")
