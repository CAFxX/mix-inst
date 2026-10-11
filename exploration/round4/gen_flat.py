"""Emit flat (parameter-free, single-module) Verilog per round-4 candidate.

Rationale: analyze2.py cannot parse yosys's escaped hierarchical net names
(`\\u.val`) produced when a wrapper instantiates a parameterized submodule.
Flat files avoid hierarchy entirely, so the mapped netlist has plain names.

Each entry: (src_file, base_module, top_name, {param: value}).
The base module's header line is replaced and parameter identifiers are
substituted textually (word-boundary) in the body.
"""
import os
import re

R4 = "/home/hatch/workspace/mix/exploration/round4"
RTL = os.path.join(R4, "rtl")
FLAT = os.path.join(RTL, "flat")
os.makedirs(FLAT, exist_ok=True)

CANDS = [
    ("r4_xsfeistel.v", "r4_xsfeistel", "r4_simeck_f10", {"FTYPE": "0", "ROUNDS": "10"}),
    ("r4_xsfeistel.v", "r4_xsfeistel", "r4_simon_f10", {"FTYPE": "1", "ROUNDS": "10"}),
    ("r4_xsfeistel.v", "r4_xsfeistel", "r4_simeck_f12", {"FTYPE": "0", "ROUNDS": "12"}),
    ("r4_xsfeistel.v", "r4_xsfeistel", "r4_dbland_f8", {"FTYPE": "2", "ROUNDS": "8"}),
    ("r4_xsm.v", "r4_xsm", "r4_xsm_c3",
     {"C": "64'h100000000000003F", "S1": "33", "S2": "27", "SL": "17", "S3": "29"}),
    ("r4_xsm.v", "r4_xsm", "r4_xsm_c8",
     {"C": "64'h8080808080808001", "S1": "31", "S2": "28", "SL": "23", "S3": "30"}),
    ("r4_fmix32.v", "r4_fmix32h", "r4_fmix32h_a", {"CROSS": "0"}),
    ("r4_fmix32.v", "r4_fmix32h", "r4_fmix32h_b", {"CROSS": "1"}),
    ("r4_glfeistel.v", "r4_glfeistel", "r4_gl5_f6", {"ROUNDS": "6"}),
    ("r4_glfeistel.v", "r4_glfeistel", "r4_gl5_f8", {"ROUNDS": "8"}),
    ("r4_blink.v", "r4_blink", "r4_blink2", {"SB": "0", "ROUNDS": "2"}),
    ("r4_blink.v", "r4_blink", "r4_blink3", {"SB": "0", "ROUNDS": "3"}),
    ("r4_blink.v", "r4_blink", "r4_blink4", {"SB": "0", "ROUNDS": "4"}),
    ("r4_blink.v", "r4_blink", "r4_midori3", {"SB": "1", "ROUNDS": "3"}),
    ("r4_speedy.v", "r4_speedy", "r4_speedy3", {"ROUNDS": "3"}),
    ("r4_speedy.v", "r4_speedy", "r4_speedy4", {"ROUNDS": "4"}),
]


def extract_module(src, modname):
    """Return the full text of `module modname ... endmodule`."""
    lines = src.splitlines(keepends=True)
    start = end = None
    for i, ln in enumerate(lines):
        if re.match(rf"\s*module\s+{modname}\b", ln):
            start = i
        elif start is not None and re.match(r"\s*endmodule\b", ln):
            end = i
            break
    assert start is not None and end is not None, f"module {modname} not found"
    return "".join(lines[start:end + 1])


def main():
    for src_file, base, top, params in CANDS:
        src = open(os.path.join(RTL, src_file)).read()
        body = extract_module(src, base)
        # replace header line: `module base #(...)` -> `module top`
        body = re.sub(rf"module\s+{base}\s*#\([^)]*\)",
                      f"module {top}", body, count=1)
        # substitute parameter identifiers (word boundary) in the body
        for p, v in params.items():
            body = re.sub(rf"\b{p}\b", v, body)
        out = os.path.join(FLAT, f"{top}.v")
        with open(out, "w") as f:
            f.write(f"// Flat single-module build of {top} (from {src_file});\n")
            f.write(f"// parameters: {params}\n")
            f.write(body)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
