# Critical-path analysis — frontier designs (unit-delay backtrace)

**Tool:** `critpath/critpath.py` (extends `round7/audit/review_synth/critpath.py`).
**Method:** top-10 distinct critical paths backtraced from max-arrival outputs on the
ABC-mapped netlist (authorized `run_synth.py` S0 path only: pinned Yosys 0.69,
`memory_map` before `techmap`, dual-analyzer agreement). Per-path segmentation:
NONLIN (S-box/chi DNF: AND/OR/NAND/NOR/AOI/OAI/MUX/INV) vs XORLIN (XOR2/XNOR2 —
linear layers, key schedule) vs BUF. All numbers unit-delays (u), not silicon.
Netlists reused from each design's own round S0 run (PARETO numbers reproduce
exactly: 28.3/4656, 36.7/4198, 37.4/3667 — no re-synthesis needed).

**Sanity check (2026-10-04):** on `r23_spn_mix3r_lp_nw`, new tool vs round-7
original vs analyze.py agree exactly — crit=21.4u, cells=3812, worst output
out[2], identical 15-gate sequence.
**Fix applied during review:** MUX2 moved to NONLIN (was XORLIN): a 2:1 mux is
AND-OR logic (chi's `a^(~b&c)` maps to it), not XOR-linear.

**Status:** all 8 designs analyzed, JSON checkpoints in `critpath/work/<name>/critpath.json`.
(run_all.py's synthesis queue is redundant now — it self-skips on existing checkpoints.)

---

## 0. The structural finding (read first)

Delay decomposes as **(nonlinear DNF depth per round) × (round count) + linear tail**,
and the per-round nonlinear depth is an invariant across every design:

| Design | Rounds | NL levels | NL/round | Total |
|---|---|---|---|---|
| r22c | 4 | 17 | **4.25** | 28.3u |
| chioff31final | 6 | 27 | **4.5** | 36.7u |
| 3rot_ns | 6 | 26 | **4.33** | 37.4u |
| r21b (fm311) | 6 | 27 | **4.5** | 38.3u |
| chioff13all_fm311 | 6 | 26 | **4.33** | 39.1u |
| r15 parsplit | 6 | 29 | **4.83** | 40.7u |
| r9 | 6 | 33 | **5.5** | 41.0u |
| r8 | 6 | 29 | **4.83** | 42.9u |
| r23 3r probe (sanity) | 3 | 11 | **3.67** | 21.4u |

NONLIN is 79–90% of every critical path; XORLIN (linear layers + key schedule) is
2–12u total. Consequences:

1. **r22c wins by round count, not by cheaper rounds** (4×4.25 vs 6×4.5). The only
   structural ways to beat it: fewer rounds (3r probe → 21.4u, already in round23)
   or sub-4u nonlinear depth per round (untried — S1's depth-minimality claim was
   about the S-box in isolation, not its ABC-mapped DNF).
2. **Linear-layer sweeps cannot move delay much** — the (a,b) rotation sweeps in
   round23/tweaking operate on the 10–20% part. They matter for S2/BIC, not delay.
   (Redirects, not kills: keep them for diffusion, stop expecting delay wins.)
3. **r9 is the outlier at 5.5 NL/round** — its chi placement synthesizes ~1 extra DNF
   level per round vs the family. If its S2 margin allows, a shallower chi buys ~6u.

---

## 1. r22c_spn_mix4r_lp_nw (Frontier S+Q speed point, 28.3u, 4,656 cells)

(a) Path: **key[15] → out[1]**, 20 levels — NONLIN 17/22.3u, XORLIN 3/6.0u.
Sequence: XOR2 → NAND4 → NAND3 → NAND2 → NAND4 → NAND2 → OAI21 → NAND2 → AOI21 →
OR4 → NAND4 → NAND2 → AOI21 → OAI21 → AOI21 → NOR2 → AOI21 → NOR2 → XNOR2 → XNOR2.
Round segments ≈ 8.0 / 7.3 / 8.0 / 5.0u. Diversity: **10 paths at exactly 28.3u**
(spread 0.0u), 4 distinct start bits (key[15], key[61], val[37], …), 10 distinct
outputs — a flat wall, not a peak.

(b) Bottleneck: the S-box DNF (wide NAND4/NAND3/NOR4 gates, 17 levels across
4 rounds). The **key schedule is on the critical path** (path starts at a key bit:
rk XOR → S-box chain); the data-side path (val[37]→out[2], also 28.3u) carries
more linear depth (6 XL/12u). Key-side and data-side are balanced — no asymmetric fix.

(c) Ranked suggestions (hypotheses; → round23):
1. **3-round SPN is the structural answer** — already in flight (21.4u S0). The
   10-path wall at identical delay means no single-path tweak can help; only
   round-count or per-round-depth changes move the number. Falsifier: S2 on 3r.
2. **S-box DNF depth, not S-box choice**: 17/20 levels are NAND/NOR/AOI DNF. The
   MOLS(4) enumeration (in round23) should score candidates by *mapped DNF depth*,
   not just crypto metrics — a 3.5u/round S-box at equal S2 buys ~3u. Falsifier:
   S0 of synthesized variant + S2.
3. **Final XNOR2×XNOR2 tail (4u)**: last round contributes only 5.0u (1 NL + 2 XL);
   the L-layer after the final S-box is pure cost. Weakening/removing the final
   linear is a construction change — S2 decides. Falsifier: S2 on no-final-L variant.
4. Considered/rejected: key-schedule restructuring — the rk XOR is already a single
   XOR2 (2u); key/data sides balanced, nothing to shave.

## 2. r21_feist6_alt_notr_chioff31final_nw (Frontier S, 36.7u, 4,198 cells)

(a) Path: **val[22] → out[37]**, 29 levels — NONLIN 27/32.7u, XORLIN 2/4.0u.
Round segments ≈ 6.5/6.8/6.9/7.1/7.4 + 2.0u tail. Diversity: 10 paths, spread 1.0u.

(b) Bottleneck: chi DNF at ~4.5 NL/round × 6 rounds. Linear layers contribute 4u total.

(c) Suggestions (→ tweaking):
1. **Chi-offset variants targeting DNF depth**: the (3,1) vs (1,3) choice was made
   on S2/size grounds; re-sweep offsets scoring mapped DNF depth first, S2 second.
   Falsifier: S0 delta + S2 per offset.
2. The 2.0u round-6 tail is already minimal (truncated chi) — no further truncation
   available (drop4 proved truncation is only safe on the final chi round).

## 3. r21_feist6_alt_notr_3rot_ns_nw (Frontier S size point, 37.4u, 3,667 cells)

(a) Path: **val[18] → out[49]**, 29 levels — NONLIN 26/31.4u, XORLIN 3/6.0u.
Segments ≈ 6.4–7.7u/round + 2.0u tail. Spread 1.5u (least walled of the family).

(b) Bottleneck: same chi DNF (~4.3 NL/round). The nonsingular 3-rotation linear
costs 6u across 6 rounds — 16% of delay; already optimal (the singular version
was +3.8u).

(c) Suggestions (→ tweaking):
1. Same chi-depth sweep as §2. The 1.5u spread (vs 0.0–1.0u elsewhere) hints the
   wall is softer here — a 1-level DNF shave has the best chance of sticking.
   Falsifier: S0 + S2.

## 4. r21b_3rot_ns_fm311_nw (Frontier Q, 38.3u, 4,299 cells)

(a) Path: **val[47] → out[45]**, 30 levels — NONLIN 27/32.3u, XORLIN 3/6.0u.
Round-6 segment is **4.2u vs 3rot_ns's 2.0u** — the fm311 cure's footprint.

(b) Bottleneck: base chi DNF (as §3) **plus the fm311 cure at +0.9u** (PARETO:
+0.9u on 3rot_ns base, +1.7u on the (1,3)-chi base — cost scales with chi cone).

(c) Suggestions (→ tweaking):
1. **Cheaper BIC cures**: fm311's cost is localized at the F_6 output (XOR2→INV→
   OAI21→…→XNOR2 tail). Any cure with a smaller output cone (fewer affected bits)
   costs less — the cone size, not the cure logic, sets the price. Falsifier:
   S0 + Q1 (bic≤0.02) per cure candidate.
2. Budget rule for Frontier Q: every BIC cure costs ~1–2u; projections for new
   Q candidates should add it up front rather than discovering it after the battery.

## 5. r9_feist6_rot311_nw (Frontier Q, 41.0u, 4,265 cells)

(a) Path: **val[18] → out[40]**, **35 levels** (deepest) — NONLIN 33/37.0u,
XORLIN 2/4.0u. Segments show **7 NL/round in rounds 1–2**. 10-path wall, spread 0.0u.

(b) Bottleneck: the rot311 chi placement synthesizes ~1 extra DNF level per round
vs the chioff family (5.5 vs 4.3–4.5 NL/round) — ~6u of the gap to chioff31final.

(c) Suggestions (→ tweaking):
1. **r9's delay is a chi-placement artifact, not intrinsic**: re-place the chi taps
   (rotation amounts feeding the AND) to minimize mapped DNF depth while keeping
   the differential profile. If r9's S2 margin (|z| max from its battery) has room,
   ~6u is available — that would put it at ~35u, threatening chioff31final.
   Falsifier: S0 + S2.
2. If the margin isn't there, r9 stays a Q-only tradeoff point (bic-clean) — say so
   and stop spending tweaking budget on its delay.

## 6. r8_feist6_s1_1sbox_nw (Frontier Q size point, 42.9u, 4,133 cells)

(a) Path: **val[30] → out[56]**, 32 levels — NONLIN 29/36.9u, XORLIN 3/6.0u.
4.83 NL/round — the S1 single-sbox F is deeper per round than chi.

(b) Bottleneck: S1's mapped DNF (4.83/round) × 6 rounds.

(c) Suggestions (→ GA / round23-S-box-batch):
1. r8's role is Q-size-point, not speed; delay work here is low priority. If the
   MOLS(4)/S-box batch finds a shallower-DNF S-box at equal S2, r8 is the
   natural beneficiary (single-sbox F amplifies per-S-box depth savings ×6).
   Falsifier: S0 + S2 of S-box swap in r8 context.

## 7. Retired extras (analyzed for completeness, off-frontier)

- **r15_feist6_parsplit_nw** (40.7u): val[18]→out[44], 31 levels, NL 29/36.7u
  (4.83/round). Bottleneck identical class to r8 — parsplit-F DNF. No action
  (retired; r21b dominates).
- **r21_feist6_alt_notr_chioff13all_fm311_nw** (39.1u): val[2]→out[53], 30 levels,
  NL 26/31.1u. Same fm311 tail footprint as r21b. No action (retired; r21b dominates).

---

## 8. S5 ground-truth cross-check (r22c)

S5 report: silicon critical path **key[5] → out[35] via XNOR2/NOR3/AOI chain,
4.91ns**; ratio 0.344× vs multiplier (unit-delay S0: 0.273× — same order, PASS).

| | Unit-delay backtrace | S5 STA (silicon) |
|---|---|---|
| Start | key[15] (key bit) | key[5] (key bit) |
| End | out[1] | out[35] |
| Gate mix | XOR2→NAND4/NAND3/NOR4 DNF→XNOR2×2 | XNOR2/NOR3/AOI chain |
| Character | 10-path wall @ exactly 28.3u | single reported path, 4.91ns |

**Agreement:** both start at a KEY bit — the key schedule is on the critical path
in both models. Both are S-box-DNF-dominated with XNOR2/AOI/NOR-class gates.
**Divergence (expected, documented):** different winning start/end bits and a
different gate mix. Mechanism: unit-delay scores every gate 1u (XOR2=2u), so 10
paths tie at exactly 28.3u; STA uses real pin-to-pin delays (NOR3/XNOR2 relatively
slower) plus routed wire delay, which re-ranks the near-critical set and picks a
different winner. **The structural conclusions are robust across both models**
(key-involved, DNF-dominated, multi-path wall); the exact winning path is not —
tweaks must therefore target the wall's shared structure (round count, per-round
DNF depth), never a single path's gates.

---

## 9. Track routing summary

- **round23**: (1) 3r S2 is the highest-value open question (wall argument says it's
  the only structural way past 28.3u); (2) score MOLS(4)/S-box candidates by mapped
  DNF depth alongside crypto metrics; (3) linear-layer (a,b) sweep: keep for S2/BIC,
  stop expecting delay wins (10–21% of delay max).
- **tweaking**: (1) chi-offset/DNF-depth sweep on chioff31final + 3rot_ns (softest
  wall, 1.5u spread); (2) r9 chi-tap re-placement iff S2 margin allows (~6u prize);
  (3) cheaper-BIC-cure search keyed on output-cone size; budget +1–2u for any cure.
- **GA**: (1) add S-box/DNF-depth genes — current cheap-layer genes touch only the
  ~15% linear part of delay; (2) consider critical-path multiplicity
  (delay_spread, n_paths-at-crit) as a fitness term — walls resist single tweaks.

All suggestions are hypotheses with named falsifiers, not validated claims.
Validation happens in the search tracks; this track does not edit PARETO.md.
