# Independent synthesis review: r7_feist8_s1_1sbox

**Claim under review**: RV64 `mix` candidate `r7_feist8_s1_1sbox` synthesizes at
56.5u = 0.546× a 64×64 multiplier reference (103.5u), 6063 cells, area 17098,
via `~/workspace/mix/exploration/run_synth.py`.
**Reviewer**: independent subagent (no contact with other reviewers).
**Date**: 2026-10-02. **Disposition sought**: verify, don't confirm — be adversarial.

## Scope

1. Reproduce the delay/area claim from a **clean environment** (no conda PATH),
   confirming the Yosys 0.69 pin defeats the /usr/bin/yosys-0.33 hazard, and
   confirming both analyzers agree.
2. Independently re-run formal equivalence (RTL ≡ mapped netlist) with
   standalone `yosys-abc cec`, with the reference side built **without**
   `abc`/`dretime` (dretime once miscompiled another candidate).
3. Simulate the mapped netlist against the Python model on ≥2000 vectors
   (iverilog + `cells_sim.v`), including key=0 / val=0 edge cases.
4. Mutation test: flip one S-box entry, re-synthesize, confirm the sim catches it.
5. Critical-path plausibility note.

Out of scope: statistical quality (S1–S4), P&R, peer review of the cipher —
this review covers the synthesis numbers and tooling only.

## Method (exact commands)

Work dir for all review artifacts: `~/workspace/mix/exploration/round7/audit/review_synth/`
(`fresh/`, `cec/`, `sim/`, `mut/`).

### 1. Fresh synthesis, clean env

```bash
cd ~/workspace/mix/exploration
env -i PATH=/usr/bin:/bin HOME=/home/hatch /usr/bin/python3 run_synth.py \
  fast_battery/candidates/r7_feist8_s1_1sbox/rtl.v r7_feist8_s1_1sbox \
  round7/audit/review_synth/fresh
```

`env -i` wipes the environment; PATH has no conda entry (and no yosys at all).
This tests whether the absolute-path pin + version assert in `run_synth.py`
actually works rather than accidentally inheriting a good PATH.

### 2. Formal equivalence, dretime-free reference

Reference BLIF from RTL with **no abc call anywhere** (pure yosys
`proc/opt/flatten/memory_map/techmap/opt/aigmap`):

```bash
Y=/home/hatch/tools/micromamba-root/envs/sky130/bin/yosys
$Y -p "read_verilog .../fast_battery/candidates/r7_feist8_s1_1sbox/rtl.v
hierarchy -check -top r7_feist8_s1_1sbox
proc; opt; flatten; memory_map; opt; techmap; opt
aigmap
write_blif rtl.blif"          # in review_synth/cec/
```

Implementation BLIF from the saved mapped netlist + behavioral cells:

```bash
$Y -p "read_verilog .../exploration/fast_battery/src/cells_sim.v
read_verilog .../round7/results/r7_feist8_s1_1sbox/_synth/_dut/mapped_r7_feist8_s1_1sbox.v
hierarchy -check -top r7_feist8_s1_1sbox
proc; opt; flatten; opt
aigmap
write_blif net.blif"
```

Then:

```bash
/home/hatch/tools/micromamba-root/envs/sky130/bin/yosys-abc -c "cec rtl.blif net.blif"
```

`cec` defaults to matching CIs/COs **by name**; I verified both BLIF files list
identical `.inputs val[0..63] key[0..63]` / `.outputs out[0..63]`, so the
matching is sound (no positional aliasing risk).

### 3. Vector simulation (iverilog + independent bit-parallel sim)

```bash
cd review_synth/sim
python3 gen_vecs.py   # 2048 seeded (0xC0FFEE) random (val,key) + 6 edge cases
                      # -> vectors.hex (128-bit val:key), expected.hex (model outputs)
~/tools/micromamba-root/bin/iverilog -o sim_good \
  ~/workspace/mix/exploration/fast_battery/src/cells_sim.v \
  ~/workspace/mix/exploration/round7/results/r7_feist8_s1_1sbox/_synth/_dut/mapped_r7_feist8_s1_1sbox.v \
  tb.v
./sim_good
```

`tb.v` drives each vector, settles `#10`, compares with `===` (X-sensitive: an
undriven net can never silently "match"), prints `RESULT MATCH=.. MISMATCH=..`.

