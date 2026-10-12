# track2-het8 — 8-bit AES-class box as single hetero stage in non-SPN frame

**Status:** TERMINAL — VERDICT O130 (2026-10-12 10:45 CEST). Pilot 0/36 fisher-keeps
(seed 0xB801), min worst|z|=43,518. K1 fired at triage: single 8-bit hetero box
is STRUCTURALLY dead — for input deltas 2^k, k≥8 the low-byte box is transparent
and XOR4+MUXD propagate single-bit high deltas deterministically (point-mass
dx_low8, z≈740k); identity-box control byte-identical (box contributes nothing);
coverage argument: 1 box covers 1/8 of the 64-bit delta space, an independently
DIFF-clean frame (≈30u with box) is arithmetically dead vs 18.6u, multi-box =
SPN = O129-closed. S0 moot, no bundle built. Full evidence: pilot.log,
pilot_keeps.jsonl (empty), LEADS_LEDGER.md O130 entry. Next axis proposed in
ledger: pool of cheap non-S-box hetero stage types in MU5 frame (broad GHA).
**Parent verdict:** O129 — 8-bit SPN COST-CLOSED (box floor 10.4u → 2r SPN ≥ 20.8u > 18.6u).
This lane tests the OPEN LEAD: the same box as a SINGLE hetero stage, co-designed, not blind-swapped.

## 1. Co-design (pre-registered, falsifiable)

**Frame:** MU5 verbatim (pre-whiten `x ^= k`; final `x ^= rotl(k,13)`). Stage types:
`BOX8` (one 8-bit AES-class box on bits[7:0], identity elsewhere),
`XOR4` (5-term circulant `x ^= ra^rb^rc^rd`, bijective for any distinct taps —
p(1)=1 ⇒ gcd(p,(z+1)^64)=1, b48 machinery),
`MUXD` (`x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)`, measured ~3.86u).

**Position thesis:** the box belongs at the INPUT (position 0, right after whiten).
Rationale: the box reads only 8 bits no matter what precedes it, so pre-box
diffusion stages are wasted on the box itself; what matters is post-box
diffusion of its 8 strongly-nonlinear output bits to all 64. Placing it last
wastes the post-diffusion (only `x^=rotl(k,13)` follows) → avalanche must fail.
Defensible cut: test p∈{0,1}; exactly one p=2 control draw to prove the
argument empirically.

**Surrounding width thesis:** the box's DU=4/NL=112 nonlinearity replaces ~2
MUXD stages' nonlinear budget. Testable claim: `T1=[BOX,XOR4,MUXD]` (~10.4+4.0+3.9
≈ 18.3u) fisher-passes. If quality needs ≥4 stages, the cost arithmetic kills
the speed thesis with the mechanism recorded.

**Byte lane:** fixed to low byte (bits[7:0]). No principled reason prefers another
lane (rotl mixing is uniform). Lane sweep is a pre-registered FOLLOW-UP axis,
only if the thesis is otherwise supported.

**Affine fusion:** AFF8 variants carry their 8×8 affine maps inside the measured
10.4u (pure-inversion control = 10.4u proves no cheaper AES-class form exists).
No extra affine cost in the frame. Primary box AFF8_06 (cheapest, 10.4u);
alternates AES_SBOX (10.7u), AFF8_03 (10.4u).

**Cost thesis (falsifiable at S0):** box 10.4u + XOR4 ~4.0u + MUXD ~3.9u ≈ 18.3u
< 18.6u strict speed bar.

## 2. Pilot templates (≤40 draws)

| T | stages | role |
|---|---|---|
| T1 | [BOX(0), XOR4, MUXD] | primary, cost-viable |
| T2 | [BOX(0), MUXD, XOR4] | order variant |
| T3 | [XOR4, BOX(1), MUXD] | box middle |
| T4 | [BOX(0), XOR4, XOR4, MUXD] | quality-needs-more probe (cost-doomed if only this keeps) |
| T5 | [BOX(0), XOR4, XOR4] | box-only nonlinearity control |
| T6 | [XOR4, MUXD, BOX(2)] | late-box diffusion control (1 draw) |

7 draws per template (T1–T5) + 1 T6 = 36 draws. Per draw: box ∈
{AFF8_06×4, AES_SBOX×1, AFF8_03×1}; XOR4 taps 4 pairwise-distinct ∈ 1..63
(fail-loud); MUXD s,a,b pairwise-distinct ∈ 0..63, d ∈ 0..63 (degenerate-mux
guard verbatim).

## 3. Gates (verbatim instruments)

- **Fisher:** KEYS10 (screen_lib KEYS[:10]), N=2^18, `diff_cell_logps`,
  `holm_reject` ALPHA=0.01 → KEEP iff n_reject==0.
- **Inner (keeps only):** `screen_lin_diff` on 2^17-pair full-range sequential
  outputs, keys 0xffffffffffffffff + 0xaaaaaaaaaaaaaaaa (batch-62 calibration) →
  lin_verdict==PASS ∧ diff_verdict==PASS.
- **Calibration:** CALIB-1 b33c z=3.3 exact reproduction (verbatim xorh5);
  CALIB-2 negative control (linear-4) → REJECT (non-vacuity).

## 4. Kill rules (pre-registered)

- **K1:** 0/30+ fisher-keeps on cost-viable templates (T1,T2,T3,T5) → SPEED THESIS
  KILLED at triage → O-entry (scoped to tested frames). Record whether T4 kept
  (mechanism = quality needs ≥4 stages).
- **K2:** ≥1 keep → bundle + S0 (run_synth.py authorized path, strict <18.6u,
  XCHECK clean). S0 ≥ 18.6u → COST-CLOSED (speed axis). Size-axis fallback ONLY
  if cells ≪ 5,833 (t6_xorh5_15 cells point); else full kill.
- **K3:** inner gate flags all keeps → KILLED, mechanism recorded.

## 5. Escalation on support

keep → bundle (BOX8 stage in bundler, bit-exact 2000/200 + iverilog 200/200) →
S0 → XCHECK → staged battery S1–S4 → Q1 (sac_z5=0) → GHA full campaign spec
(CAFxX/fanout, mix-sbox-search tenant, PAT push). Box emitter dual-canary check:
AES_SBOX case form synthesizes ≈10.7u in the same VM flow (mirrors GHA canary).
