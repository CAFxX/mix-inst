"""run_all.py -- synthesize frontier designs (S0-only, authorized run_synth path)
and run critpath.py analysis on each mapped netlist.

Polite concurrency: waits for <2 foreign heavy pipelines before each synth.
Checkpoint: per-design JSON + mapped netlist under critpath/work/<name>/.
"""
import os, sys, json, time, subprocess

MIX = "/home/hatch/workspace/mix"
EXPL = os.path.join(MIX, "exploration")
CRIT = os.path.join(EXPL, "critpath")
WORK = os.path.join(CRIT, "work")
GENLIB = os.path.join(MIX, "synth", "mini.genlib")
sys.path.insert(0, EXPL)
from run_synth import synth_one

HEAVY = ["yosys", "openroad", "RNG_test", "diffprof_", "s1_screen", "iverilog", "vvp"]

DESIGNS = [
    # (name, rtl_src, rounds)
    ("r22c_spn_mix4r_lp_nw", "/home/hatch/workspace/your_files/mix_rtl_pareto/mix_r22c_spn_mix4r_lp_nw.v", 4),
    ("r21_feist6_alt_notr_chioff31final_nw", "/home/hatch/workspace/your_files/mix_rtl_pareto/mix_r21_feist6_alt_notr_chioff31final_nw.v", 6),
    ("r21_feist6_alt_notr_3rot_ns_nw", "/home/hatch/workspace/your_files/mix_rtl_pareto/mix_r21_feist6_alt_notr_3rot_ns_nw.v", 6),
    ("r21b_3rot_ns_fm311_nw", "/home/hatch/workspace/your_files/mix_rtl_pareto/mix_r21b_3rot_ns_fm311_nw.v", 6),
    ("r9_feist6_rot311_nw", os.path.join(EXPL, "fast_battery/candidates/r9_feist6_rot311_nw/rtl.v"), 6),
    ("r8_feist6_s1_1sbox_nw", os.path.join(EXPL, "fast_battery/candidates/r8_feist6_s1_1sbox_nw/rtl.v"), 6),
    ("r15_feist6_parsplit_nw", os.path.join(EXPL, "fast_battery/candidates/r15_feist6_parsplit_nw/rtl.v"), 6),
    ("r21_feist6_alt_notr_chioff13all_fm311_nw", os.path.join(EXPL, "fast_battery/candidates/r21_feist6_alt_notr_chioff13all_fm311_nw/rtl.v"), 6),
]

def foreign_heavy_count():
    try:
        out = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return 99
    n = 0
    for line in out.splitlines():
        if "grep" in line:
            continue
        if any(h in line for h in HEAVY):
            n += 1
    # exclude our own yosys (called below) -- count before launching
    return n

def wait_for_slot():
    while True:
        n = foreign_heavy_count()
        if n < 2:
            return
        print(f"[run_all] {n} foreign heavies, backing off 120s", flush=True)
        time.sleep(120)

def main():
    os.makedirs(WORK, exist_ok=True)
    done = []
    for name, src, rounds in DESIGNS:
        out_json = os.path.join(WORK, name, "critpath.json")
        if os.path.exists(out_json):
            print(f"[run_all] {name}: already done, skipping", flush=True)
            done.append(name)
            continue
        assert os.path.exists(src), f"missing RTL: {src}"
        wait_for_slot()
        wdir = os.path.join(WORK, name)
        print(f"[run_all] synthesizing {name} ...", flush=True)
        r = synth_one(src, name, wdir)  # authorized path; dual-analyzer cross-checked
        print(f"[run_all] {name}: cells={r['cells']} crit={r['crit']}", flush=True)
        mapped = os.path.join(wdir, f"mapped_{name}.v")
        cp = os.path.join(CRIT, "critpath.py")
        rr = subprocess.run(
            [sys.executable, cp, mapped, GENLIB, "--topk", "10",
             "--rounds", str(rounds), "--name", name, "--json", out_json],
            capture_output=True, text=True, timeout=600)
        if rr.returncode != 0:
            print(f"[run_all] critpath FAILED for {name}:\n{rr.stderr[-2000:]}", flush=True)
            continue
        print(rr.stdout.splitlines()[0], flush=True)
        done.append(name)
    print(f"[run_all] DONE: {done}", flush=True)

if __name__ == "__main__":
    main()