Edge cases (first 6 vectors): `(0,0)`, `(0, 0x123456789ABCDEF0)`,
`(0xFEDCBA9876543210, 0)`, `(all-ones, all-ones)`, `(1, 0)`, `(msb, msb)`.

Additionally, an **independent simulator** (`bpsim.py`, written for this review,
no iverilog/yosys/abc code): topological evaluator over the mapped netlist
with all 2054 vectors bit-parallel in Python ints (bit i of each net = value
under vector i). Guards against a systematic iverilog miscompile.

### 4. Mutation

```bash
cd review_synth/mut
sed 's/4.h0: sbox_feist8_s1_1sbox = 4.h0;/4'"'"'h0: sbox_feist8_s1_1sbox = 4'"'"'h1;/' \
  .../fast_battery/candidates/r7_feist8_s1_1sbox/rtl.v > rtl_mut.v
# flip S(0): 0 -> 1 ; verified by diff: only line 12 differs
env -i PATH=/usr/bin:/bin HOME=/home/hatch /usr/bin/python3 \
  .../exploration/run_synth.py round7/audit/review_synth/mut/rtl_mut.v \
  r7_feist8_s1_1sbox round7/audit/review_synth/mut/synth
python3 ../sim/bpsim.py mut/synth/_dut/mapped_r7_feist8_s1_1sbox.v \
  ../sim/vectors.hex ../sim/expected.hex
```

### 5. Critical path trace

