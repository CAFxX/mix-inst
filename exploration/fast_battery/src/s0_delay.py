#!/usr/bin/env python3
"""S0: unit-delay synthesis probe (fast staged battery).
Usage: s0_delay.py <candidate> <outdir>

Synthesizes candidates/<cand>/rtl.v with Yosys + ABC against mini.genlib
(unit-delay model) and measures the critical path. The 64x64 multiplier
reference is measured once through the IDENTICAL flow and cached in
ref/mult_ref.txt; subsequent runs reuse it so S0 stays in the seconds range.

FLOW NOTE (2026-10-01): the historical flow used `abc -fast`, but the yosys
installed on this VM (0.69+ conda-forge, post-reboot reinstall) dropped the
`-fast` option, so S0 uses `abc -genlib mini.genlib` (default ABC script).
This changes absolute unit-delays vs the old 44.3u bar, therefore the bar is
expressed as a RATIO: dut_crit <= 0.9 * mult_crit (the user's actual
requirement is "latency no higher than a multiplier"). Both DUT and reference
go through the identical flow, so the ratio is apples-to-apples.

Also runs a mapped-netlist equivalence spot-check: the ABC-mapped netlist is
simulated (iverilog + src/cells_sim.v) on 1000 random (v,k) vectors against
the Python model. A synthesis miscompile can never pass as a fast design.

Writes s0_result.json into outdir. Exit 0 on PASS, 2 on delay FAIL or
equivalence mismatch.
"""
import importlib.util
import json
import os
import random
import re
import subprocess
import sys
import time

FB = "/home/hatch/workspace/mix/exploration/fast_battery"
EXP = "/home/hatch/workspace/mix/exploration"
MIX = "/home/hatch/workspace/mix"
SYNTH = os.path.join(MIX, "synth")
GENLIB = os.path.join(SYNTH, "mini.genlib")
# PINNED TOOLCHAIN (2026-10-02): bare "yosys" resolves via PATH and silently
# picked up /usr/bin/yosys 0.33 instead of the conda 0.69, producing different
# delay numbers for identical RTL (78.3u vs 56.5u). Always use this path and
# assert the version before synthesizing.
YOSYS = "/home/hatch/tools/micromamba-root/envs/sky130/bin/yosys"
YOSYS_WANT = "0.69"
REF_V = os.path.join(SYNTH, "mul64.v")
RATIO_BAR = 0.9
EQUIV_VECS = 1000

YS_TMPL = """# fast_battery S0 flow. ABC script: src/abc_nodretime.script
# (= yosys default for -genlib with dretime REMOVED; see that file for why).
read_verilog {src}
hierarchy -check -top {top}
proc; opt; flatten; opt
memory_map; opt
techmap; opt
abc -genlib {genlib} -script {abc_script}
opt; clean
stat
write_verilog -noattr {mapped}
"""


def parse_analyze(out):
    m = re.search(r"cells:\s*(\d+)\s+total_area:\s*([\d.]+)\s+critical_path:\s*([\d.]+)", out)
    assert m, f"could not parse analyzer output:\n{out}"
    return dict(cells=int(m.group(1)), area=float(m.group(2)), crit=float(m.group(3)))


