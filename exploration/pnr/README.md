# Sky130 P&R — r3_xorlin_qm physical-design gap closure

Date: 2026-10-01. Tool versions: Yosys 0.69 (conda-forge), OpenROAD v2.0-17598-ga008522d8,
OpenSTA 2.6.0. PDK: Sky130A via Volare, revision
c6d73a35f524070e85faff4a6a9eef49553ebc2b (sky130_fd_sc_hd).
Corner: TT 100C 1.8V (`sky130_fd_sc_hd__tt_100C_1v80.lib`).

## Gap 1 — routing (GRT-0701) root cause and fix

`global_route` failed with `[ERROR GRT-0701] Missing track structure for routing
layers` because the Sky130 tech LEF (`sky130_fd_sc_hd__nom.tlef`) ships with no
TRACKS section, and the `make_tracks` workaround only created tracks for
met1–met5 — but **li1 is also a TYPE ROUTING layer** in this PDK and had no
tracks. Adding

```
make_tracks li1 -x_offset 0.23 -x_pitch 0.46 -y_offset 0.17 -y_pitch 0.34
```

(after `initialize_floorplan`, before `global_route`) clears GRT-0701.
Pitches/offsets are taken from the tech LEF LAYER statements.

## Flows

- `flow.tcl` — combinational designs (virtual 10000ns clock, 0 IO delays).
  Reports post-route input→output critical path, area, power, DRC.
- `flow_seq.tcl` — sequential designs (real clock on `clk`, default period 10ns).
- `mul64_64.v` — 64×64→64 truncated multiplier reference (matches mixer output width).
- `add64.v` — 64-bit adder reference.
- Synth netlists: `synth_mul64_64.v` (9639 cells), `synth_add64.v`, `synth_pipe2.v`.
  Mixer netlist reused from `../results/r3/pnr_qm/synth.v` (6883 cells).
- `summarize.py` — parses wd_*/timing.rpt, power.rpt, drc.rpt, flow.log.

## Work dirs

- `wd_mixer` — r3_xorlin_qm, DIE 300 (core 270×270)
- `wd_mul` — mul64_64, DIE 355 (utilization-matched to mixer; DIE 300 over-dense, GPL-0302)
- `wd_add` — add64, DIE 200
- `wd_pipe2` — mix_pipe2_base, DIE 300, CLK_PERIOD 10ns

## Results

(see parent-agent report for the final table)
