# P&R Gap Closure Status — 2026-10-01

## Gap 1: GRT-0701 (global routing) — FIXED

**Root cause**: Sky130 `sky130_fd_sc_hd__nom.tlef` ships with no TRACKS section.
The prior `make_tracks` workaround covered met1–met5 but missed `li1`, which is
also `TYPE ROUTING` in this PDK → `[ERROR GRT-0701] Missing track structure`.

**Fix** (`pnr/flow.tcl`): after `initialize_floorplan`, create tracks for ALL
routing layers including li1, with pitches/offsets from the tech LEF LAYER
statements:
- li1:  x 0.23/0.46, y 0.17/0.34
- met1: x 0.17/0.34, y 0.17/0.34
- met2: x 0.23/0.46, y 0.23/0.46
- met3: x 0.34/0.68, y 0.34/0.68
- met4: x 0.46/0.92, y 0.46/0.92
- met5: x 1.70/3.40, y 1.70/3.40

Verified: global route completes with **zero overflow** (8.77% usage).

**Additional discovery**: TritonRoute generates systematic DRC violations when
signals are routed on `li1` (the intra-cell local-interconnect layer). The fix
(per ORFS sky130hd and kishlabs/sky130-tapeout): 
`set_routing_layers -signal met1-met5 -clock met1-met5` before `global_route`.
With li1: 980→1830→3217 violations (diverging). Without li1: 445→916 (lower,
still needs optimization iterations to converge).

**Also**: `detailed_route -droute_end_iter 20` (more optimization iterations;
violations decrease 3460→2460 across iterations, need ~20 to converge).

## Gap 2: Multiplier reference — P&R RUNNING

`pnr/mul64_64.v`: 64×64→64 truncated multiplier (fairer vs mixer, less ABC work).
Yosys+ABC: ~5s, 9639 cells. P&R at DIE=355 (62% util) running in `wd_mul/`.

## Results

### Adder (ripple, 64-bit) — CLEAN, COMPLETE
- DRC: **0 violations** (converged 5→0)
- Critical path: **9.59 ns**
- Area: 305 instances, **2124.5 µm²**
- Power: **0.37 µW** total (default activity)

### Kogge-Stone adder — functional, P&R interrupted
- 2000-vector iverilog sim: PASS
- P&R killed (machine overload); needs rerun

### Mixer (r3_xorlin_qm) — P&R RUNNING with fixes
- `wd_mixer_final/`: no-li1 + 20 DRT iterations, in 0th optimization iter
- Expected: convergence to 0 violations (trend supports this)

### Multiplier — P&R RUNNING
- `wd_mul/`: in 0th optimization iteration

## Files
- `pnr/flow.tcl`: updated with li1 tracks, no-li1 routing, 20 DRT iters
- `pnr/flow_final.tcl`: mixer-specific (with `-output_drc`)
- `pnr/post.tcl`, `pnr/summarize.py`: post-route analysis
- `pnr/README.md`: full documentation

## Remaining
1. mixer_final and mul to finish DRT (~30-60 min on 2-CPU box)
2. Run `post.tcl` on final DEFs for timing/area/power
3. Rerun KS adder P&R
4. Standalone DRC (Magic/KLayout) not available — document as gap
