#!/usr/bin/env python3
"""S1+S2 screen for wave candidates via official fast_battery scripts, sequential.
Usage: s12_wave.py <cand> [cand ...]
S1: src/s1_screen.py <cand> <outdir>   (official amended 4-family screen)
S2: build diffprof + run with kill_repeats (official differential early-kill)
Results appended to adder_lat/s12_results.txt
"""
import json, os, subprocess, sys, time

EXP = "/home/hatch/workspace/mix/exploration"
AL = os.path.join(EXP, "adder_lat")
FB = os.path.join(EXP, "fast_battery")
OUT = os.path.join(AL, "s12_results.txt")
BLD = os.path.join(FB, "build")

def load_ok():
    try:
        with open("/proc/loadavg") as f:
            return float(f.read().split()[0])
    except Exception:
        return 99.0

def polite():
    while load_ok() > 22.0:
        print("load high, backing off 60s", flush=True)
        time.sleep(60)

def main():
    os.makedirs(BLD, exist_ok=True)
    for cand in sys.argv[1:]:
        polite()
        cdir = os.path.join(FB, "candidates", cand)
        outdir = os.path.join(AL, "s1_out", cand)
        os.makedirs(outdir, exist_ok=True)
        # S1
        t0 = time.time()
        r = subprocess.run([sys.executable, os.path.join(FB, "src", "s1_screen.py"),
                            cand, outdir], capture_output=True, text=True,
                           timeout=3600, cwd=FB)
        dt1 = time.time() - t0
        tail = r.stdout.strip().split("\n")[-4:]
        s1verdict = "S1-PASS" if r.returncode == 0 else ("S1-FLAG" if r.returncode == 2 else "S1-INFRA")
        line1 = f"{cand}: {s1verdict} rc={r.returncode} wall={dt1:.0f}s :: {' | '.join(tail)}"
        print(line1, flush=True)
        with open(OUT, "a") as f:
            f.write(f"# {time.strftime('%Y-%m-%d %H:%M %Z')} {line1}\n")
        if r.returncode != 0:
            with open(os.path.join(AL, f"s1_{cand}.log"), "w") as f:
                f.write(r.stdout + "\n==== STDERR ====\n" + r.stderr)
            continue
        # S2: build diffprof, run
        polite()
        exe = os.path.join(BLD, f"diffprof_{cand}")
        r = subprocess.run(["gcc", "-O2", "-o", exe,
                            os.path.join(FB, "src", "s2_diffprof.c"),
                            os.path.join(cdir, "impl.c"), "-lm"],
                           capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            line = f"{cand}: S2-BUILD-FAIL {r.stderr[-300:]}"
            print(line, flush=True)
            with open(OUT, "a") as f:
                f.write(f"# {line}\n")
            continue
        kill_rep = open(os.path.join(FB, "ref", "s2_kill_repeats.txt")).read().strip()
        key = json.load(open(os.path.join(cdir, "meta.json")))["practrand_keys"][0]
        t0 = time.time()
        r = subprocess.run([exe, key, "22", kill_rep], capture_output=True,
                           text=True, timeout=1800)
        dt2 = time.time() - t0
        s2verdict = "S2-PASS" if r.returncode == 0 else ("S2-KILL" if r.returncode == 2 else "S2-INFRA")
        # extract max|z| and repeats summary
        zs = []
        for ln in r.stdout.split("\n"):
            p = ln.split()
            if len(p) >= 4 and p[0].startswith("0x"):
                try:
                    zs.append((float(p[1]), int(p[3]), p[0]))
                except ValueError:
                    pass
        if zs:
            worst = max(zs)
            det = f"max|z|={worst[0]:.1f} repeats={worst[1]} delta={worst[2]}"
        else:
            det = r.stdout.strip().split("\n")[-2:]
            det = " | ".join(det) if isinstance(det, list) else det
        line2 = f"{cand}: {s2verdict} rc={r.returncode} wall={dt2:.0f}s :: {det}"
        print(line2, flush=True)
        with open(OUT, "a") as f:
            f.write(f"# {time.strftime('%Y-%m-%d %H:%M %Z')} {line2}\n")
        with open(os.path.join(AL, f"s2_{cand}.log"), "w") as f:
            f.write(r.stdout + "\n==== STDERR ====\n" + r.stderr)

if __name__ == "__main__":
    main()
