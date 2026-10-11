# Peer review: `r3_xorlin_qm` Sky130 P&R (placement + STA)

**Reviewer role:** independent physical-design methodology review (not the designer).
**Scope:** `exploration/pnr_sky130.sh` (63 lines), `exploration/results/r3/pnr_qm/pnr.tcl` (31 lines),
`exploration/results/r3/pnr_qm/{synth.v,pnr.def,timing.rpt}`; related probes
`exploration/pnr/{flow.tcl,probe_route.tcl,probe_route2.tcl,probe_route2.log,wd_mixer/flow.log,synth_mul64_64.log}`.
**Method:** read all scripts end to end; independently re-ran the flow in `/tmp` (no workspace writes)
to reproduce the GRT-0701 failure and to test the fix. Did **not** touch `exploration/round4/`.

## Verdict (up front)

1. **The routing-failure diagnosis in the report is wrong.** "Tech LEF lacks TRACKS" is correct
   (verified: 0 occurrences of `TRACKS` in `sky130_fd_sc_hd__nom.tlef`), but GRT-0701 is **not**
   a "version-specific global_route check" or a tool/PDK integration gap. It is a **flow scripting
   omission**: `pnr_sky130.sh` creates tracks for met1–met5 but not for **li1** (a vertical routing
   layer in this tech LEF). The designer's own later script `pnr/flow.tcl:16` already documents
   exactly this: *"li1 included — missing li1 tracks cause GRT-0701 'Missing track structure'"*.
   I reproduced the failure and the fix on the same OpenROAD v2.0 binary: adding the li1
   `make_tracks` line makes `global_route` complete with **0 overflow** (1828 nets, 100305 µm).
   No OpenROAD upgrade, no PDK change, no alternative track generation is needed — one line.
2. **The reported P&R numbers don't match the artifacts.** The placed design is **1700**
   `sky130_fd_sc_hd` instances at **25.5%** utilization (OpenROAD `GPL-0019`), not "6883 cells"
   at "~9% utilization". 6883 is the *screening-flow* (`abc -fast`, mini.genlib) cell count from
   `candidates.md:314`; it was carried over into the P&R section incorrectly.
3. **"0 STA violations" is vacuous.** The virtual clock is `-period 10000` = **10 µs, not 10 ns**
   (units error in the narrative), with zero input/output delays, on a **pre-route** netlist
   using liberty **wireload-model** estimates (`[WARNING RSZ-0021] no estimated parasitics`).
   5.07 ns vs a 10 µs requirement can never violate. The number is a delay *measurement*, not
   timing *closure*.
4. **The P&R gate is not closed, and the headline multiplier comparison was never run.**
   The multiplier netlist exists and synthesizes fine (`pnr/synth_mul64_64.v`, 9639 cells,
   5.15 s — no timeout evidence in any artifact); `pnr/pnr_mul64/` is empty. The requirement
   "latency ≤ multiplier, verified post-route under identical conditions" is unverified.
5. **"Routable in principle" is defensible as engineering judgment but not as a gate result.**
   What exists (legal placement at 25.5% util, 0.099% final overflow, plus the designer's own
   *unreported* clean global route at 0 overflow / 8.8% resource usage) makes detailed-route
   success highly likely — but placement+STA alone proves nothing about DRC, antenna, real RC
   delay, or IR drop, and the project's own hard gate demands "actual post-route verification".

**Fix effort:** small. `pnr/flow.tcl` (full flow incl. detailed route, DRC, post-route STA hooks)
already exists; it is a run-and-wait task (tens of minutes), not a debug task.

---

## Findings

### CRITICAL

**C1. GRT-0701 misdiagnosed as a tool-version issue; root cause is a missing `li1` `make_tracks` line.**
- `pnr_sky130.sh` (tcl lines 20–24 of the generated script) and `results/r3/pnr_qm/pnr.tcl:15-19`
  create tracks for met1–met5 only. `li1` is a `TYPE ROUTING ; DIRECTION VERTICAL` layer in
  `sky130_fd_sc_hd__nom.tlef` (PITCH 0.46 0.34, OFFSET 0.23 0.17) and OpenROAD v2.0's global
  router requires track structures on **all** routing layers; the missing one raises
  `[ERROR GRT-0701] Missing track structure for routing layers.`
- Reproduction (same binary `~/tools/sky130bin/openroad`, v2.0-17598-ga008522d8, same PDK):
  verbatim flow + `global_route` → GRT-0701, exit 1. Same flow + one added line
  `make_tracks li1 -x_offset 0.23 -x_pitch 0.46 -y_offset 0.17 -y_pitch 0.34` (values taken
  from the tech LEF LAYER statement, matching OpenROAD-flow-scripts' sky130hd `make_tracks.tcl`)
  → global route completes: 1828 nets routed, final congestion **0 / 0 / 0 overflow**,
  total wirelength 100305 µm. The designer's own `pnr/probe_route2.tcl` (which includes the
  li1 line) and `pnr/probe_route2.log` show the identical successful result.
