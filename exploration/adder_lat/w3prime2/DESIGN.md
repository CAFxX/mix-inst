# W3'' co-design — cheap-linear-diffusion word-AND (2026-10-12)

## Cost thesis (from `adder_lat/w3prime/COST_AUTOPSY.md`)

W3' is 48u because 3 GF(2^64) constant multiplications are ~85–90% of the
cost. The AND layers (the entire nonlinearity budget) are ~10%. Cost is
schedule-independent (±2.5% across 4 schedules) — **arm (a), a bigger
screen of the GF form, is rejected**: no schedule can be meaningfully
cheaper. The GF multiplier is LINEAR (O93); its S1-LIN role is rank
contribution. A cheaper linear diffusion preserves the nonlinearity budget
while attacking ~90% of the cost.

## Form

```
x = v ^ k
repeat 3 stages:
    x ^= (rotl(x,a1) & rotl(x,b1))     # d-constrained ANDs (unchanged)
    x ^= (rotl(x,a2) & rotl(x,b2))
    x ^= rotl(x,p) ^ rotl(x,q)          # cheap linear diffusion (NEW: was gf_mul(x,P))
x ^= rotl(k,13)
```

- AND pairs: d=(b−a) mod 64 ∈ {1,2,3,4,5,59,60,61,62,63}, enforced at
  generation (same as W3').
- (p,q): drawn per candidate, p,q ∈ {1..63}, p≠q. Joint search, honestly
  triaged — no hand-picked "good" rotations.
- Pre-whiten / final key fold unchanged from W3'.

## Mechanism re-check (not assumed)

1. Sequential-affinity pre-check per AND: `and_layer_rank(a,b) ≥ 8`
   (unchanged — AND layers are identical to W3').
2. **Full-rank probe on the NEW form**: 64 sequential inputs, fixed key,
   rank ≥ 62. The linear layer changed, so O93's rank-63 result does NOT
   transfer — measured per candidate, hard gate.
   - **Refinement found 2026-10-12 (smoke test, al_w3p_a schedule):** the
     cheap linear's rank is (p,q)-DEPENDENT: (29,36)→57, (17,42)→55,
     (7,53)→58, (1,32)→60, but (57,1)→63. Grid search over (p,q) finds
     rank-63 choices for both 3-term and 4-term forms. This is WHY (p,q) is
     drawn per candidate and rank-gated, rather than fixed: the probe
     discriminates good linear diffusions from bad ones. The GF mult is
     load-bearing for rank *in the dense form*, but a well-chosen sparse
     linear layer also reaches 63.
3. Fisher triage via `lin_diff.screen_lin_diff` verbatim (the S1 gate's own
   rule): KEEP iff LIN PASS **and** DIFF PASS (0 Holm rejections on both
   families). Stricter than b57's DIFF-only — appropriate because the
   changed linear layer is exactly what LIN rank depends on.

## Calibration (before the screen)

- Canary gate: `triage_core.check_canaries()` (same as W3').
- Positive control: al_w3p_a (S1-clean, full battery+Q1 pass) under the
  Fisher triage → expect KEEP (0 rejections). Validates the instrument on
  the word-AND family. (Instrument was validated on muxD5f in b57; this
  checks it transfers.)

## Screen parameters

- N=300 schedules, seed 0x5EED2 (valid hex — cf. the 0xW3E4 incident).
- JSONL checkpoint per candidate, resume by regenerating the stream.
- Draw-loop fail-loud cap 10000 (b45 lesson).
- Heartbeat every 25 to `adder_lat/supervisor_heartbeat.txt`.

## Pre-registered escalation (no mid-flight judgment)

- ≥1 KEEP → bundle top keeps by (n_reject=0, then min worst|z|), preferring
  distinct (p,q): bit-exact bundle (model==screen 2000 vec × 3 keys,
  C==Python, goldens) → S0 via authorized `run_synth.py`.
- **S0 < 30u** (≥38% cheaper than W3' 48u) → staged battery S1→S2→S3→S4→Q1.
- S0 ≥ 30u → structural thesis failed: record verdict, pre-registered
  fallback is (b2) sparse-GF (one GF mult at end, cheap linear between
  stages) — co-designed then, not now.
- 0/300 KEEP → close the cheap-linear variant with the kill signature;
  (b2) becomes the next arm.

## Explicit non-goals

- Arm (a) rejected (see autopsy). Not revisited without new evidence that
  cost varies with schedule.
- Fewer than 3 stages: contraindicated by O93 (2 effective stages → rank 44).
- Changing the AND structure: the d-constraint is the proven nonlinearity
  budget; not touched.
