# Wave-14: word-level non-bit-sliced fused structures (WFS)

Opened 2026-10-11 01:05 CEST by the track-3 supervisor (respawn). Queued since
the 2026-10-10 22:32 CEST ledger entry ("track-8 re-test trigger (c),
word-level non-bit-sliced fused structures").

## Why this axis

Every sub-21u construction to date is **bit-sliced**: 64 parallel 1-bit
nonlinearities (`x ^= (ra&rb)^rc`). Track-6's autopsy: the S1-DIFF wall is a
*deterministic differential skeleton* surviving to the output (mode 1), or
catastrophic bias without determinism (mode 2). Bit-sliced AND is delay-cheap
(3.35u/stage) but needs 6 stages for quality → the floor is 19.8u (t6_b33c).

Word-level ops (adds, multiplies, GF(2^64) linear maps) mix **whole words per
operation** — fewer, denser stages. North star: bare 64-bit add delay A64
(calibrating in work/calib.json); "adder-like" = full quality within ~1.5× A64.

## Families

**W1 — narrow-lane carry-fused ARX (flagship).** 4×16-bit lanes.
```
x ^= k
repeat r:
    li = li + rotl16(l[(i+1)%4], a_i) + C_i      # 16-bit 3-op add, word-level
    (l0..l3) = laneperm(l0..l3)                    # wiring
    x = concat(lanes); x ^= rotl64(x, b_i)        # full-word linear mix
x ^= rotl64(k, 13)
```
Cost/stage ≈ A16 + XOR64 ≈ 5.5u → 3 stages ≈ 16.5u < 19.8u. Adds have no
deterministic DIFF skeleton; failure mode is carry-run concentration —
adjudicated by the triage, with rotation schedules (a_i, b_i, perm) as the
co-design knob (b33 playbook).

**W2 — full-word CSA-fused add chain** (contingent: calibration must show
Yosys inferring CSA for 3+/4-op adds, i.e. add3 ≈ add64 + ~2u).
```
x ^= k
repeat: x = x + rotl(x,a_i) + C_i
        x ^= rotl(x,b_i)
x ^= rotl(k,13)
```

**W3 — GF(2^64)-diffused word-AND** (contingent: gf64 cost affordable).
```
x ^= k
repeat: x ^= (rotl(x,a_i) & rotl(x,b_i))
        x = gfmul64(x, P_i)        # GF(2^64) x const, reduction x^64+x^4+x^3+x+1
```
Hypothesis: a perfect-diffusion (branch-65) linear layer kills the
deterministic-skeleton *survival* mode structurally — every output bit is a
XOR of ~32 skeleton bits. The triage adjudicates; no claim made.

**W4 — narrow-multiply fused** (contingent: mul16 < ~8u).
`li = li + l[(i+1)%4] * K_i` etc.

## Co-design rules (from autopsies, non-negotiable)

1. **DIFF wall**: rotation-schedule co-design via the exact-DIFF triage —
   never blind schedules (b33 playbook: the method is the differentiator).
2. **Subspace collapse** (track-8 wave-34): triage PRIMARY on sequential
   inputs (the S1-DIFF methodology, harsh domain), SECONDARY on random-64;
   report both, KEEP requires the sequential bar.
3. **No linear cross-terms** creating deterministic skeletons (wave-34 V0
   lesson): every cross-lane influence passes through a nonlinear op.
4. **Cost-eligibility before escalation**: estimated delay < 19.8u.
5. **Positive controls on every gate** (standby rule).

## Pipeline

0. **Calibrate** word-op costs — run_calib.py, 9 primitives via the authorized
   run_synth.py (pinned Yosys 0.69, analyze==analyze2 XCHECK). → work/calib.json
1. **Triage harness** — triage_core.py: exact-DIFF via lin_diff.diff_cell_logps,
   10 keys, KEEP bar max|z|<10. Canary gate FIRST: as6_200_106 must KILL
   (z=71.4), al_and6a + t6_b33b must KEEP (z~3.0). No candidate trusted until
   the harness reproduces all three.
2. **Screen** W1 schedules (both domains) → KEEPs.
3. **S0** for cost-eligible KEEPs (single-stage cost probe first, then full).
4. **Staged battery** S1→S4+Q1 for S0 survivors (b33 playbook).

## Family selection verdicts (2026-10-11 ~03:10 UTC, on work/calib.json)

Calib (ref mul64 103.5u): add64=82.3u, add32x2=43.4u, add16x4=23.0u,
add3=94.4u (+12.1u/op), add4=101.3u (+19.0u), mul16=51.9u, mul32=92.2u,
mulc64=87.0u, gf64=15.9u. Bars: frontier 19.8u; adder-like 1.5×A64=123.4u.

- **W1 narrow-lane carry-fused ARX: COMMIT** (flagship, adder-like mission).
  The doc's "~5.5u/stage → 3st≈16.5u<19.8u" math is FALSIFIED — measured
  A16=23.0u, not ~4u (carry chain dominates; narrow lanes don't save delay).
  Revised: stage ≈ 27–29u (3-op 16-bit = 23.0u + CSAε) or ≈24–25u (2-op +
  xor const); 2st ≈ 50–58u, 3st ≈ 81–87u ≈ 1.0×A64. All < 123.4u; none
  < 19.8u. The sub-frontier flagship rationale is dead; the adder-like
  rationale holds — 3 stages at ~1.0× the bare-add delay is genuinely
  "adder-like". → DIFF screen of rotation/laneperm/const schedules.
- **W2 full-word CSA-fused add chain: KILL (cost-terminal).**
  CSA *is* fused (+12.1u/op, not +82.3u chained) but far above the doc's
  +~2u hope; stage ≈ 96u → 2st ≈ 192u > 123.4u. Even ideal hand-CSA
  (≥A64+ε ≈ 85u/stage) gives 2st ≈ 170u > bar; 1 stage implausible for
  DIFF. No achievable configuration meets any bar. Terminal.
- **W3 GF(2^64)-diffused word-AND: COMMIT** (perfect-diffusion lead).
  gf64=15.9u is cheap; stage ≈ 17–18u (AND + GF); 2st ≈ 35u, 3st ≈ 53u —
  0.28–0.43× A64, < 123.4u. Cannot beat 19.8u (1st ≈ 18u < bar, but one
  nonlinear layer cannot pass DIFF — structural). The perfect-diffusion
  hypothesis (branch-65 linear layer kills skeleton *survival*) is a
  genuinely new structural bet against the DIFF wall. → screen.
- **W4 narrow-multiply fused: KILL (contingency failed).**
  mul16=51.9u vs the <8u bar — 6.5× over. Terminal.

Reframing: wave-14's mission is the **adder-like bar (123.4u)**, not the
19.8u frontier — calib proves no W-family stage is cheap enough for a
sub-frontier win (cheapest stage: W3 ≈ 18u, still needs ≥2 stages for
DIFF). Cost-eligibility for S0 escalation: estimated full delay < 123.4u.

## Status

- 2026-10-11 01:05 CEST: opened; calibration worker launched (tag
  track3/w14-calib). Awaiting work/calib.json.
- 2026-10-11 01:18 CEST: **triage harness positive controls PASS**
  (triage_core.py): as6_200_106 → seq z=71.4 killkey=0x0 KILL (reproduces the
  recorded 71.4 exactly); t6_b33b → seq z=3.0 KEEP (exact); al_and6a → seq
  z=3.2 KEEP. Harness reproduces track-6's exact-DIFF numbers bit-for-bit —
  trusted for candidate screening.
- **Wave-34 lesson confirmed in the canary data**: as6_200_106 is rnd64-clean
  (z=2.5) but seq-killed (z=71.4) — the DIFF wall is invisible on random-64
  inputs. Sequential domain stays the PRIMARY gate; random-64 is reported,
  never trusted alone.