def synth_one(src, top, workdir):
    workdir = os.path.abspath(workdir)
    os.makedirs(workdir, exist_ok=True)
    src = os.path.abspath(src)
    mapped = os.path.join(workdir, f"mapped_{top}.v")
    ys = os.path.join(workdir, f"s_{top}.ys")
    with open(ys, "w") as f:
        f.write(YS_TMPL.format(src=src, top=top, genlib=GENLIB,
                               abc_script=os.path.join(FB, "src", "abc_nodretime.script"),
                               mapped=mapped))
    vv = subprocess.run([YOSYS, "-V"], capture_output=True, text=True, timeout=60)
    if YOSYS_WANT not in (vv.stdout + vv.stderr):
        raise RuntimeError(f"wrong yosys at {YOSYS}: want {YOSYS_WANT}, got {(vv.stdout+vv.stderr)[:120]}")
    r = subprocess.run([YOSYS, "-s", ys], capture_output=True, text=True,
                       cwd=workdir, timeout=900)
    if r.returncode != 0 or not os.path.exists(mapped):
        raise RuntimeError(f"yosys failed for {top}:\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
    a1 = subprocess.run([sys.executable, os.path.join(SYNTH, "analyze.py"),
                         mapped, GENLIB], capture_output=True, text=True, timeout=300)
    a2 = subprocess.run([sys.executable, os.path.join(EXP, "analyze2.py"),
                         mapped, GENLIB], capture_output=True, text=True, timeout=300)
    for tag, a in (("analyze.py", a1), ("analyze2.py", a2)):
        if a.returncode != 0:
            raise RuntimeError(
                f"{tag} crashed on {top} (rc={a.returncode}):\n{a.stderr[-3000:]}")
    try:
        r1, r2 = parse_analyze(a1.stdout), parse_analyze(a2.stdout)
    except AssertionError as e:
        # parse failures hide the analyzer's real error (it prints to stderr);
        # surface both analyzers' stderr so the root cause is visible.
        raise RuntimeError(
            f"could not parse analyzer output for {top}:\n"
            f"--- analyze.py rc={a1.returncode} stderr ---\n{a1.stderr[-2000:]}\n"
            f"--- analyze2.py rc={a2.returncode} stderr ---\n{a2.stderr[-2000:]}"
        ) from e
    if abs(r1["crit"] - r2["crit"]) > 1e-6 or abs(r1["area"] - r2["area"]) > 1e-6 \
            or r1["cells"] != r2["cells"]:
        raise RuntimeError(f"analyzer MISMATCH for {top}: {r1} vs {r2}")
    return r1, mapped


def get_ref():
    cache = os.path.join(FB, "ref", "mult_ref.txt")
    if os.path.exists(cache):
        return json.load(open(cache)), True
    print("[S0] measuring multiplier reference (one-time, cached)...", flush=True)
    t0 = time.time()
    r, mapped = synth_one(REF_V, "mul64", os.path.join(FB, "ref", "_mult"))
    ok, msg = equiv_check_generic(
        mapped, "mul64", ("a", "b", "p"),
        lambda a, b: (a * b) & ((1 << 64) - 1),
        os.path.join(FB, "ref"), tag="mult")
    if not ok:
        raise RuntimeError(f"reference multiplier mapped-netlist mismatch: {msg}")
    print(f"[S0] reference cached in {time.time()-t0:.0f}s", flush=True)
    json.dump(r, open(cache, "w"))
    return r, False


def load_model(cand):
    spec = importlib.util.spec_from_file_location(
        "model_" + cand, f"{FB}/candidates/{cand}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.mix


def equiv_check_generic(mapped, top, ports, model_fn, outdir, tag="dut"):
    """Simulate the mapped netlist on EQUIV_VECS random vectors vs model_fn.

    ports = (in1, in2, out) port names; model_fn(in1, in2) -> expected out.
    Returns (ok, detail)."""
    pin1, pin2, pout = ports
    rng = random.Random(0xE9CE)
    vecs = [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(EQUIV_VECS)]
    vf = os.path.join(outdir, f"_equiv_vecs_{tag}.txt")
    with open(vf, "w") as f:
        for x, y in vecs:
            f.write("%016x %016x %016x\n" % (x, y, model_fn(x, y)))
    tb = os.path.join(outdir, f"_equiv_tb_{tag}.v")
    with open(tb, "w") as f:
        f.write(r"""module tb_equiv;
  reg [63:0] in1, in2; wire [63:0] outw;
  %s dut(.%s(in1), .%s(in2), .%s(outw));
  reg [63:0] x, y, e; integer f, n, err;
  initial begin
    f = $fopen("%s", "r"); n = 0; err = 0;
    while ($fscanf(f, "%%h %%h %%h", x, y, e) == 3) begin
      in1 = x; in2 = y; #1; n = n + 1;
      if (outw !== e) begin err = err + 1;
        if (err < 5) $display("MISMATCH x=%%h y=%%h got=%%h exp=%%h", x, y, outw, e); end
    end
    $display("EQUIV n=%%0d err=%%0d", n, err); $finish;
  end
endmodule
""" % (top, pin1, pin2, pout, vf))
    sim = os.path.join(outdir, f"_equiv_sim_{tag}")
    r = subprocess.run(["iverilog", "-o", sim, mapped,
                        os.path.join(FB, "src", "cells_sim.v"), tb],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        return False, f"iverilog compile failed:\n{r.stderr[-1500:]}"
    r = subprocess.run(["vvp", sim], capture_output=True, text=True, timeout=600)
    m = re.search(r"EQUIV n=(\d+) err=(\d+)", r.stdout)
    if not m:
        return False, f"no EQUIV line:\n{r.stdout[-1500:]}\n{r.stderr[-500:]}"
    ok = int(m.group(2)) == 0 and int(m.group(1)) == EQUIV_VECS
    return ok, f"n={m.group(1)} err={m.group(2)}"


def equiv_check(cand, top, mapped, outdir):
    """DUT mapped-netlist check vs the candidate's Python model."""
    return equiv_check_generic(mapped, top, ("val", "key", "out"),
                               load_model(cand), outdir, tag=cand)


def main():
    cand, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    meta = json.load(open(f"{FB}/candidates/{cand}/meta.json"))
    top = meta["rtl_top"]
    src = f"{FB}/candidates/{cand}/rtl.v"

    t0 = time.time()
    ref, cached = get_ref()
    t_ref = time.time() - t0
    t1 = time.time()
    dut, mapped = synth_one(src, top, os.path.join(outdir, "_synth"))
    t_dut = time.time() - t1
    t2 = time.time()
    eq_ok, eq_msg = equiv_check(cand, top, mapped, outdir)
    t_eq = time.time() - t2

    ratio = dut["crit"] / ref["crit"]
    delay_ok = ratio <= RATIO_BAR
    verdict = "PASS" if (delay_ok and eq_ok) else "FAIL"
    out = {
        "candidate": cand,
        "verdict": verdict,
        "delay_u": dut["crit"],
        "cells": dut["cells"],
        "area": dut["area"],
        "delay_ratio_vs_mult": round(ratio, 4),
        "ratio_bar": RATIO_BAR,
        "ref": {"cells": ref["cells"], "crit": ref["crit"], "cached": cached},
        "equiv_check": {"ok": eq_ok, "detail": eq_msg, "nvecs": EQUIV_VECS},
        "flow": "yosys 0.69+ abc -genlib mini.genlib, explicit no-dretime script (see README)",
        "time_ref_s": round(t_ref, 1),
        "time_dut_s": round(t_dut, 1),
        "time_equiv_s": round(t_eq, 1),
    }
    json.dump(out, open(os.path.join(outdir, "s0_result.json"), "w"), indent=1)
    print(f"[S0 {cand}] delay={dut['crit']:.1f}u cells={dut['cells']} "
          f"x_mult={ratio:.3f} (bar {RATIO_BAR}) equiv={eq_msg} -> {verdict} "
          f"[ref {t_ref:.0f}s cached={cached}, dut {t_dut:.0f}s, equiv {t_eq:.0f}s]")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
