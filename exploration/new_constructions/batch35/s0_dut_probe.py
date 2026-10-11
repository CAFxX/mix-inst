#!/usr/bin/env python3
"""Batch-35 DUT-only S0 probe (track 6).

Uses run_synth.synth_one (identical Yosys flow, pinned toolchain, genlib,
analyze.py+analyze2.py cross-check) but SKIPS the mul64 reference synth:
the reference deadlocks box-wide in the yosys->abc pipe (yosys stuck in
anon_pipe_read, 0 CPU; abc in poll_schedule; LOUD infra issue, needs
toolchain owner -- see batch34/RESUME.md). Small DUTs do not wedge
(track-3 2-gate smoke PASS 02:22 CEST, ~8s).

Reports absolute critical-path delay ("u" units) -- the reference only
provides a ratio, unneeded for the cost gate (frontier 19.8u absolute).

Usage: s0_dut_probe.py <verilog> <top> <workdir>
"""
import os
import sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from run_synth import synth_one

src, top, workdir = sys.argv[1], sys.argv[2], sys.argv[3]
r = synth_one(src, top, os.path.join(workdir, "_dut"))
print(f"RESULT name={top} cells={r['cells']} area={r['area']:.0f} "
      f"crit={r['crit']:.1f}")
print("XCHECK: analyze.py == analyze2.py (cells/area/crit identical)")
