# Sky130 P&R — round-4 finalist `h_xorspn3` (r4_h_xorspn3) vs mul64_64 vs add64

Date: 2026-10-01. Work dir: [`~/workspace/mix/exploration/round4/pnr/`](./)
(separate from [`../pnr/`](../../pnr/) — another agent is active there).

## Tool / PDK / corner / constraints

- OpenROAD v2.0-17598-ga008522d8, OpenSTA 2.6.0, Yosys 0.69 (conda-forge)
- PDK sky130A rev c6d73a35f524070e85faff4a6a9eef49553ebc2b (Volare), `sky130_fd_sc_hd`
- Corner: TT / 100C / 1.8V (`sky130_fd_sc_hd__tt_100C_1v80.lib`)
- Constraints: virtual clock 10000ns, `set_input_delay 0` / `set_output_delay 0` on all IO
  (all three designs combinational). No SAIF/VCD — `report_power` uses default activity.
- Die sizes tuned from liberty cell areas for ~25% utilization (measured below).

## Flows

- [`flow.tcl`](flow.tcl) — copy of the fixed [`../pnr/flow.tcl`](../../pnr/flow.tcl) (incl. `make_tracks li1` GRT-0701 fix),
  full detailed route. NOTE: `report_area` and `report_drc` do not exist in this
  OpenROAD build — both fail with `invalid command name` (round-3 hit the same;
  see [`../pnr/wd_add/flow.log`](../../pnr/wd_add/flow.log)). Area/power recovered via [`post.tcl`](post.tcl) on `final.def`;
  DRC violation count taken from TritonRoute's final `DRT-0199` line.
- [`flow_gr2.tcl`](flow_gr2.tcl) — identical placement, stops at `global_route`, then
  `estimate_parasitics -global_routing` + `report_checks`/`report_power`.
  (This OpenSTA has no `-detailed_routing` parasitic mode; without extraction STA
  falls back to wireload models — confirmed by `RSZ-0021` warning.)
- [`post.tcl`](post.tcl) — copy of [`../pnr/post.tcl`](../../pnr/post.tcl): area from DB masters, timing, power.

## Synthesis (Yosys flow per task)

[`synth_h_xorspn3.v`](synth_h_xorspn3.v): 1305 mapped cells, module `r4_h_xorspn3`.
Reference netlists reused read-only: `../pnr/synth_mul64_64.v` (9639 cells),
`../pnr/synth_add64.v` (305 cells).

Netlist fix (mixer only): yosys `write_verilog -noattr -noexpr -nodec` emits
`assign <dead-wire> = <hex>x...;` for function temporaries (264 of them, none
connected to any cell). OpenROAD turns these into a GROUND-typed `zero_` net and
`detailed_route` aborts with `DRT-0305`. Stripped the dead assigns + wire decls
(456 lines); the 4 real shuffle assigns (`rk*` concatenations) kept.
The mul/add netlists have zero assigns and never hit this.

## Results

### Detailed route ([flow.tcl](flow.tcl))

| design | DIE | core (µm²) | inst | stdcell area (µm²) | util | crit path (wireload) | power | DRC |
|---|---|---|---|---|---|---|---|---|
| r4_h_xorspn3 ([`wd_mixer`](wd_mixer/)) | 260 | 52445 | 1305 | 13081.3 | 24.94% | 4.0015 ns, key[44]→out[28] | 55.9 µW | **0 violations** |
| add64 ([`wd_add`](wd_add/)) | 125 | 9025 | 305 | 2124.5 | 24.24% | 9.5912 ns, a[1]→y[63] | 0.368 µW | **0 violations** |
| mul64_64 | 545 | 265225 | 9639 | ~66510 (est) | 25.08% (GR run) | — not completed — | — | — |

### Global-route + parasitic STA ([flow_gr2.tcl](flow_gr2.tcl), identical conditions)

| design | crit path (parasitics) | endpoints | power |
|---|---|---|---|
| r4_h_xorspn3 ([`wd_mixer_gr`](wd_mixer_gr/)) | **4.9534 ns** | key[19]→out[9] | 69.2 µW |
| mul64_64 ([`wd_mul_gr`](wd_mul_gr/)) | **12.5632 ns** | b[23]→y[63] | 157 µW |
| add64 ([`wd_add_gr`](wd_add_gr/)) | **10.7517 ns** | a[1]→y[63] | 0.405 µW |

Validation: mul 12.5632ns reproduces round-3's published 12.56ns (same netlist,
same corner, GR+parasitics) to 4 significant figures — methodology confirmed.

## Mixer-vs-multiplier ratio

4.9534 / 12.5632 = **0.394 → 0.39x** (parasitic-annotated, matched ~25% util).
Beats round-3's r3_xorlin_qm A/B of 0.47x (5.91/12.56): h_xorspn3 is 16% faster
post-route than r3_xorlin_qm (4.95ns vs 5.91ns), consistent with the 34.5u vs
40.0u unit-delay screening numbers.

## What remains open

1. **mul64_64 detailed route + DRC not completed.** The box (2 cores, load 6–12 from
   other agents, rebooted 3× during this task) could not finish the 9639-cell
   detailed route: 30 min to reach 10% of the first DRT iteration at ~25% CPU
   share. Killed and replaced with the GR+parasitics flow, which is the same
   methodology as round-3's published A/B and reproduces its mul number exactly.
2. **Pipelined variants appeared after this task started** and were not run:
   [`../rtl/mix_h_xorspn3_pipe.v`](../rtl/mix_h_xorspn3_pipe.v) (module `mix_h_xorspn3_pipe`),
   [`../rtl/mix_h_xorspn3_pipe_adv.v`](../rtl/mix_h_xorspn3_pipe_adv.v), [`../rtl/mix_h_xorspn3_pipe_tb.v`](../rtl/mix_h_xorspn3_pipe_tb.v).
   Sequential — would need [`flow_seq.tcl`](../../pnr/flow_seq.tcl) + a real clock constraint.
3. **STA is wireload-based after detailed route** (this OpenSTA lacks
   `estimate_parasitics -detailed_routing`); the parasitic-annotated numbers come
   from global-route extraction. True extracted-parasitic post-DRT STA needs a
   newer OpenSTA or an external extractor.
4. `report_area`/`report_drc` missing from this OpenROAD build — worked around via
   [`post.tcl`](post.tcl) (DB-master area) and DRT logs; a real sign-off DRC (Magic/KLayout)
   was not run.
5. Power is default-activity only (no SAIF/VCD); treat as relative, not absolute.
