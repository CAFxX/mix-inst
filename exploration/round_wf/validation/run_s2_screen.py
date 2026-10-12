#!/usr/bin/env python3
"""Phase C S2 screen for round_wf candidates, with polite-concurrency backoff.

Usage: run_s2_screen.py <candidate_name>
  candidate lives in round_wf/validation/candidates/<name>/.
Steps: foreign-heavy backoff (<=2 system-wide, count by binary) ->
  build diffprof -> xcheck 10k -> S2 N=2^22 kill_repeats=10.
Logs to round_wf/validation/logs/s2_<name>.log
"""
import os, re, subprocess, sys, time

EXP = "/home/hatch/workspace/mix/exploration"
CAND = sys.argv[1]
CDIR = f"{EXP}/round_wf/validation/candidates/{CAND}"
LOGD = f"{EXP}/round_wf/validation/logs"
BLD = f"{EXP}/fast_battery/build"
# Heavy binaries only (not the lightweight driver .py processes, which are
# long-lived but mostly idle; their heavy children are what the gate is for).
HEAVY = ("yosys", "RNG_test", "diffprof_", "s1_screen", "iverilog", "vvp")

def foreign_heavy_count():
    try:
        ps = subprocess.run(["ps", "aux"], capture_output=True, text=True).stdout
    except Exception:
        return 99
    n = 0
    for line in ps.splitlines():
        if "run_s2_screen" in line:
            continue
        if any(h in line for h in HEAVY):
            n += 1
    return n

def main():
    os.makedirs(LOGD, exist_ok=True)
    log = open(f"{LOGD}/s2_{CAND}.log", "w")
    def emit(s):
        print(s, flush=True); log.write(s + "\n"); log.flush()
    # polite backoff
    while True:
        n = foreign_heavy_count()
        if n < 2:
            break
        emit(f"[polite] {n} foreign heavies, sleeping 120s")
        time.sleep(120)
    emit(f"[gate] proceeding with {foreign_heavy_count()} foreign heavies")
    # build
    binpath = f"{BLD}/diffprof_{CAND}"
    r = subprocess.run(["gcc", "-O2", "-o", binpath,
                        f"{EXP}/fast_battery/src/s2_diffprof.c",
                        f"{CDIR}/impl.c", "-lm"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        emit("BUILD FAIL\n" + r.stderr[-2000:]); return 2
    emit("build OK")
    # xcheck
    r = subprocess.run([sys.executable, f"{EXP}/round_wf/validation/xcheck_wf.py",
                        CDIR, binpath, "10000", f"{LOGD}/vecs_{CAND}.txt"],
                       capture_output=True, text=True)
    emit(r.stdout[-500:] + r.stderr[-500:])
    if r.returncode != 0:
        emit("XCHECK FAIL"); return 2
    # S2
    emit("S2 start N=2^22 kill=10")
    t0 = time.time()
    r = subprocess.run([binpath, "0x123456789abcdef0", "22", "10"],
                       capture_output=True, text=True, timeout=3600)
    dt = time.time() - t0
    emit(r.stdout[-6000:])
    if r.stderr:
        emit("STDERR tail: " + r.stderr[-1000:])
    emit(f"S2 done rc={r.returncode} wall={dt:.0f}s")
    # verdict parse
    m = re.search(r"PASS max_repeats=(\d+) max\|z\|=([\d.]+)", r.stdout)
    k = re.search(r"KILL", r.stdout)
    if k:
        emit("VERDICT: S2-KILL"); return 1
    if m:
        emit(f"VERDICT: S2-PASS repeats={m.group(1)} max|z|={m.group(2)}"); return 0
    emit("VERDICT: UNKNOWN (parse manually)"); return 3

if __name__ == "__main__":
    sys.exit(main())