`critpath.py` (review_synth/): re-implements the analyzer's arrival computation
on the fresh netlist, backtracks from the worst output, prints the cell
sequence. (Cross-checked total = 56.5u = analyzer's number.)

## Findings

### Check 1 — clean-env re-synthesis: PASS (no finding)

```
REF mul64: cells=12645 area=35323 crit=103.5
DUT r7_feist8_s1_1sbox: cells=6063 area=17098 crit=56.5
RESULT ... delay_ratio=0.546 area_ratio=0.484 ref_crit=103.5 ref_area=35323
XCHECK: analyze.py == analyze2.py (cells/area/crit identical)
```

- Reproduces the claimed numbers **exactly**: 56.5u, 0.546×, 6063 cells,
  area 17098, ref 103.5u — from `env -i` with PATH=/usr/bin:/bin (no conda,
  no yosys on PATH at all). The absolute-path pin + `"0.69" in yosys -V`
  assert works; the /usr/bin/yosys-0.33 hazard class is defeated for this
  script. (For the record, `/usr/bin/yosys` does not exist on this machine —
  the hazard was environmental, but the pin makes the script immune regardless.)
- Analyzer cross-check fired and agreed (the script raises on any mismatch in
  cells/area/crit; it printed the XCHECK line).
- The **saved** netlist
  (`round7/results/r7_feist8_s1_1sbox/_synth/_dut/mapped_r7_feist8_s1_1sbox.v`)
  re-analyzed independently with both analyzers: `cells: 6063 total_area: 17098
  critical_path: 56.5` from **both** — the saved artifact is current, not stale.

### Check 2 — ABC cec RTL ≡ netlist: PASS (no finding)

```
/home/hatch/tools/micromamba-root/envs/sky130/bin/yosys-abc -c "cec rtl.blif net.blif"
======== ABC command line "cec rtl.blif net.blif"
Networks are equivalent.  Time =    21.07 sec
```

- Exact verdict: **`Networks are equivalent.  Time =    21.07 sec`** (exit 0).
- The reference side never went through `abc`/`dretime` (pure yosys
  techmap→aigmap), so this is a genuine independent proof against the
  dretime-miscompile failure mode seen on h_xorspn3 — not a vacuous
  same-bug-on-both-sides check.
- CI/CO matching by name verified sound: both BLIFs expose identical
  `val[0..63] key[0..63]` / `out[0..63]` lists.
- The mapped netlist is fully mapped: 0 `assign` statements, 6063 cell
  instances, every instance type covered by `cells_sim.v` (cross-checked the
  18-type histogram against the sim models).

### Check 3 — mapped netlist vs Python model, 2054 vectors: PASS (no finding)

- Independent bit-parallel sim (`bpsim.py`, my own code, no shared
  infrastructure with iverilog/yosys): **MATCH=2054 MISMATCH=0** in 4.3 s.
  Includes the 6 edge cases (key=0, val=0, all-ones, msb-only).
- iverilog run (`sim_good`, cells_sim.v + saved mapped netlist + tb.v,
  `===` comparison): **RESULT MATCH=2054 MISMATCH=0**.
  (10-vector calibration run also 10/10; the full run was slowed by machine
  contention — 2 cores, load ~13 from parallel jobs — but completed with the
  same 2054/2054 result.)
- The `===` comparison means X/undriven nets would have shown up as mismatches;
  2054/2054 exact matches means the netlist genuinely computes the model.

### Check 4 — mutation sensitivity: PASS (no finding)

- Mutated RTL (S(0): 0→1, single-line diff confirmed) re-synthesized clean-env:
  6657 cells / 18630 area / 58.3u — the change propagated through synthesis
  (different cell count and delay than the 6063/17098/56.5 original).
- Mutated netlist vs original expected outputs: **MATCH=31 MISMATCH=2023**.
  The 31 accidental matches are quantitatively predicted: each evaluation does
  64 S-box lookups and the mutation only fires on input nibble 0,
  (15/16)^64 ≈ 1.6% × 2054 ≈ 33. The sim is demonstrably sensitive — a
  single-entry S-box change is caught overwhelmingly.

### Check 5 — critical-path plausibility: reasonable (no finding)

Traced critical path on the fresh netlist: **42 cells, 56.5u**, worst output
`out[35]`. Per-round ≈ 5.25 cells / 7.06u. The path alternates S-box clusters
(NAND2/3/4, NOR2/3/4, AOI21, OAI21) with XOR2/XNOR2 stages — exactly the
F-function anatomy (S-box layer → `t ^ rotl7(t) ^ rotl13(t)` → `^ rk32`),
preceded by a whitening XOR2/XNOR2 at the inputs. No anomalously deep or
shallow structure; 42 cell levels for 8 Feistel rounds of this F is
proportional (compare: r6's 86.5u with two S-box layers per round ≈ 1.53×,
consistent with ~2× the S-box depth per round).

### Adversarial notes (considered, not findings)

- **dretime**: the known-bad pass is in the default `abc -genlib` script used
  to produce the netlist. Mitigated by (a) the cec proof above with a
  dretime-free reference, and (b) 2054-vector functional agreement with the
  Python model. Both would have to fail correlatively for a dretime bug to
  survive; they didn't.
- **Analyzer gaming**: `analyze.py` hard-errors on functional assigns driving
  live nets (the 8.9u-vs-86.5u bug class); the netlist has zero assigns.
  Both analyzers are byte-identical in output on all three netlists examined
  (fresh DUT, saved DUT, mutated DUT).
- **Reference sanity**: mul64 at 103.5u/12645 cells is a plausible 64×64
  multiplier in these unit delays, and it re-measured bit-identically across
  three independent runs (fresh, mutation, and the saved-results run).
- **Sim-oracle circularity**: the Python model is the oracle for the sim, and
  the RTL was hand-written against it — a spec bug shared by model+RTL would
  not be caught here. That's outside this review's scope (statistical battery
  + peer review cover the design), but noted for completeness.
- **Units**: "u" are mini.genlib relative unit-delays, not picoseconds; only
  the 0.546× ratio is meaningful. The claim presents it as a ratio — correct.

## Verdict

**APPROVE** — no BLOCKER, MAJOR, or MINOR findings.

- The 56.5u / 0.546× / 6063-cell / 17098-area claim reproduces **exactly**
  from a clean environment; the Yosys 0.69 pin defeats the PATH hazard.
- `yosys-abc cec` (dretime-free reference): "Networks are equivalent."
- Mapped netlist ≡ Python model on 2054/2054 vectors (iverilog **and** an
  independent bit-parallel simulator), edge cases included.
- Mutation (one S-box entry) is caught: 2023/2054 mismatches.
- Critical path (42 cells, 56.5u, S-box/XOR alternation) is structurally
  plausible for 8 Feistel rounds of this F-function.
- Both analyzers agree everywhere; the saved netlist artifact is current.

Review artifacts: `~/workspace/mix/exploration/round7/audit/review_synth/`
(`fresh/`, `cec/`, `sim/`, `mut/`, `critpath.py`).
