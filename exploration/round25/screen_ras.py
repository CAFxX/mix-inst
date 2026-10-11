#!/usr/bin/env python3
"""R25 Track B (Rasoolzadeh pool): standalone synthesis + tracer depth ranking.

Samples are in sbox_screen_ras/sampled.json (12 S-boxes, 6 per affine class).
For each: emit standalone Verilog with gen_r25's QM-DNF, synthesize via
run_synth.py, run critpath tracer, rank by mapped logic levels.
Writes sbox_screen_ras/keep_ras.txt with the 3 shallowest.
"""
import json
import os
import subprocess
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R25 = os.path.join(EXP, "round25")
SCR = os.path.join(R25, "sbox_screen_ras")
GENLIB = "/home/hatch/workspace/mix/synth/mini.genlib"

sys.path.insert(0, R25)
sys.path.insert(0, os.path.join(R25, "models"))
import gen_r25  # noqa: E402


def du_of(sbox):
    mx = 0
    for da in range(1, 16):
        cnt = {}
        for x in range(16):
            db = sbox[x] ^ sbox[x ^ da]
            cnt[db] = cnt.get(db, 0) + 1
        mx = max(mx, max(cnt.values()))
    return mx


def emit_standalone(name, sb):
    lines = [f"module sbox_{name}(input [63:0] x, output [63:0] y);",
             "reg [63:0] y;", "always @(*) begin"]
    lines += ["    " + l.strip() for l in gen_r25._v_sbox16_stmts(sb, "x", "y")]
    lines += ["end", "endmodule"]
    vp = os.path.join(SCR, f"sbox_{name}.v")
    with open(vp, "w") as f:
        f.write("\n".join(lines) + "\n")
    return vp


def synth_and_trace(name, sb):
    vp = emit_standalone(name, sb)
    wd = os.path.join(SCR, f"synth_{name}")
    os.makedirs(wd, exist_ok=True)
    r = subprocess.run(
        [sys.executable, os.path.join(EXP, "run_synth.py"), vp, f"sbox_{name}", wd],
        capture_output=True, text=True, timeout=600)
    mapped = os.path.join(wd, "_dut", f"mapped_sbox_{name}.v")
    if not os.path.exists(mapped):
        return None, f"no mapped netlist: {r.stdout[-300:]}"
    out_json = os.path.join(wd, "critpath.json")
    r2 = subprocess.run(
        [sys.executable, os.path.join(EXP, "critpath", "critpath.py"),
         mapped, GENLIB, "--name", f"sbox_{name}", "--json", out_json],
        capture_output=True, text=True, timeout=300)
    if r2.returncode != 0:
        return None, f"tracer rc={r2.returncode}"
    d = json.load(open(out_json))
    top = d["topk"][0]
    return {"depth": top["levels"], "nonlin": top["nonlin_levels"],
            "cells": d["cells"], "crit": d["crit"]}, None


def main():
    sampled = json.load(open(os.path.join(SCR, "sampled.json")))
    rows = []
    for name, fn, ix, sb in sampled:
        du = du_of(sb)
        assert du == 4, (name, f"DU={du}, expected 4")
        res, err = synth_and_trace(name, sb)
        if err:
            print(f"{name} ({fn}:{ix}): ERROR {err}")
        else:
            print(f"{name} ({fn}:{ix}): depth={res['depth']} "
                  f"(nonlin {res['nonlin']}), cells={res['cells']}, DU=4")
            rows.append((name, fn, ix, sb, res))
    rows.sort(key=lambda r: r[4]["depth"])
    print("\nRanked:")
    for name, fn, ix, sb, res in rows:
        print(f"  {res['depth']} levels  {name} ({fn}:{ix})")
    keep = [(n, f, ix, sb) for n, f, ix, sb, _ in rows[:3]]
    json.dump(keep, open(os.path.join(SCR, "keep_ras.json"), "w"))
    with open(os.path.join(SCR, "keep_ras.txt"), "w") as f:
        f.write("\n".join(n for n, _, _, _ in keep) + "\n")
    print(f"\nkeep: {[n for n, _, _, _ in keep]}")
    # save full table for the round log
    with open(os.path.join(SCR, "depth_table.json"), "w") as f:
        json.dump([{"name": n, "file": fn, "line": ix, "sbox": sb,
                    **res} for n, fn, ix, sb, res in rows], f, indent=1)


if __name__ == "__main__":
    main()