- The designer's own `pnr/flow.tcl:14-17` already contains the correct diagnosis
  ("missing li1 tracks cause GRT-0701"). The report text (`candidates.md:330-335`, the
  `pnr.tcl:25-27` comment, and the memory note) still claims a "version-specific global_route
  check" / "tool/PDK integration gap, not a design issue". That claim is **refuted by the
  designer's own later script and by independent reproduction**. No version upgrade or PDK
  change is required.
- Consequence: the headline "routing impossible in this OpenROAD version" conclusion is
  invalid, and the full routing that would close the gate was never attempted with the
  corrected one-line script.

### MAJOR

**M1. Reported cell count and utilization contradict the P&R artifacts.**
- Report: "6883 cells", "~9% utilization" (`pnr_sky130.sh` tcl comment; `candidates.md:335`;
  memory note "6883 cells / 0.410x multiplier area").
- Artifacts: `results/r3/pnr_qm/synth.v` = 1700 `sky130_fd_sc_hd__*` instances;
  `pnr.def` `COMPONENTS 1700`; OpenROAD log `GPL-0006 NumInstances: 1700`,
  `GPL-0018 PlaceInstsArea: 18320.070 um^2`, **`GPL-0019 Util: 25.496 %`**
  (core area 71853.9 µm², 300×300 µm die).
- 6883 is the screening-flow cell count (`abc -fast` → mini.genlib mapping,
  `candidates.md:314` "Synth: 40.0 (0.787× multiplier; 6883 cells; area 18910, 0.410×)").
  Full `abc -liberty` in the P&R flow optimizes the same RTL to 1700 sky130 cells.
  The screening number was carried into the P&R section; "~9%" matches neither 18320/90000
  (20.4%) nor 18320/71853 (25.5%) and appears to come from no artifact at all.
- The design is still small and low-utilization — the qualitative point survives — but every
  quantitative P&R claim in the report section is wrong and must be corrected to
  **1700 instances, 25.5% utilization, 18320 µm² placed cell area**.

**M2. "0 violations @ 10ns" is a vacuous constraint; 5.07 ns is a measurement, not closure.**
- `pnr.tcl:10`: `create_clock -name vclk -period 10000`. OpenROAD/OpenSTA time unit here is
  ns (arrival 5.0703 reads as ns, consistent with the "5.07 ns" claim), so the period is
  **10000 ns = 10 µs, not 10 ns** — a 1000× units error in the narrative (`candidates.md:332`).
- `set_input_delay 0` / `set_output_delay 0` on all IOs: required time = 10000 ns,
  arrival = 5.07 ns, slack = +9994.93 ns (`timing.rpt:55-60`), `tns 0.00 / wns 0.00`
  (`timing.rpt:62`). No path in this design could ever violate this constraint; "0 violations"
  carries zero information about timing health.
- The STA ran **pre-route with no parasitics**: `[WARNING RSZ-0021] no estimated parasitics.
  Using wire load models.` The 5.07 ns uses liberty wireload estimates, not routed RC.
  Post-route delay with real parasitics will differ (typically ±20–30% on such estimates);
  the number cannot be quoted as a post-route result.
- What the STA legitimately establishes: the input→output propagation delay of the placed
  netlist under wireload estimates is 5.07 ns (key[8]→out[39], 17 logic stages). Useful as a
  relative probe number; not a timing signoff.

**M3. Identical-condition multiplier comparison never ran; "ABC timed out" is unevidenced.**
- `pnr/pnr_mul64/` is empty. No multiplier DEF, timing report, or comparison exists.
- The multiplier netlist **exists and synthesizes cleanly**: `pnr/synth_mul64_64.v`
  (9639 cells) from `pnr/synth_mul64_64.log`: `abc -liberty … -constr /dev/null` completed,
  total flow 5.15 s. I found no log, artifact, or error trace of an ABC timeout anywhere in
  the workspace; the claim in the handoff ("ABC optimization timed out on the large
  multiplier design") does not match the on-disk evidence (`candidates.md:336` says only
  "in progress (ABC optimizing large 64×64 design)").
- Status of the hard requirement — *"latency no greater than the multiplier, verified
  post-route under identical conditions"* — is therefore **unverified**, independent of the
  ABC story. The unit-delay screening ratio (0.787×) is not a substitute: it used
  `abc -fast` (no timing-driven mapping), wireload-free unit delays, and a different
  synthesis effort than the P&R flow.

