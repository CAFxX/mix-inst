# Peer review — round-3 winner `r3_xorlin_qm` (consolidated)

**Design:** `rtl/r3/r3_xorlin_qm.v` — 4-round SPN, Quine–McCluskey-minimized PRESENT
S-box, function-identical to `spn4_xorlin_1137`. **Date:** 2026-10-01.
**Coordinator:** this report consolidates four independent peer reviews
(RTL, statistics, synthesis, P&R methodology), each conducted by an agent with no
access to the designer's notes, plus remediation and new measurements.

**Bottom line:** the design is functionally correct and genuinely clears the
≤44.3-unit-delay bar with margin, but three classes of claim were overstated and
have been corrected: (1) the P&R narrative (wrong cell count, misdiagnosed
routing failure, vacuous STA framing, missing multiplier comparison) —
root-caused and replaced with an identical-condition Sky130 A/B (global-route
STA: mixer 5.91ns vs 64×64 multiplier 12.56ns = 0.47×, better than the 0.787
screening ratio); (2) the statistical story ("calibrated at α=0.01",
"hash-map uniformity OK") — the screen is sound *as a screen* but the wording
overclaimed, and new differential measurements show strong key-independent
joint structure that the screen never probed; (3) the 0.787× ratio is
flow-relative — the model's fanout-blindness and ABC-naive reference (M4/M5)
remain true as stated limitations, though the silicon A/B shows the net effect
favored the DUT in this flow. The design remains the round-3 winner and
Pareto-optimal for the hash-map use, with the battery failures (PractRand BRank,
TestU01 SimpPoker) now joined by a characterized differential profile.

---

## 1. Findings by severity

### Critical

- **C1 [P&R] — GRT-0701 misdiagnosed; routing failure was a scripting omission.**
  Root cause is a missing `li1` `make_tracks` line in `pnr_sky130.sh`, reproduced
  on the same OpenROAD v2.0 binary: adding the li1 line completes global route
  with 0 overflow. Not a tool/PDK version issue. The designer's own
  `pnr/flow.tcl:16` already documented this. Fixed (see §2).

### Major

- **M1 [P&R] — reported "6883 cells / ~9% util" contradicts the artifacts.**
  The actual placed design is **1700 instances at 25.5% utilization** (GPL-0019);
  6883 is the unit-delay screening-flow count wrongly carried over.
  Corrected in `candidates.md` (see §2).
- **M2 [P&R] — "0 STA violations" vacuous.** The virtual clock is 10µs, not 10ns
  (1000× units error in the narrative), with zero IO delays, on a pre-route
  netlist with wireload-model timing. 5.07ns is a delay *measurement*
  (a lower bound), not closure. Narrative corrected; superseded by the
  global-route STA A/B in §3.3 (5.91ns with Steiner-tree wire estimates).
- **M3 [P&R] — multiplier comparison never ran; "ABC timed out" unevidenced.**
  The multiplier netlist `pnr/synth_mul64_64.v` (9639 cells) synthesized in
  5.15s. The hard requirement "latency ≤ multiplier post-route under identical
  conditions" was unverified. Now verified at global-route level: identical
  flow/corner, matched ~25% utilization, mixer 5.91ns vs multiplier 12.56ns
  (§3.3). Detailed-route + DRC still pending (environment).
- **M4 [synth] — fanout-blind unit-delay model flatters the DUT asymmetrically.**
  All fanout-delay fields in `synth/mini.genlib` are 0. The DUT's 30-gate
  critical path drives on-path nets with fanout 11/12/13/14 (629 nets ≥ fanout 8
  overall); the multiplier reference's 38-gate critical path never exceeds
  fanout 4 on-path. 40.0 is optimistic *relative to* the 50.8 it is divided by,
  by an unquantified amount.
