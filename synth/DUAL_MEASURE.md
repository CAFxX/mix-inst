# Dual Critical-Latency Measurement

Carlo's directive (2026-10-12): every design gets **two** latency numbers —
standard HD cells and high-speed/high-drive HS cells.

## The two flows

Both flows mirror `exploration/run_synth.py` methodology (Yosys 0.69 →
`abc` technology mapping → topological critical-path analysis), but use
real Sky130 Liberty timing instead of the unit-delay `mini.genlib`.

| Flow | Library | Corner | File |
|------|---------|--------|------|
| HD (baseline) | `sky130_fd_sc_hd` | tt_100C_1v80 | volare PDK (installed) |
| HS (optimized) | `sky130_fd_sc_hs` | tt_100C_1v80 | `synth/pdk_hs/` (chipfoundry/volare tarball) |

**Script:** `synth/run_synth_hs.py <verilog> <top> <workdir> [--lib hd|hs]`
**Analyzer:** `synth/analyze_liberty.py` (parses Liberty, extracts per-cell
intrinsic delay = min over cell_rise/cell_fall tables, topological crit path).

Yosys command: `abc -liberty <file.lib>` (replaces `abc -genlib mini.genlib`).

## Calibration (measured, not estimated)

All numbers from actual synthesis runs, Yosys 0.69, TT 100C 1v80.

### 64-bit adder (`synth/add64.v`)

| Flow | Critical path | Cells | Area |
|------|---------------|-------|------|
| Unit-delay (mini.genlib) | 83.0u | — | — |
| Sky130 HD | 2.0943 ns | 305 | 1988 |
| Sky130 HS | 1.4428 ns | 302 | 2581 |

HS is 31% faster than HD for the adder (1.44 vs 2.09 ns), at 30% more area.

### 64-bit multiplier (`synth/mul64.v`, reference)

| Flow | Critical path |
|------|---------------|
| Sky130 HD | 2.4891 ns |
| Sky130 HS | 1.5591 ns |

Adder/mul64 ratio: 0.841 (HD), 0.925 (HS) — both under the S0 ≤0.9× bar
(HD) or close (HS; the multiplier benefits more from HS sizing).

### Frontier validation (`t6_b59_47`, 18.6u unit-delay)

| Flow | Critical path | Delay ratio vs mul64 |
|------|---------------|----------------------|
| Unit-delay | 18.6u | 0.180 |
| Sky130 HD | 0.4993 ns | 0.201 |
| Sky130 HS | 0.3790 ns | 0.243 |

HD ratio within 12% of unit-delay — sanity check passes. HS gives a
24% speedup over HD for t6_b59_47 (0.379 vs 0.499 ns).

## Re-expressed targets

The <10u / <8u goal (O131) was set against the 83u unit-delay adder
(1/10th adder latency). In real silicon:

**HD:**
- **<10u** → <(10/83)×2.0943 = **<0.252 ns**
- **<8u** → <(8/83)×2.0943 = **<0.202 ns**

**HS:**
- **<10u** → <(10/83)×1.4428 = **<0.174 ns**
- **<8u** → <(8/83)×1.4428 = **<0.139 ns**

Current frontier (t6_b59_47): 0.4993 ns (HD), 0.3790 ns (HS).
- HD: needs ~2× for <10u-equivalent, ~2.5× for <8u-equivalent.
- HS: needs ~2.2× for <10u-equivalent, ~2.7× for <8u-equivalent.

The HS numbers are the "optimized layout" targets Carlo asked for —
what's achievable with high-drive cells.

## Library versions

- HD: volare sky130 `c6d73a35f524070e85faff4a6a9eef49553ebc2b` (open_pdks),
  `sky130_fd_sc_hd__tt_100C_1v80.lib` (from `~/.volare`).
- HS: chipfoundry/volare `sky130-e0f692f46654d6c7c99fc70a0c94a080dab53571`,
  `sky130_fd_sc_hs__tt_100C_1v80.lib` (35MB, in `synth/pdk_hs/`; the 726MB
  source tarball was deleted after extraction).

## Methodology notes

- `analyze_liberty.py` uses **intrinsic delay** (min over timing tables =
  fast input, light load), mirroring the unit-delay model's intent. Using
  max (worst-case corner) overestimates by ~20×.
- The topological analysis does not model wire load or coupling — absolute
  ns values are pre-layout estimates. **Ratios** (design vs adder, HD vs HS)
  are the meaningful comparison, same as the unit-delay flow.
- Yosys ABC with `-liberty` performs delay-aware mapping; the cell
  selection differs from the genlib flow (e.g. prefers complex AOI/OAI
  gates). This is intended — it reflects what the real flow would do.