### MINOR

**m1. `report_area` output missing from `timing.rpt`.**
`pnr_sky130.sh` appends `report_area >> $WD/timing.rpt`, but `results/r3/pnr_qm/timing.rpt`
(62 lines) ends at `wns 0.00` with no area section; the script's own
`grep -iE "design area|utilization"` finds nothing. The area/utilization numbers quoted in
the report therefore did not come from this flow's output (consistent with M1). The placed
area/utilization are recoverable from the OpenROAD log (`GPL-0018/0019`) instead.

**m2. `place_pins` omitted in `pnr_sky130.sh` → delivered DEF not routable as-is.**
`pnr.def` has `PINS 192` with no `PLACED` coordinates (pins unplaced; the script comments
"let OpenROAD assign" but OpenROAD does not auto-place pins). Any routing attempt on this
DEF must add `place_pins` first — as the designer's own `probe_route2.tcl` and `flow.tcl`
both do (`place_pins -hor_layers met3 -ver_layers met2`).

**m3. No `estimate_parasitics -placement` before STA.**
Pre-route STA falls back to the liberty wireload model (see M2). One command would have
given placement-based Steiner estimates — still not routed RC, but strictly better than a
wireload model for a delay probe.

**m4. `pnr_sky130.sh` bakes relative paths into the generated `pnr.tcl`.**
The heredoc writes `read_verilog results/r3/pnr_qm/synth.v` etc.; the tcl only runs from
`exploration/`. Fragile but not wrong for a one-shot probe.

### INFO

**i1. Tech-LEF-without-TRACKS diagnosis is correct; `make_tracks` is the sanctioned workaround.**
Verified 0 occurrences of `TRACKS` in `sky130_fd_sc_hd__nom.tlef`. Sky130's tech LEFs
intentionally omit TRACKS; OpenROAD-flow-scripts' sky130hd platform uses exactly this
`make_tracks` sequence (including li1). Nothing PDK-side needs fixing.

**i2. CTS correctly absent — nothing to review there.** The design is fully combinational
(`rtl/r3/r3_xorlin_qm.v:3`: 128 inputs, 64 outputs, no clocks/FFs); `repair_design` ran for
slew/cap buffering only. The "floorplan → placement → CTS → STA" checklist collapses to
floorplan → placement → STA here, which is correct.

**i3. PDK/liberty/LEF references are correct and consistent.**
tt_100C_1v80 liberty, `sky130_fd_sc_hd__nom.tlef`, `sky130_fd_sc_hd.lef`, all from Volare
version `c6d73a35f524070e85faff4a6a9eef49553ebc2b`; Yosys 0.69 from the sky130 micromamba env.
Single-corner (tt) is fine for a *relative* A/B comparison; a signoff would add ss/ff.

**i4. Placement quality itself looks healthy.** Final Nesterov overflow 0.098725 (matches the
reported 0.099), 0 macros, legalized HPWL delta 9%, 25.5% utilization — no placement red flags.

---

## Detailed answers to the review questions

### 1. Flow soundness (`pnr_sky130.sh`, `pnr.tcl`)
Sequence floorplan → make_tracks → global/detailed placement → write_def → STA is coherent
for a combinational probe; PDK files are the right ones (i3); die/core geometry
(300×300 / 270×270 µm, site unithd) is sane for 1700 cells at 25.5% util. Bugs/questionable
steps: **C1** (missing li1 tracks — fatal to routing), **m2** (no `place_pins` — DEF not
routable as delivered), **m1** (area report silently absent), **M2** (constraint setup
vacuous; 10 µs not 10 ns), **m3** (no `estimate_parasitics -placement`). `repair_design`
with defaults and no `check_placement`/filler/PDN is acceptable scoping for a feasibility
probe, not for tapeout.

### 2. Routing failure — version issue or scripting error?
**Scripting error, conclusively.** Same OpenROAD v2.0 binary, same PDK: without li1 tracks →
`[ERROR GRT-0701] Missing track structure for routing layers.` (reproduced); with the li1
`make_tracks` line → global route completes, 0 overflow. The "version check" framing is
wrong; the designer's own `pnr/flow.tcl:16` already states the true cause. Alternatives
assessed: (a) different OpenROAD version — unnecessary; (b) generating tracks differently —
unnecessary, `make_tracks` values match the tech LEF PITCH/OFFSET statements and ORFS
conventions; (c) different Volare revision tech LEF — unnecessary, all Sky130 tech LEFs
omit TRACKS by design (i1). **Fix effort: one line + re-run** (tens of minutes incl.
detailed route).