- **M5 [synth] — the 50.8 reference is an ABC-naive multiplier, not a production one.**
  ABC `-fast` does no Booth/CSD recoding (`candidates.md:103` acknowledges the
  class); a real 64×64 multiplier is faster and smaller than 50.8u/46073.
  Both M4 and M5 bias the 0.787 ratio the same way (downward). The ratio is
  solid *as flow-relative screening* (reproduced bit-exactly, exact
  longest-path computation cross-checked by two analyzers, reference re-measured
  fresh each run, conservative absolute 44.3 bar, 9.7% margin) but must be quoted
  as "0.787× under the ABC/mini.genlib screening model", not as a silicon prediction.
- **M6 [synth] — Sky130 "0 violations at 10ns" misframes the result; no multiplier
  counterpart.** Placed-only, unrouted (no wire RC — optimistic lower bound),
  unconstrained near fmax; `results/r3/pnr_mul64/` was empty. Honest statement:
  "placed, unrouted STA gives 5.07ns (TT/100C/1.8V), a lower bound; physical
  feasibility demonstrated, not timing closure."
- **M7 [stats] — "calibrated at α=0.01" overstates rigor (claim B).**
  The calibrated screen is accepted *as screening evidence*, but: Fisher-combination
  dependence was never calibrated; catalog coverage is partial (2 random keys vs
  the ≥32 the methodology's own scenarios doc requires; shrunken reduction sets;
  GRAY/UPSTREAM/BYTE-REP/SPARSE-HD/PTR-RAND/SMALL-INT scenarios never run);
  extreme-point-only validation controls; two Holm families ⇒ FWER ≤ 0.02,
  not 0.01. Wording must say "screened clean (0/468 Holm rejections)" with the
  coverage delta documented, not "calibrated".
- **M8 [stats] — claim C ("hash-map uniformity OK, not PRNG-grade") REJECTED as stated.**
  Sequential-counter input *is* the deployment distribution, so "not the
  deployment" doesn't neutralize the battery failures; BRank R=+622…+754 is a
  hundreds-of-sigma linear-dependency signal; SimpPoker (p<1e-300) probes bits
  [7:2] — exactly the low-bit region mask reductions consume; differentials are
  key-independent by construction, so a per-map secret seed doesn't neutralize
  them; and there is a 128× sample-size mismatch (batteries at 2²⁵ vs screen
  at 2¹⁸). New differential data (§3) sharpens this further.
- **M9 [stats/new data] — strong key-independent differential/truncated-differential
  structure, unprobed by the screen.** For single-bit input differences δ=2^i,
  the 4-round cipher shows large output-difference biases: per-output-bit flip
  biases up to ~0.05 (z>200 at N=2²¹ pairs, confirmed in two independent
  implementations — C and numpy) and truncated differentials on the low 8 bits
  with χ² up to ~29000 on 255 dof (≈1250σ, δ=0x9; ~18000 for weight-1 δ=2²),
  key 0x123456789ABCDEF0, sequential inputs. 37/64 weight-1 deltas show
  max|z|>10. The low-8-bit
  region is exactly what mask reductions consume. This does **not** break
  single-output uniformity (the screen's marginal cells still pass at N=2²⁴,
  §3) — it is joint structure across related inputs, i.e. precisely the class
  the PractRand/TestU01 failures belong to. Adversarial implications
  (collision-forcing / hash-flooding surface) are not analyzed.

### Minor

- **m1** [stats] Dieharder is NOT installed — the note claiming 3.31.1 at
  /usr/bin/dieharder is stale. (Low priority: two batteries already fail
  decisively; differential analysis was the higher-signal follow-up.)
- **m2** [stats] C reference model vs numpy: cross-checked bit-exact on
  h(0)/h(1)/h(2⁶⁴−1) for the tested key during remediation — no divergence found.
- **m3** [P&R] `report_area` missing from the original `timing.rpt`.
- **m4** [P&R] `place_pins` omitted — delivered DEF not routable as-is. Fixed.
- **m5** [P&R] no `estimate_parasitics -placement` before the original STA. Fixed.
- **m6** [P&R] relative paths baked into generated pnr.tcl.
- **m7** [synth] `gen_wallace.py` is not the 50.8 reference (it's a
  constant-multiplier generator for a separate experiment); the reference is
  behavioral `synth/mul64.v` via ABC. Keep provenance straight.
