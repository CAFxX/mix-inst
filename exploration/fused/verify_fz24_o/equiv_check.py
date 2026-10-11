#!/usr/bin/env python3
"""Mapped-netlist equivalence check for fz24_o (independent replication of
s0_delay.py::equiv_check_generic, oracle = independent ref_fz24_o spec model).

Simulates the PINNED run_synth mapped netlist (mapped_fz24_o.v) via iverilog
+ cells_sim.v behavioral models on 1000 random vectors, compares vs ref model.
"""
import os, random, re, subprocess, sys

V = "/home/hatch/workspace/mix/exploration/fused/verify_fz24_o"
FB = "/home/hatch/workspace/mix/exploration/fast_battery"
sys.path.insert(0, V)
from ref_fz24_o import ref_mix

OUT = os.path.join(V, "s0")
MAPPED = os.path.join(OUT, "_dut", "mapped_fz24_o.v")
CELLS = os.path.join(FB, "src", "cells_sim.v")
TOP, PIN1, PIN2, POUT = "fz24_o", "val", "key", "out"
NVEC, SEED = 1000, 0xE9CE

rng = random.Random(SEED)
vecs = [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(NVEC)]
vf = os.path.join(OUT, "_equiv_vecs_dut.txt")
with open(vf, "w") as f:
    for x, y in vecs:
        f.write("%016x %016x %016x\n" % (x, y, ref_mix(x, y)))
tb = os.path.join(OUT, "_equiv_tb_dut.v")
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
""" % (TOP, PIN1, PIN2, POUT, vf))
sim = os.path.join(OUT, "_equiv_sim_dut")
env = dict(os.environ)
env["PATH"] = os.path.expanduser("~/tools/ivl-env/bin") + ":" + env["PATH"]
r = subprocess.run(["iverilog", "-o", sim, MAPPED, CELLS, tb],
                   capture_output=True, text=True, timeout=300, env=env)
if r.returncode != 0:
    print("IVERILOG COMPILE FAILED:\n", r.stderr[-1500:])
    sys.exit(1)
r = subprocess.run(["vvp", sim], capture_output=True, text=True, timeout=600, env=env)
m = re.search(r"EQUIV n=(\d+) err=(\d+)", r.stdout)
if not m:
    print("NO EQUIV LINE:\n", r.stdout[-1500:], "\n", r.stderr[-500:])
    sys.exit(1)
ok = int(m.group(2)) == 0 and int(m.group(1)) == NVEC
print(f"EQUIV n={m.group(1)} err={m.group(2)} -> {'PASS' if ok else 'FAIL'} "
      f"(pinned mapped netlist vs independent spec model)")
sys.exit(0 if ok else 2)
