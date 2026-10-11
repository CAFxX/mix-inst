"""Delay batch for round-4 B/S/V families (ternary S-box fix)."""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP)
os.environ["PATH"] = (os.path.expanduser("~/tools/micromamba-root/bin") + ":" +
                       os.path.join(EXP, "bin") + ":" + os.environ["PATH"])
from run_synth import synth_one, REF_V

R4 = os.path.join(EXP, "round4")
CANDS = [
    ("blink2", "r4_blink.mix_blink2_np", "flat2/r4_blink2.v", "r4_blink2"),
    ("blink3", "r4_blink.mix_blink3_np", "flat2/r4_blink3.v", "r4_blink3"),
    ("blink4", "r4_blink.mix_blink4_np", "flat2/r4_blink4.v", "r4_blink4"),
    ("midori3", "r4_blink.mix_midori3_np", "flat2/r4_midori3.v", "r4_midori3"),
    ("speedy3", "r4_speedy.mix_speedy3_np", "flat2/r4_speedy3.v", "r4_speedy3"),
    ("speedy4", "r4_speedy.mix_speedy4_np", "flat2/r4_speedy4.v", "r4_speedy4"),
    ("skinny_xorlin", "r4_xorlinv.mix_skinny_xorlin_np", "r4_xorlinv.v", "r4_skinny_xorlin"),
]

print("measuring reference mul64 (fresh)...", flush=True)
ref = synth_one(REF_V, "mul64",
                os.path.join(R4, "results", "_ref4"))
print(f"REF: cells={ref['cells']} area={ref['area']} crit={ref['crit']}", flush=True)
BAR = 0.9 * ref["crit"]
print(f"bar={BAR:.1f}", flush=True)

rows = []
for name, modfn, rtl, top in CANDS:
    d = os.path.join(R4, "results", name)
    try:
        r = synth_one(os.path.join(R4, "rtl", rtl), top, d)
        crit = r["crit"]
        tag = "PASS" if crit <= BAR else "OUT"
        print(f"[{name}] crit={crit:.1f} r_ref={crit/ref['crit']:.3f} "
              f"cells={r['cells']} -> delay {tag}", flush=True)
        rows.append((name, crit, crit / ref["crit"], r["cells"], tag))
    except Exception as e:
        print(f"[{name}] synth FAILED: {str(e)[:300]}", flush=True)
        rows.append((name, None, None, None, "SYNTH-FAIL"))

print("\n=== B/S/V delay summary (bar %.1f) ===" % BAR)
print(f"{'name':14s} {'crit':>6s} {'x_mult':>7s} {'cells':>7s} gate")
for name, crit, xr, cells, tag in rows:
    cs = f"{crit:.1f}" if crit else "--"
    xs = f"{xr:.3f}" if xr else "--"
    ns = f"{cells}" if cells else "--"
    print(f"{name:14s} {cs:>6s} {xs:>7s} {ns:>7s} {tag}")
print(f"ref_crit={ref['crit']} ref_cells={ref['cells']}")