- **m8** [synth] predecessor cell count is 7360 in the current flow, not 7450
  (immaterial).
- **m9** [RTL/info] `results/r3/_r3_xorlin_qm/` keeps no saved PASS log for the
  equivalence run (only stdout); future runs should tee it. Re-ran: 500/500 PASS.

### Info (no action)

- QM SOP → multi-level NAND/NOR/AOI glitches more than 2-level AND-OR: power
  note, no delay/functional impact under STA/registered use.
- Bar conservatism: absolute 44.3 (0.9× old 49.2) is stricter than 0.9×50.8=45.72.
- TRACKS-less tech LEF is by-design; CTS correctly absent (combinational);
  PDK references correct; placement healthy (0.099 overflow).
- RTL review: **PASS** — S-box exhaustive 0/64 mismatches; round structure,
  all 5 round-key constants, rotation directions/wirings verified; QM fix
  present and exactly minimal (independent brute-force exact cover agrees:
  6/5/5/5 cubes); bijectivity proved (linear-layer GF(2) rank 64, S-box a
  permutation); 1-cycle pipeline claim validated adversarially (a true-2-cycle
  variant fails the unmodified testbench); emitter reproduces the RTL byte-for-byte.

---

## 2. Remediation performed (coordinator, 2026-10-01)

