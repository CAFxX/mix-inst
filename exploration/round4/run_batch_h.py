"""Delay batch for round-4 HYBRID track (8 candidates)."""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP)
os.environ["PATH"] = (os.path.expanduser("~/tools/micromamba-root/bin") + ":" +
                       os.path.join(EXP, "bin") + ":" + os.environ["PATH"])
from run_synth import synth_one, REF_V

R4 = os.path.join(EXP, "round4")
CANDS = [
    ("h_sandwich2", "r4_h_sandwich2"),
    ("h_chifeist6", "r4_h_chifeist6"),
    ("h_multspn", "r4_h_multspn"),
    ("h_spnmult", "r4_h_spnmult"),
    ("h_clmulspn", "r4_h_clmulspn"),
    ("h_laimassey", "r4_h_laimassey"),
    ("h_xorspn", "r4_h_xorspn"),
    ("h_heterofeist", "r4_h_heterofeist"),
]

print("measuring reference mul64 (fresh)...", flush=True)
ref = synth_one(REF_V, "mul64", os.path.join(R4, "results", "_refh"))
print(f"REF: cells={ref['cells']} crit={ref['crit']}", flush=True)
BAR = 44.3
print(f"bar={BAR}", flush=True)

rows = []
for name, top in CANDS:
    d = os.path.join(R4, "results", name)
    try:
        r = synth_one(os.path.join(R4, "rtl", "flat2", top + ".v"), top, d)
        crit = r["crit"]
        tag = "PASS" if crit <= BAR else "OUT"
        print(f"[{name}] crit={crit:.1f} r_ref={crit/ref['crit']:.3f} "
              f"cells={r['cells']} -> delay {tag}", flush=True)
        rows.append((name, crit, crit / ref["crit"], r["cells"], tag))
    except Exception as e:
        print(f"[{name}] synth FAILED: {str(e)[:200]}", flush=True)
        rows.append((name, None, None, None, "SYNTH-FAIL"))

print("\n=== hybrid delay summary (bar %.1f) ===" % BAR)
print(f"{'name':16s} {'crit':>6s} {'x_mult':>7s} {'cells':>7s} gate")
for name, crit, xr, cells, tag in rows:
    cs = f"{crit:.1f}" if crit else "--"
    xs = f"{xr:.3f}" if xr else "--"
    ns = f"{cells}" if cells else "--"
    print(f"{name:16s} {cs:>6s} {xs:>7s} {ns:>7s} {tag}")
print(f"ref_crit={ref['crit']} ref_cells={ref['cells']}")
