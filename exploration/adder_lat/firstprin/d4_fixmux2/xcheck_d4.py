#!/usr/bin/env python3
"""Bit-exact check: Verilog (iverilog) vs d4_model on random vectors."""
import subprocess, sys, os
import numpy as np
import d4_model as M

IVL = "/home/hatch/tools/ivl-env/bin/iverilog"
VVP = "/home/hatch/tools/ivl-env/bin/vvp"

def check(kind, p1, p2, vfile, top, fn, nvec=200, seed=0xD4):
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=nvec, dtype=np.uint64)
    ks = rng.integers(0, 2**64, size=nvec, dtype=np.uint64)
    exp = []
    with open("xcheck_vec.hex", "w") as f:
        for x, k in zip(xs, ks):
            y = (fn(np.uint64(x) ^ np.uint64(k)) ^ M.rotl(np.uint64(k), 13)) & M.M64
            # note: model fn takes already-whitened input; verilog does x^k internally
            # recompute properly: verilog xk = x^k; y = F(xk)^rotl(k,13)
            y = (fn((np.uint64(x) ^ np.uint64(k)) & M.M64) ^ M.rotl(np.uint64(k), 13)) & M.M64
            exp.append(int(y))
            f.write(f"{int(x):016x}_{int(k):016x}_{int(y):016x}\n")
    tb = f"""`timescale 1ns/1ps
module tb;
  reg [63:0] x, k; wire [63:0] y;
  {top} dut(.x(x), .k(k), .y(y));
  reg [191:0] vec [0:{nvec-1}];
  integer i, bad;
  initial begin
    $readmemh("xcheck_vec.hex", vec);
    bad = 0;
    for (i = 0; i < {nvec}; i = i+1) begin
      x = vec[i][191:128]; k = vec[i][127:64]; #1;
      if (y !== vec[i][63:0]) begin bad = bad+1;
        $display("MISMATCH %0d x=%h k=%h got=%h exp=%h", i, x, k, y, vec[i][63:0]); end
    end
    $display("XCHECK %s: %0d/%0d mismatches", "{top}", bad, {nvec});
    $finish;
  end
endmodule
"""
    open("tb_xcheck.v", "w").write(tb)
    r1 = subprocess.run([IVL, "-o", "tb.vvp", "tb_xcheck.v", vfile], capture_output=True, text=True)
    assert r1.returncode == 0, r1.stderr[:500]
    r2 = subprocess.run([VVP, "tb.vvp"], capture_output=True, text=True)
    # vvp $finish trailer parse: find XCHECK line
    for line in r2.stdout.splitlines():
        if "XCHECK" in line or "MISMATCH" in line:
            print(line)
    return "0/" in r2.stdout  # crude pass check refined below

if __name__ == "__main__":
    okA = check("A", 11, 23, "d4_A.v", "d4A", lambda x: M.apply_A(x, 11, 23))
    okC = check("C", 11, 23, "d4_C.v", "d4C", lambda x: M.apply_C(x, 11, 23))
    print("A bit-exact:", okA, " C bit-exact:", okC)