| # | Action | Evidence |
|---|--------|----------|
| 1 | `pnr_sky130.sh` rewritten: li1 `make_tracks` (C1), `place_pins` (m4), full global+detail route, `report_drc`, `estimate_parasitics -detailed_routing` before STA (m5), die-size parameter, honest STA comments (M2/M6) | `pnr_sky130.sh` |
| 2 | Routed A/B, identical flow/corner (M3): full detailed-route runs were killed by the loaded machine; fell back to global-route + `estimate_parasitics -global_routing` STA. Result at matched ~25% utilization: mixer **5.91ns** vs 64×64 multiplier **12.56ns** (TT/100C/1.8V) = **0.47×** — better than the 0.787 screening ratio. | `pnr/wd_mixer_gr/timing.rpt`, `pnr/wd_mul_gr545/timing.rpt`, `pnr/flow_gr.tcl` |
| 3 | Differential profile: C profiler over all 64 weight-1 + 8 weight-2 input deltas at N=2²² pairs × 2 keys; per-bit flip bias, low-8-bit truncated χ², full-64-bit repeat counts (M8/M9) | `peer_review_r3_tools/diffprof.c`, `results/r3/diffprof_key1234.txt`, `results/r3/diffprof_key0.txt` |
| 4 | Reduction cells re-run at N=2²⁴ (64× the screen) on SEQ and PTR-j8, both keys, reusing `screen_lib` cell statistics exactly (reviewer's C3) | `peer_review_r3_tools/recell24.py` → `/tmp/recell24.txt` |
| 5 | `candidates.md` P&R section corrected: 1700 instances / 25.5% (M1), li1 root cause (C1), 5.07ns as placed-unrouted lower bound (M2/M6), multiplier "ABC timeout" note retracted (M3) | `candidates.md` |
| 6 | C model vs numpy cross-checked bit-exact (m2) | §3 |

---

## 3. New measurement results

### 3.1 Differential profile (sequential inputs = deployment distribution)

(Tables: `results/r3/diffprof_key1234.txt`, `results/r3/diffprof_key0.txt` —
N=2²² pairs per delta, deduped unordered pairs.)

Key 0x123456789ABCDEF0 (N=2²² deduped pairs per delta; null: max|z|≈4.5,
low8-χ²=255±23, repeats≈0). 40 of 72 deltas flagged (max|z|>10 or χ²>400 or
repeats>0); the rest sit at null levels:

| δ (input difference) | max|z| over 64 output bits | low8 χ² (255 dof) | full-64-bit repeats |
|---|---|---|---|
| `0x0000000000000002` (bit 1) | 26.1 | 4684.7 | 0 |
| `0x0000000000000004` (bit 2) | 63.5 | 17937.2 | 3 |
| `0x0000000000000020` (bit 5) | 25.2 | 264.4 | 0 |
| `0x0000000000000040` (bit 6) | 80.1 | 265.9 | 0 |
| `0x0000000000000200` (bit 9) | 33.5 | 254.2 | 0 |
| `0x0000000000000400` (bit 10) | 119.0 | 293.0 | 1 |
| `0x0000000000002000` (bit 13) | 53.1 | 332.3 | 1 |
| `0x0000000000004000` (bit 14) | 27.9 | 342.8 | 0 |
| `0x0000000000020000` (bit 17) | 25.5 | 255.2 | 0 |
| `0x0000000000040000` (bit 18) | 164.2 | 282.4 | 4 |
| `0x0000000000100000` (bit 20) | 18.9 | 262.9 | 0 |
| `0x0000000000200000` (bit 21) | 23.8 | 270.7 | 0 |
| `0x0000000000400000` (bit 22) | 48.2 | 291.7 | 0 |
| `0x0000000000800000` (bit 23) | 14.8 | 277.7 | 0 |
| `0x0000000001000000` (bit 24) | 22.0 | 1012.3 | 0 |
| `0x0000000004000000` (bit 26) | 222.4 | 1427.7 | 11 |
| `0x0000000010000000` (bit 28) | 12.0 | 467.2 | 0 |
| `0x0000000040000000` (bit 30) | 158.1 | 9964.2 | 4 |
| `0x0000000100000000` (bit 32) | 24.7 | 240.9 | 0 |
| `0x0000000200000000` (bit 33) | 47.2 | 279.3 | 0 |
| `0x0000000400000000` (bit 34) | 15.8 | 280.1 | 0 |
| `0x0000002000000000` (bit 37) | 210.1 | 9283.0 | 6 |
| `0x0000010000000000` (bit 40) | 28.4 | 282.9 | 0 |
| `0x0000040000000000` (bit 42) | 11.9 | 299.5 | 0 |
| `0x0000200000000000` (bit 45) | 91.9 | 246.3 | 2 |
| `0x0000400000000000` (bit 46) | 162.0 | 231.9 | 12 |
| `0x0000800000000000` (bit 47) | 17.0 | 270.5 | 0 |
| `0x0001000000000000` (bit 48) | 23.7 | 257.5 | 0 |
| `0x0004000000000000` (bit 50) | 19.9 | 247.6 | 0 |
| `0x0010000000000000` (bit 52) | 20.2 | 337.1 | 0 |
| `0x0040000000000000` (bit 54) | 11.7 | 409.5 | 0 |
| `0x0100000000000000` (bit 56) | 15.2 | 557.2 | 0 |
| `0x0200000000000000` (bit 57) | 17.1 | 364.6 | 0 |
| `0x0400000000000000` (bit 58) | 12.6 | 344.1 | 0 |
| `0x0800000000000000` (bit 59) | 10.8 | 368.3 | 0 |
| `0x2000000000000000` (bit 61) | 27.1 | 8467.5 | 1 |
| `0x4000000000000000` (bit 62) | 17.8 | 328.9 | 0 |
| `0x0000000000000003` (wt 2) | 52.8 | 3189.5 | 0 |
| `0x0000000000000005` (wt 2) | 31.7 | 2526.1 | 0 |
| `0x0000000000000009` (wt 2) | 103.6 | 29024.5 | 6 |

Reading: per-output-bit flip biases reach |p−0.5|≈0.05 (z=222 at N=2²²);
low-8-bit truncated differentials reach χ²≈29000 on 255 dof (≈1250σ);
full-64-bit output differences repeat up to 12× in 2²² pairs where ~0 are
expected under uniformity — i.e. differentials with probability ≫2⁻⁶⁴ exist.
Strongest signals concentrate on input bits ≡1,2 (mod 4) (the middle bits of
each S-box nibble). Key-0 sweep (`results/r3/diffprof_key0.txt`): 37 deltas
flagged, max|z|=259 (δ=2⁶¹), low-8-bit χ² up to 194367 (δ=2⁶¹) — same class and
magnitude of signal as key 0x1234 (specific loudest deltas differ because the
key shifts the sequential input window; the differential structure itself is
key-independent by construction).

Cross-implementation check (numpy, independent code path): δ=2¹⁸ → output bit
20 flip bias −0.0089 (z=−18.2 at N=2²⁰ random pairs); δ=2²⁶ → bit 28 bias
−0.0093 (z=−19.0). Sequential-input magnitudes are larger than random-input
magnitudes (input-distribution dependence under investigation — see §4.6).

**Collision-forcing advantage (adversarial reading).** For chosen input δ, the
low-8-bit output-difference distribution (the mask-8 bucket region), N=2²²
sequential pairs, key 0x1234…F0 (`peer_review_r3_tools/colladv.c`):
- δ=0x9: P(dx₈=0)=0.00455 vs 1/256=0.00391 → **1.17×**; best target dx₈=0x0b
  at 1.25× expected. Top-8 values all 1.22–1.25×.
- δ=0x4: P(dx₈=0) at 1.19×; best 0x08 at 1.24×.
- δ=2²⁶: best 1.05×; δ=2³⁰: best 1.08× — no practical advantage.
So a chosen-input attacker forcing low-8-bit collisions (hash-flooding the
mask-8 buckets) gets at most ~1.2× over brute force per pair — a real but
modest pairwise edge; multi-way chaining (many keys, one bucket) is unanalyzed
and is the actual hash-DoS primitive. This bounds M9's practical severity for
the 8-bit-bucket use: measurable, not catastrophic, and worth a differential
bound as a design constraint for round 4.

### 3.2 Reduction cells at N=2²⁴ (64× the screen's N)

Exact `screen_lib` cell statistics (mask8, mask32 = worst of lo16/hi16/coll,
lemire 10/1000/2³²) on SEQ and PTR-j8, two keys. Null: |z|≲4.

| scenario | key | mask8 | mask32 (worst) | lemire-10 | lemire-1000 | lemire-2³² |
|---|---|---|---|---|---|---|
| SEQ | 0x123456789ABCDEF0 | +1.07 | hi16 −1.00 | −0.38 | −2.07 | −1.27 |
| SEQ | 0x0 | −0.72 | hi16 +2.21 | +0.12 | +0.93 | +0.18 |
| PTR-j8 | 0x123456789ABCDEF0 | −0.58 | lo16 −0.12 / hi16 −0.17 | +1.11 | +0.34 | −0.34 |
| PTR-j8 | 0x0 | +1.49 | lo16 +1.99 / hi16 −0.61 | +1.69 | +0.88 | +0.01 |

All |z| ≤ 2.21 at N=2²⁴ (null: |z|≲4): clean at 64× the screen's sample size —
the marginal (single-output) uniformity the screen measured is real and
strengthens with N. (Differential joint structure in §3.1 is a different
statistic and is unaffected by this.)

### 3.3 Routed post-route A/B (Sky130, TT/100C/1.8V, identical flow)

Global-route + `estimate_parasitics -global_routing` STA (detailed route did
not survive the loaded machine — both full-route runs were killed mid-route;
the GR STA below replaces the wireload model with real Steiner-tree wire
estimates, a strict improvement over the 5.07ns placed-only number):

| design | die | util | critical path | endpoints |
|---|---|---|---|---|
| `r3_xorlin_qm` | 300µm | 25.50% | **5.91ns** | key[7] → out[26] |
| `mul64_64` (64×64→64) | 670µm | 16.22% | 12.51ns | b[4] → y[63] |
| `mul64_64` (64×64→64) | **545µm** | **25.08%** | **12.56ns** | b[23] → y[63] |

Ratio at matched utilization: **5.91/12.56 = 0.47×** — the mixer is *faster*
vs the multiplier in Sky130 than the 0.787 unit-delay ratio suggests, and the
number is insensitive to the utilization match (0.470 vs 0.471). Plausible
cause: the multiplier's high-fanout nets (max 76, per the synthesis review)
cost real delay in silicon but 0 in the unit-delay model, so the model
flattered the multiplier absolutely more than it flattered the DUT relatively
(M4's asymmetry cuts both ways across the two designs' different fanout
profiles). Full detailed-route + DRC remains undone (the long runs were killed
by the loaded machine); `pnr/flow_gr.tcl` reproduces the GR A/B,
`pnr/flow_full.tcl` the full route.

Caveat: `mul64_64` is ABC-mapped with no Booth/CSD recoding (M5) — a production
multiplier would be faster than 12.56ns. The A/B is apples-to-apples *within
this flow*, not vs best-in-class silicon.

---

## 4. Remaining open items

1. **Adversarial analysis of the differential structure (M9)** — pairwise
   collision-forcing bounded during remediation (§3.1: ≤1.25× over brute force
   for low-8-bit targets). What remains: multi-way chaining (many keys into one
   bucket — the actual hash-DoS primitive) is unanalyzed, and no differential
   bound exists as a design constraint. Required before any "production-ready"
   claim; the round-4/new-primitives track should adopt one.
2. **Silicon-side delay ratio** — QUANTIFIED at global-route level (§3.3):
   0.47× (5.91ns vs 12.56ns @ matched ~25% util, identical flow/corner).
   Detailed-route + DRC remains undone (machine killed the long runs); the GR
   number already reverses the M4/M5 worry direction — the screening ratio was
   pessimistic, not optimistic, vs this ABC-mapped multiplier. A production
   Booth/CSD multiplier would still beat 12.56ns (M5 stands).
3. **Screen coverage delta (M7)** — scenarios GRAY/UPSTREAM/BYTE-REP/SPARSE-HD/
   PTR-RAND/SMALL-INT and ≥32-key coverage were never run; Fisher-dependence
   never calibrated. Either run them or keep the "screening evidence" wording.
4. **Dieharder** (m1) — not installed; low signal given two decisive battery
   failures. Install only if a future candidate passes PractRand+TestU01.
5. **Fanout-penalty sensitivity** (M4) — DONE during remediation. Re-ran the
   exact longest-path analysis on the same-run mapped netlists with a fanout
   penalty k added per unit fanout (`/tmp/analyze_fo.py`):
   k=0 → 40.0/50.8 = **0.787** (reproduces claim); k=0.1 → 0.828; k=0.2 →
   0.858; k=0.3 → 0.891; k=0.5 → 0.934. The DUT degrades faster (+27% at
   k=0.1) than the reference (+21%), confirming the asymmetric fanout exposure.
   Even a modest penalty (k=0.1–0.2) moves the honest ratio to ~0.83–0.86;
   the 0.787 figure is the optimistic end of the range.
6. **Numpy-vs-C differential cross-check at scale** (m2 done at 3 vectors) —
   RESOLVED by controlled experiment (numpy, independent code path):
   δ=2¹⁸ sequential → output bit 20 flip bias −0.0650 (z=−133 at N=2²⁰),
   same delta random-input → bias −0.0092 (z=−27 at N=2²¹). I.e. sequential
   inputs (the deployment distribution) AMPLIFY the bias ~7× vs random; and
   the dependence goes both ways (δ=2⁴²: quiet under sequential, z=25 at
   bit 44 under random). Differential biases are input-distribution-dependent;
   the deployment distribution is the loud one for the strongest differentials.

## 5. Verdict

`r3_xorlin_qm` remains the round-3 winner: functionally correct (RTL PASS),
genuinely under the delay bar (9.7% margin in the screening model, and 0.47×
the ABC-mapped multiplier in a matched-utilization Sky130 GR-STA A/B —
better than the 0.787 screening ratio), CAL_PASS as screening evidence,
1-cycle pipeline verified. The peer review downgraded three narratives to
honest versions — P&R numbers and routing story, the statistical wording,
the silicon meaning of 0.787× — and surfaced one genuinely new technical
fact: strong key-independent differential structure (M9) that the screen
never probed and that bounds the design's adversarial claims. Nothing in the
review changes the Pareto position for the non-adversarial hash-map use;
everything in it constrains what may be claimed and what round 4 must do better.
