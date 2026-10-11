#!/usr/bin/env python3
"""R25 Track B (refined per parent directive 2026-10-05): least-depth ranking
in the GJN17 sense, adapted to our flow.

For each standalone-synthesized S-box candidate, run the critpath tracer
(exploration/critpath/critpath.py) on the ABC-mapped netlist and rank by the
tracer's reported critical-path depth (mapped logic levels of the top path).

Literature basis: Banik et al. 2015 (depth as S-box path-delay metric, MIDORI
Sb0/Sb1); GJN17 (tool computing least-depth logical expression per 4-bit
S-box); Sto16 (SAT with depth as optimization criterion). Our S1 is already
cryptographically optimal (DU=4, NL=4); 4 AND + 4 XOR is the proven gate-count
floor (Ullrich et al.) -- headroom is depth/shape only.

CAVERT (recorded in ROUND25_TABLE.md): literature depth counts logical-
operation levels; ours counts mapped Sky130 cell levels -- strongly correlated
(both AND-level dominated) but not identical. The standalone depth is only the
pre-filter; final ranking comes from S0 in the pba19b01 construction.

Usage: python3 rank_sbox_depth.py [--write-keep]
  Without --write-keep: prints ranking table only.
  With --write-keep: writes sbox_screen/keep.txt with the 3 shallowest.
"""
import json
import os
import subprocess
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R25 = os.path.join(EXP, "round25")
SCR = os.path.join(R25, "sbox_screen")
GENLIB = "/home/hatch/workspace/mix/synth/mini.genlib"  # same as run_synth.py


def tracer_depth(workdir, name):
    """Run critpath tracer on the standalone mapped netlist; return top-path levels."""
    mapped = os.path.join(workdir, "_dut", f"mapped_sbox_{name}.v")
    if not os.path.exists(mapped):
        return None, "no mapped netlist"
    out_json = os.path.join(workdir, "critpath.json")
    r = subprocess.run(
        [sys.executable, os.path.join(EXP, "critpath", "critpath.py"),
         mapped, GENLIB, "--name", f"sbox_{name}", "--json", out_json],
        capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        return None, f"tracer rc={r.returncode}: {r.stderr[:200]}"
    d = json.load(open(out_json))
    top = d["topk"][0]
    return top["levels"], None


def main():
    write_keep = "--write-keep" in sys.argv
    # discover candidates from the .v files
    cands = sorted(
        f[5:-2] for f in os.listdir(SCR)
        if f.startswith("sbox_") and f.endswith(".v"))
    rows = []
    for name in cands:
        wd = os.path.join(SCR, f"synth_{name}")
        depth, err = tracer_depth(wd, name)
        rows.append((name, depth, err))
        print(f"{name}: mapped depth = {depth if depth is not None else 'ERR ' + str(err)}")

    done = [(n, d) for n, d, e in rows if d is not None]
    pending = [n for n, d, e in rows if d is None]
    if pending:
        print(f"\npending: {pending} -- re-run when synthesis finishes")
    # rank non-baseline by depth
    ranked = sorted((d, n) for n, d in done if n != "S1_baseline")
    base = next((d for n, d in done if n == "S1_baseline"), None)
    print(f"\nS1 baseline mapped depth: {base}")
    print("Ranked (non-baseline, shallowest first):")
    for d, n in ranked:
        print(f"  {d} levels  {n}")
    if write_keep:
        if pending:
            print("REFUSING to write keep.txt with pending candidates")
            sys.exit(1)
        keep = [n for _, n in ranked[:3]]
        with open(os.path.join(SCR, "keep.txt"), "w") as f:
            f.write("\n".join(keep) + "\n")
        print(f"keep.txt: {keep}")


if __name__ == "__main__":
    main()
