"""Testbench for the 2-stage pipeline: functional correctness, 1/cycle
throughput, and valid tracking. Expected values from the numpy model."""
import os, subprocess, sys
import numpy as np

EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP + "/models")
from spn4_xorlin_1137 import mix_spn4_xorlin_1137_np

def gen_tb(pipe_top, n_main=64):
    rng = np.random.default_rng(1234)
    vals = rng.integers(0, 2**64, size=n_main, dtype=np.uint64)
    keys = rng.integers(0, 2**64, size=n_main, dtype=np.uint64)
    exps = [int(mix_spn4_xorlin_1137_np(int(v), int(k))) for v, k in zip(vals, keys)]
    L = [f"// tb for {pipe_top}: {n_main} back-to-back inputs, then bubbles",
         "`timescale 1ps/1ps",
         f"module tb_{pipe_top};",
         "  reg clk = 0;",
         "  reg [63:0] val; reg [63:0] key; reg valid_in;",
         f"  wire [63:0] out; wire valid_out;",
         f"  {pipe_top} dut(.clk(clk), .val(val), .key(key), .valid_in(valid_in), .out(out), .valid_out(valid_out));",
         "  always #5 clk = ~clk;",
         "  integer i; integer errs;",
         f"  reg [63:0] TVAL [0:{n_main-1}];",
         f"  reg [63:0] TKEY [0:{n_main-1}];",
         f"  reg [63:0] TEXP [0:{n_main-1}];",
         "  initial begin"]
    for i in range(n_main):
        L.append(f"    TVAL[{i}] = 64'h{int(vals[i]):016x}; TKEY[{i}] = 64'h{int(keys[i]):016x}; TEXP[{i}] = 64'h{exps[i]:016x};")
    L += [f"""
    errs = 0;
    valid_in = 0; val = 0; key = 0;
    @(posedge clk); @(posedge clk); // settle, valid_q=0
    // phase 1: back-to-back inputs, 1 per cycle.
    // 1-cycle latency: input i presented before posedge i -> out==TEXP[i] after posedge i.
    for (i = 0; i < {n_main}; i = i + 1) begin
      val = TVAL[i]; key = TKEY[i]; valid_in = 1;
      @(posedge clk);
      #1;
      if (!valid_out) begin $display("THROUGHPUT-FAIL: valid_out low at i=%0d", i); errs = errs + 1; end
      if (out !== TEXP[i]) begin $display("MISMATCH i=%0d: got %h exp %h", i, out, TEXP[i]); errs = errs + 1; end
    end
    // drain: valid_in=0 -> valid_out must drop next cycle; out holds last value (don't care)
    valid_in = 0;
    @(posedge clk); #1;
    if (valid_out) begin $display("DRAIN-FAIL: valid_out stuck high"); errs = errs + 1; end
    @(posedge clk); #1;
    if (valid_out) begin $display("DRAIN-FAIL2: valid_out stuck high"); errs = errs + 1; end
    // phase 2: intermittent valid (gap every 3rd) still correct
    @(posedge clk);
    for (i = 0; i < 12; i = i + 1) begin
      val = TVAL[i]; key = TKEY[i]; valid_in = (i % 3 != 2);
      @(posedge clk); #1;
      if (valid_in) begin
        // input i was presented before this posedge; but if previous cycle had a bubble,
        // valid_out corresponds to THIS input (1-cycle latency from presentation)
        if (!valid_out) begin $display("INTERMITTENT-FAIL: valid_out low at i=%0d", i); errs = errs + 1; end
        if (out !== TEXP[i]) begin $display("INTERMITTENT-MISMATCH i=%0d: got %h exp %h", i, out, TEXP[i]); errs = errs + 1; end
      end else begin
        if (valid_out) begin $display("INTERMITTENT-VALID-FAIL at i=%0d", i); errs = errs + 1; end
      end
    end
    valid_in = 0;
    repeat (4) @(posedge clk);
    if (errs == 0) $display("PIPECHECK PASS");
    else $display("PIPECHECK FAIL: %0d errors", errs);
    $finish;
  end
endmodule"""]
    path = EXP + f"/results/r3/tb_{pipe_top}.v"
    open(path, "w").write("\n".join(L))
    return path

def run(pipe_top, rtl_path):
    tb = gen_tb(pipe_top)
    r = subprocess.run(
        ["iverilog", "-o", "/tmp/pipe_tb", rtl_path, tb],
        capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print("IVERILOG FAIL", r.stderr[-2000:]); return False
    r = subprocess.run(["vvp", "/tmp/pipe_tb"], capture_output=True, text=True, timeout=300)
    out = r.stdout + r.stderr
    ok = "PIPECHECK PASS" in out
    print(("PIPE-OK " if ok else "PIPE-FAIL ") + pipe_top)
    if not ok: print(out[-3000:])
    return ok

if __name__ == "__main__":
    top = sys.argv[1] if len(sys.argv) > 1 else "mix_pipe2_base"
    rtl = EXP + f"/rtl/r3/{top}.v"
    sys.exit(0 if run(top, rtl) else 1)