### 3. Is "physically feasible / routable in principle" defensible without routing?
Partially. What placement+STA actually proves:
- ✅ Netlist is legal and placeable; 0.099% final placement overflow; 25.5% utilization —
  no density/congestion red flag at placement level.
- ✅ 5.07 ns wireload-estimated input→output delay (a measurement, not closure).
- ❌ Nothing about DRC-clean routing, antenna rules, real RC delay, IR drop/EM, or hold.
- ❌ "0 violations" proves nothing (M2).
Weight for a reviewer: placement-only is **weak evidence** for the latency gate, because the
gated number (post-route delay) is exactly what placement cannot produce. *However*, the
designer already possesses stronger evidence than they reported: their own
`pnr/probe_route2.log` shows a completed **global route with 0 overflow** at 8.8% routing
resource usage — for a 1700-cell block at 25% utilization that makes detailed-route success
highly likely, though still unproven. "Routable in principle" is a defensible engineering
judgment **given the global-route result**; "placement+STA demonstrates physical
feasibility" as a *gate-closing* statement is not — the project's hard gate explicitly
requires "actual post-route verification".

### 4. Multiplier comparison — status and concrete path
Status: **not done; requirement unverified.** The ABC-timeout narrative is unevidenced
(the netlist `pnr/synth_mul64_64.v`, 9639 cells, synthesized in 5.15 s). Concrete path:
1. Run the existing `pnr/flow.tcl` (it already does place_pins, global+detailed route,
   `report_drc`, post-route STA hooks) on `pnr/synth_mul64_64.v`. Add
   `estimate_parasitics -detailed_routing` (or `-global_routing`) before the final
   `report_checks` so both designs get real-RC STA.
2. **Do not use the same 300 µm die**: the multiplier is 5.7× larger (9639 vs 1700 cells);
   identical conditions = same PDK corner, same utilization target (~25%), same constraint
   style — i.e. scale the die to ≈ 670–700 µm for equal utilization, not the same absolute die.
3. Compare routed critical-path delays (input→output, same SDC style). Optionally also run
   the mixer through the same `flow.tcl` so both numbers are post-route rather than
   comparing the mixer's post-route number against the multiplier's wireload estimate.
4. If ABC *timing-driven* optimization is desired for fairness (both designs pushed to their
   delay optimum), use `abc -liberty $LIB -constr <sdc>` with a real constraint instead of
   `/dev/null`; if ABC ever does hang on the multiplier, bound it with `timeout` and fall
   back to the already-synthesized netlist — but first reproduce the alleged hang, since no
   evidence of it exists on disk.

### 5. STA setup
Virtual clock `vclk`, period **10000 ns = 10 µs** (not 10 ns — units error, M2);
`set_input_delay 0` / `set_output_delay 0` on all 192 ports; no clock uncertainty, no
derating, no parasitics (wireload model fallback, RSZ-0021). Applied SDC measures pure
combinational input→output propagation. "0 violations" is entailed by the 2000×-loose
constraint, not by design quality. For the A/B comparison this SDC style is acceptable
*if applied identically to both designs post-route*; for any absolute claim it is
meaningless.

---

## What remains to close the P&R gate
1. Fix `pnr_sky130.sh` (or adopt `pnr/flow.tcl`): add the li1 `make_tracks` line; add
   `place_pins`; correct the report narrative (1700 cells, 25.5% util, 10 µs virtual clock).
2. Run full route: `global_route` → `detailed_route` → `write_def` → `report_drc`
   (must be 0 violations) → `estimate_parasitics -detailed_routing` → post-route STA.
3. Run the identical flow on the 64×64 multiplier with die scaled to equal utilization;
   compare post-route critical paths. This is the actual hard-gate requirement.
4. Correct `candidates.md:330-335` and the memory note: replace the GRT-0701
   "version-specific / integration gap" diagnosis with the li1 root cause, replace
   "6883 cells / ~9%" with the P&R-netlist numbers, and drop "0 violations @ 10ns".
5. (Optional, for signoff-grade rigor: ss/ff corners, antenna check, IR drop.)

## Reproduction notes (reviewer-run, /tmp only)
- `/tmp/pnrrepro/repro.tcl`: verbatim flow + `global_route` → GRT-0701, exit 1
  (`/tmp/pnrrepro/repro.log:483-485`).
- `/tmp/pnrrepro/repro2.tcl`: + li1 `make_tracks` + `place_pins` + `global_route` +
  `detailed_route` → global route passed (designer's `pnr/probe_route2.log` shows the
  completed reference: 0 overflow); detailed route was still in pin-access at review time.
- No files under `exploration/` were modified; `round4/` untouched.
