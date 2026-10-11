"""Round-4 batch driver: check_rtl + synthesis (delay gate) for all candidates.

Usage: python3 run_batch.py
Reference mul64 measured fresh once; ratios vs ref AND vs 41.9 (round-2
Wallace-dense CSD const-mult reference, documented in candidates.md).
Writes results/<name>/synth.json per candidate; prints a summary table.
"""
import os
import sys
import json
import subprocess

EXP = "/home/hatch/workspace/mix/exploration"
R4 = os.path.join(EXP, "round4")
sys.path.insert(0, EXP)
os.environ["PATH"] = os.path.join(EXP, "bin") + ":" + os.environ["PATH"]
os.environ["PYTHONPATH"] = os.path.join(R4, "models") + ":" + os.environ.get("PYTHONPATH", "")

from run_synth import synth_one, REF_V

CSD_REF = 41.9  # round-2 Wallace-dense 64-bit const-mult (23 CSD terms)

CANDS = [
    # (name, dotted.model.fn, rtl, top)
    ("simeck_f10", "r4_xsfeistel.mix_simeck_f10_np", "flat2/r4_simeck_f10.v", "r4_simeck_f10"),
    ("simon_f10", "r4_xsfeistel.mix_simon_f10_np", "flat2/r4_simon_f10.v", "r4_simon_f10"),
    ("simeck_f12", "r4_xsfeistel.mix_simeck_f12_np", "flat2/r4_simeck_f12.v", "r4_simeck_f12"),
    ("dbland_f8", "r4_xsfeistel.mix_dbland_f8_np", "flat2/r4_dbland_f8.v", "r4_dbland_f8"),
    ("xsm_c3", "r4_xsm.mix_xsm_c3_np", "flat/r4_xsm_c3.v", "r4_xsm_c3"),
    ("xsm_c8", "r4_xsm.mix_xsm_c8_np", "flat/r4_xsm_c8.v", "r4_xsm_c8"),
    ("xsm_sa", "r4_xsm.mix_xsm_sa_np", "r4_xsm.v", "r4_xsm_sa"),
    ("fmix32h_a", "r4_fmix32.mix_fmix32h_a_np", "flat/r4_fmix32h_a.v", "r4_fmix32h_a"),
    ("fmix32h_b", "r4_fmix32.mix_fmix32h_b_np", "flat/r4_fmix32h_b.v", "r4_fmix32h_b"),
    ("gl5_f6", "r4_glfeistel.mix_gl5_f6_np", "flat2/r4_gl5_f6.v", "r4_gl5_f6"),
    ("gl5_f8", "r4_glfeistel.mix_gl5_f8_np", "flat2/r4_gl5_f8.v", "r4_gl5_f8"),
    ("skinny_xorlin", "r4_xorlinv.mix_skinny_xorlin_np", "r4_xorlinv.v", "r4_skinny_xorlin"),
    ("blink2", "r4_blink.mix_blink2_np", "flat2/r4_blink2.v", "r4_blink2"),
    ("blink3", "r4_blink.mix_blink3_np", "flat2/r4_blink3.v", "r4_blink3"),
    ("blink4", "r4_blink.mix_blink4_np", "flat2/r4_blink4.v", "r4_blink4"),
    ("midori3", "r4_blink.mix_midori3_np", "flat2/r4_midori3.v", "r4_midori3"),
    ("speedy3", "r4_speedy.mix_speedy3_np", "flat2/r4_speedy3.v", "r4_speedy3"),
    ("speedy4", "r4_speedy.mix_speedy4_np", "flat2/r4_speedy4.v", "r4_speedy4"),
]

BAR = 44.3


def main():
    print("measuring reference mul64 (fresh)...", flush=True)
    ref = synth_one(REF_V, "mul64", os.path.join(R4, "results", "_ref"))
    print(f"REF: cells={ref['cells']} area={ref['area']:.0f} crit={ref['crit']:.1f}", flush=True)
    rows = []
    for name, dotted, rtl, top in CANDS:
        wd = os.path.join(R4, "results", name)
        os.makedirs(wd, exist_ok=True)
        # 1. RTL equivalence
        r = subprocess.run(
            [sys.executable, os.path.join(EXP, "check_rtl.py"), dotted,
             os.path.join(R4, "rtl", rtl), top, os.path.join(wd, "_chk"), "200"],
            capture_output=True, text=True, timeout=600)
        if "RTLCHECK" not in r.stdout or "PASS" not in r.stdout:
            print(f"[{name}] RTLCHECK FAILED:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
            rows.append((name, None, None, None, None, "RTLCHECK-FAIL"))
            continue
        # 2. synthesis
        try:
            d = synth_one(os.path.join(R4, "rtl", rtl), top, os.path.join(wd, "_syn"))
        except Exception as e:
            print(f"[{name}] synth FAILED: {e}")
            rows.append((name, None, None, None, None, "SYNTH-FAIL"))
            continue
        with open(os.path.join(wd, "synth.json"), "w") as f:
            json.dump(dict(dut=d, ref=ref), f)
        rr = d["crit"] / ref["crit"]
        rc = d["crit"] / CSD_REF
        gate = "PASS" if d["crit"] <= BAR else "OUT"
        print(f"[{name}] crit={d['crit']:.1f} r_ref={rr:.3f} r_csd={rc:.3f} cells={d['cells']} -> delay {gate}",
              flush=True)
        rows.append((name, d["crit"], rr, rc, d["cells"], gate))
    print("\n=== round-4 delay summary (bar %.1f) ===" % BAR)
    print(f"{'name':14s} {'crit':>6s} {'x_mult':>7s} {'x_csd':>7s} {'cells':>7s} gate")
    for name, crit, rr, rc, cells, gate in rows:
        if crit is None:
            print(f"{name:14s} {'--':>6s} {'--':>7s} {'--':>7s} {'--':>7s} {gate}")
        else:
            print(f"{name:14s} {crit:6.1f} {rr:7.3f} {rc:7.3f} {cells:7d} {gate}")
    print(f"ref_crit={ref['crit']:.1f} ref_cells={ref['cells']}")


if __name__ == "__main__":
    main()
