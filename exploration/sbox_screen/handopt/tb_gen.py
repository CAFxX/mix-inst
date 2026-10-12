#!/usr/bin/env python3
"""Generate an iverilog testbench checking an emitted box vs harvest table.

Usage: python3 tb_gen.py <box.v> <boxname> <out_tb.v>
The testbench instantiates module <boxname.lower()> and checks all 256
inputs against the table hardcoded from the harvest JSON.
"""
import json
import os
import sys

box_v, name, out = sys.argv[1], sys.argv[2], sys.argv[3]
harvest = os.path.expanduser(
    "~/workspace/mix/exploration/sbox_screen/ranked_sbox8_pool_20261012.json")
table = None
for rec in json.load(open(harvest))["records"]:
    if rec["name"] == name:
        table = bytes.fromhex(rec["table"])
assert table and len(table) == 256

L = []
L.append("`timescale 1ns/1ps")
L.append(f"module tb;")
L.append(f"  reg [7:0] x; wire [7:0] y;")
L.append(f"  {name.lower()} dut(.x(x), .y(y));")
L.append(f"  reg [7:0] tab [0:255]; integer i, fails;")
L.append(f"  initial begin")
for i, v in enumerate(table):
    L.append(f"    tab[{i}] = 8'h{v:02x};")
L.append(f"    fails = 0;")
L.append(f"    for (i = 0; i < 256; i = i + 1) begin")
L.append(f"      x = i; #1;")
L.append(f"      if (y !== tab[i]) begin fails = fails + 1; "
         f"$display(\"MISMATCH x=%02h got=%02h want=%02h\", x, y, tab[i]); end")
L.append(f"    end")
L.append(f"    if (fails == 0) $display(\"TB-PASS 256/256\");")
L.append(f"    else $display(\"TB-FAIL %0d/256\", fails);")
L.append(f"    $finish;")
L.append(f"  end")
L.append(f"endmodule")
open(out, "w").write("\n".join(L) + "\n")
print(f"wrote {out}")
