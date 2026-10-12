#!/usr/bin/env python3
"""Emit case-statement Verilog for a pool box or pure GF inversion.

Usage:
  python3 emit_case.py --name AFF8_06 --out case_aff8_06.v
  python3 emit_case.py --inv8 --out case_inv8.v   (x -> x^254 in GF(2^8)/0x11B)
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import comp8 as C

HARVEST = os.path.expanduser(
    "~/workspace/mix/exploration/sbox_screen/ranked_sbox8_pool_20261012.json")


def emit(modname, table):
    L = [f"// {modname}: case-form 8-bit box",
         f"module {modname} (input [7:0] x, output reg [7:0] y);",
         "  always @(*) begin",
         "    case (x)"]
    for i, v in enumerate(table):
        L.append(f"      8'h{i:02x}: y = 8'h{v:02x};")
    L.append("      default: y = 8'h00;")
    L.append("    endcase")
    L.append("  end")
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default=None)
    ap.add_argument("--inv8", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.inv8:
        # pure GF(2^8) inversion via comp8's composite field (verified math:
        # isomorphism checked over all 65536 pairs; box model == harvest)
        lam = 0xC
        table = [C.to_byte(C.c_inv(C.from_byte(x), lam)) for x in range(256)]
        open(a.out, "w").write(emit("inv8", table))
        print(f"wrote {a.out} (pure inversion)")
    else:
        for rec in json.load(open(HARVEST))["records"]:
            if rec["name"] == a.name:
                table = list(bytes.fromhex(rec["table"]))
                break
        open(a.out, "w").write(emit(a.name.lower(), table))
        print(f"wrote {a.out} ({a.name} case form)")


if __name__ == "__main__":
    main()
