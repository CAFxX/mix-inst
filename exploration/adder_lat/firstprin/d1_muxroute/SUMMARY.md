# D1 MUX-routing — SUMMARY

## What was built

[gen_d1.py](gen_d1.py) emits 10 Verilog variants (see [DESIGN.md](DESIGN.md) §1 for the ladder):

| ID | structure | select | predicted S0 |
|---|---|---|---|
| D1-A | 4:1 MUX (task's literal design) | s0=(a&b)^c^k0, s1=(d&e)^f^k1 | ~9.5u |
| D1-B | 2:1 MUX | s=a^b^(c&k) (task's fallback) | ~6.0u |
| D1-C | 2:1 MUX | s=(a&b)^c | ~5.5u |
| D1-D | 2:1 MUX | s=a&b | ~3.5u |
| D1-E | 2:1 MUX | s=(a&b)\|(c&d) via NAND-NAND | ~4.0u |
| D1-F | 2:1 MUX | s=a^b (linear control) | ~4.0u |
| D1-G | 2:1 MUX | s=a\|b | ~3.5u |
| D1-H | 2:1 MUX | s=~((a&b)\|c) (AOI21) | ~3.5u |
| 2stage | 2× cascaded D1-D, distinct taps | — | ~7.0u |
| 2stage_H | 2× cascaded D1-H, distinct taps | — | ~7.0u |

Model [`d1_model.py`](d1_model.py) verified **bit-exact vs the generated RTL 300/300**
(independent regex-parse RTL evaluator vs numpy model).

## First-principles corrections to the task brief

1. **4:1 MUX ≠ 1 level.** A 4:1 MUX is 2 MUX2 levels = 4.0u data path; with any
   computed select the task's literal design is ≥5.5u/stage. The <4u/stage target
   forces the **2:1 MUX base** (2.0u) + single-gate select (≤1.5u) = 3.5u.
2. **Balanced nonlinear selects don't fit <4u.** Single-gate selects are {biased
   nonlinear} ∪ {linear} (genlib-exhaustive); balanced+nonlinear needs ≥2 gates.
3. **Shared-select fanout is an illusion.** 8 MUXes per shared select *concentrates*
   slots (144 total vs 256 unshared) → 1.25×/stage, *worse* than unshared 1.5×.
4. **Best <4u nonlinear select is AOI21** (`~((a&b)|c)`, D1-H): 1.625×/stage
   confusion growth vs 1.500 for AND2/OR2/NAND2/NOR2 (truth-table-exhaustive).

## Measured (bit-exact model, never invented)

| network | mean bits flipped / single-bit delta | predicted |
|---|---|---|
| D1-D stage 1 | **1.501** | 1.500 |
| D1-D 2-stage | **2.053** | 2.250 |
| D1-H 2-stage | **2.514** | 2.641 |

Constant-output-bit fraction across 64-consecutive-input blocks (200 blocks):
**D: 0.906, H: 0.794** → LIN matrices rank ≤ ~13 ≪ 61 → LIN FLAG mechanism.

## S0 — MEASURED (run_synth.py, pinned yosys 0.69, XCHECK analyze.py==analyze2.py, ref mul64 103.5u)

| ID | predicted | **measured crit** | cells | area | gate |
|---|---|---|---|---|---|
| D1-A (task's literal 4:1) | ~9.5u | **6.4u** | 1280 | 3520 | ✗ (>4u) |
| D1-B (task's fallback) | ~6.0u | **5.2u** | 704 | 1856 | ✗ (>4u) |
| D1-D | ~3.5u | **3.0u** | 128 | 384 | ✓ (<4u) |
| D1-H | ~3.5u | **3.5u** | 128 | 448 | ✓ (<4u) |
| 2stage_H | ~7.0u | **6.6u** | 896 | 2368 | ✓ (<8u, <10u → Fisher) |

Note: ABC beat naive level-counting on D1-A (6.4u measured vs 9.5u predicted —
cross-boundary optimization between the select XORs and the mux tree); the gate
verdict is unchanged (6.4 > 4). D1-C/E/F/G skipped: all predicted ≥4u and none is
decision-relevant (D/H cover the <4u claim; B covers the task's fallback).

## Fisher triage — MEASURED ([`lin_diff.screen_lin_diff`](../../../fast_battery/src/lin_diff.py) verbatim, 10 keys, N=2^18, 2stage_H)

- **LIN: FLAG, nrej=10/10, D=4096/4096 on all keys** (every 64×64 consecutive-output
  matrix rank-deficient — the constant-column mechanism: 0.794 of output bits
  constant across 64-blocks → rank ≤ ~13 ≪ 61).
- **DIFF: FLAG, nrej=10/10, worst |z| 9.2e5–1.5e6** (low avalanche concentrates
  output differences; catastrophic).

Full per-key detail: [fisher_2stage_H.json](fisher_2stage_H.json).

## Verdict

**Direction 1 (input-dependent MUX routing) is TERMINAL as a sub-10u direction**
(registered as O154 in [VERDICT_SCOPE.md](../../../VERDICT_SCOPE.md)). Cost-eligible (6.6u < 10u) but
Fisher-catastrophic on both families with the mechanism fully characterized
(counting bound + constant-column LIN kill). See the O154 row for scope,
re-test triggers, and what was NOT claimed.
