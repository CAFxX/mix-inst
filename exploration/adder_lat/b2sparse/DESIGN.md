# (b2) sparse-GF word-AND co-design — 2026-10-12

## Cost thesis (from O127: the W3'' cheap-linear kill)

The cheap-linear arm (b1) is QUALITY-CLOSED: 19/19 Fisher-triage survivors
were DIFF-killed with LIN PASS. The (p,q) rank probe discriminated rank
(24 rank kills, one rank-63 draw) but even rank-63 draws died on DIFF — the
kill is in DIFFUSION QUALITY, not linear rank. The GF(2^64) multiplier is
load-bearing for diffusion, not just rank. So the next structural variant
keeps ONE GF mult but moves it to the END of the pipeline, with cheap
linear diffusion between stages.

Cost estimate (structural, from the O123 autopsy): W3' = 3 GF mults ≈
85–90% of cost (each GF const-mult ≈ 2,200 XOR2-equivs) + AND layers ≈ 10%.
(b2) = 1 GF mult + same AND layers → ≈ 1/3 of the GF cost → projected
~20–25u (vs W3' 48u). The final single GF mult is the diffusion backstop
(O93: "GF(2^64) carries diffusion") — stages 1–2 rely on cheap linear
between stages, which is the explicit risk carried from O127.

## Form

```
x = v ^ k
repeat 3 stages:
    x ^= (rotl(x,a1) & rotl(x,b1))     # d-constrained ANDs (unchanged)
    x ^= (rotl(x,a2) & rotl(x,b2))
    x ^= rotl(x,p) ^ rotl(x,q)          # cheap linear diffusion (rotl-xor form)
x = gf_mul(x, 0x94D049BB133111EB)       # ONE GF(2^64) mult at END (was: per stage)
x ^= rotl(k,13)
```

- AND pairs: d=(b−a) mod 64 ∈ {1,2,3,4,5,59,60,61,62,63}, enforced at
  generation (same as W3', W3'').
- (p,q): drawn per candidate, p,q ∈ {1..63}, p≠q. Joint search, honestly
  triaged — no hand-picked "good" rotations.
- P constant FIXED at 0x94D049BB133111EB (al_w3p_a's P: rank-63, full
  battery+Q1 pass). The P cut is defensible, not a narrowing-by-convenience:
  (1) the GF mult is a fixed linear bijection (P odd → invertible), so its
  diffusion contribution is P-independent in quality terms; (2) O98 shows
  three P constants all reaching full battery+Q1 — quality does not vary
  with P; (3) P's cost varies only with popcount (wire-level), and the
  search axis is the (a,b,p,q) schedule space, not the constant. A per-draw
  P would mix two independent axes with no mechanism for P×schedule
  interaction.
- Pre-whiten / final key fold unchanged from W3'/W3''.

## Mechanism re-check (not assumed)

1. Sequential-affinity pre-check per AND: `and_layer_rank(a,b) ≥ 8`
   (unchanged — AND layers are identical to W3'/W3'').
2. **Full-rank probe on the NEW form**: 64 sequential inputs, fixed key,
   rank ≥ 62. The linear layer is the W3'' form (not GF), and the final GF
   mult is a GF(2) bijection, so rank behavior follows the W3'' smoke test:
   (p,q)-DEPENDENT — this is WHY (p,q) is drawn per candidate and
   rank-gated, never fixed. The probe discriminates good linear diffusions
   from bad ones, per the O127 evidence.
3. Fisher triage via `lin_diff.screen_lin_diff` verbatim (the S1 gate's own
   rule): KEEP iff LIN PASS **and** DIFF PASS (0 Holm rejections on both
   families). The gate that killed the cheap-linear arm unchanged — no
   instrument tuning between the kill and the follow-up.

## Calibration (before the screen) — fail-loud

- Canary gate: `triage_core.check_canaries()` (same as W3'/W3'').
- Positive control: al_w3p_a (S1-clean, full battery+Q1 pass) under the
  Fisher triage → expect KEEP. Validates the instrument on the word-AND
  family (same as W3'').
- **(p,q) discrimination self-check on the b2 form** (transfers the W3''
  smoke-test finding, measured on THIS form before screening): known-bad
  (29,36) must probe fr < 62; known-good (57,1) must probe fr = 63. If
  either fails → the rank probe is not discriminating on the b2 form →
  ABORT, do not screen.
- Any calibration failure aborts with exit 2 (never proceeds silently).

## Screen parameters

- N=300 schedules, seed 0xB200 (fresh seed — a new form, not the W3'' stream).
- JSONL checkpoint per candidate, resume by regenerating the stream.
- Draw-loop fail-loud cap 10000 (b45 lesson).
- Heartbeat every 25 to `adder_lat/supervisor_heartbeat.txt` (tag b2sparse).
- Backoff-gated launch (cleared-flag single-gate pattern), `setsid` +
  `agentwork-launch.sh --nice 19 --tag track3/b2sparse-screen`.
- Work-registry entry `track3-b2sparse` (register at launch, heartbeat,
  mark done on completion).

## Pre-registered escalation (no mid-flight judgment)

- ≥1 KEEP → bundle the top keep (n_reject=0, then min worst|z|; preferring
  distinct (p,q)): bit-exact bundle (model==screen 2000 vec × 3 keys,
  C==Python, goldens) → S0 via authorized `run_synth.py`.
- **S0 < 30u** (≥38% cheaper than W3' 48u) → staged battery S1→S2→S3→S4→Q1.
  Q1 sac_z5=0 is mandatory for any frontier claim.
- S0 ≥ 30u → the sparse-GF cost thesis failed: record the verdict with the
  measured number; re-test trigger: synthesis-path change or P-constant
  exploration. Close.
- 0/300 KEEP → close the sparse-GF variant with the kill signature (same
  form as O127: verdict breakdown + calibration evidence + what narrowed);
  record the next re-test trigger. The lead then moves to genuinely new
  axes (4-term linear between stages, or GF mult at a middle position —
  co-designed then, not now).

## Explicit non-goals (carried from W3'' DESIGN.md — still hold)

- Arm (a) rejected (O123). Not revisited without new evidence that cost
  varies with schedule.
- Fewer than 3 stages: contraindicated by O93 (2 effective stages → rank 44).
- Changing the AND structure: the d-constraint is the proven nonlinearity
  budget; not touched.
- No second GF mult inside the pipeline (that is the W3' form already
  tested — O98). The distinguishing question of (b2) is exactly one GF at
  the end.
