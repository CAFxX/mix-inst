# W4T DESIGN — 4-term rotl-xor linear diffusion (track-3 arm, 2026-10-12)

## Cost thesis (quantitative)

Delay model, calibrated from raw S0:
- W3' 48.3u: 3 stages x (2 AND-layers x 2lv + GF XOR-tree ~5.5lv) = ~28.5 levels
  -> ~1.7u/level.
- b2sparse 34.9u: 3x(2x2) AND + 2x(2lv) linear + 1x(5.5lv) GF = ~21.5 levels
  -> ~1.6u/level.
- Consistent: **~1.65u per gate level.**

Per-operation depth:
- AND layer `x ^= (rotl(x,a) & rotl(x,b))`: AND(1) + XOR(1) = 2 levels.
- 2-term linear `x^rotl(x,p)^rotl(x,q)`: 2 XORs = 2 levels.
- **4-term linear `x^rotl(x,p)^rotl(x,q)^rotl(x,r)^rotl(x,s)`: 3 XORs in
  tree = 2 levels.** Same depth as 2-term, 2x the mixing per stage.
- GF(2^64) const-mult (popcount~29): ~5.5 levels.

W4T estimate: 3 stages x (2 AND-layers x 2lv + 4-term linear 2lv)
= 3 x 6 = **18 levels x 1.65u = ~30u.**

This is BORDERLINE vs the strict <30u bar. The estimate is honest, not
optimistic: S0 (yosys) is the ground truth. If S0 < 30u and S1-clean,
escalate. If S0 30-35u, the arm is COST-MARGINAL (record, do not escalate
to full battery — b2sparse precedent O128). If S0 > 35u, COST-CLOSED.

**What W4T attacks:** the GF multiplier's 5.5 levels/stage (16.5 of 28.5
total in W3'). Replacing it with a 2-level 4-term linear removes ~10.5
levels (~35% depth reduction). The AND layers (the nonlinearity budget)
are untouched.

## Quality thesis (addresses the O127 kill mechanism)

O127 killed 2-term linear on DIFF (19/19 survivors lin=PASS/diff=FLAG).
The kill was in DIFFUSION QUALITY: 2-term gives each output bit ~2 input
dependencies; after 3 stages ~2^3 = 8 dependency bits — too sparse to
diffuse.

4-term gives each output bit 4 input dependencies; after 3 stages
~4^3 = 64 — full-word dependency. This is 8x denser diffusion at the
SAME depth (2 levels) and nearly the same gate cost (192 vs 128 XOR2).

The O127 verdict explicitly left 4-term untested ("NOT about other
cheap-linear forms (4-term rotl-xor...)"). This arm is the direct
follow-up: it tests whether DENSER cheap-linear diffusion survives the
Fisher DIFF gate where sparse 2-term failed.

**Explicit risk:** 4-term may still fail DIFF (the GF mult's diffusion may
be qualitatively different, not just denser). If 4-term dies on DIFF,
the next arm is GF-at-middle + 4-term linear (GF provides the diffusion
the pure-linear form lacks).

## Form per candidate

  x = v ^ k                                    (pre-whiten)
  3 stages:
    2 d-constrained ANDs (d in {1..5,59..63})   (nonlinearity, unchanged)
    x ^= rotl(x,p) ^ rotl(x,q) ^ rotl(x,r) ^ rotl(x,s)   (4-term linear)
  x ^= rotl(k,13)                              (post-whiten, unchanged)

(p,q,r,s): 4 distinct non-zero rotations, drawn per candidate.

## Gates (all must pass for KEEP)

(a) Sequential-affinity pre-check: and_layer_rank >= 8 per AND
    (unchanged from W3'' — the AND layers are identical).
(b) Mechanism re-check: full 64-seq GF(2) rank >= 62 on the NEW 4-term
    form. The (p,q) rank-dependence from W3'' (fr 44-63) must be re-probed
    for (p,q,r,s) — never assumed.
(c) Fisher triage: lin_diff.screen_lin_diff verbatim (S1 gate's own rule).
    KEEP iff LIN PASS and DIFF PASS (0 Holm rejections, both families).

Calibration (non-vacuity):
- Canary gate: check_canaries() must PASS.
- Positive control: al_w3p_a (S1-clean, full battery+Q1) must KEEP under
  the Fisher triage on its own model (validates the instrument).

## Pre-registered escalation

- Screen N=300, seed 0xW4T (see script). JSONL checkpoint, resumable.
- If keeps >= 1: bundle bit-exact (model==screen, C==Python, RTL==model),
  S0 via run_synth.py.
- S0 bar: **<30u strict** for full-battery escalation.
  - <30u + S1-clean: full battery + Q1 (the prize).
  - 30-35u: COST-MARGINAL — record verdict, do NOT escalate (b2sparse
    precedent: 34.9u was COST-CLOSED).
  - >35u or 0 keeps: arm CLOSED (quality or cost, per the gate that
    fired).
- If 4-term dies on DIFF (like 2-term): record O-number, next arm is
  middle-GF + 4-term (pre-registered contingent).

## Why NOT middle-GF standalone (axis 2)

A single GF mult at the middle has the SAME cost as b2sparse's GF at the
end (~1 GF = 5.5 levels; total ~21.5 levels -> ~35u). It does not beat
the <30u bar — no cost thesis. Running it standalone would be theater
(same ~35u as the COST-CLOSED b2sparse). It becomes relevant ONLY as a
diffusion-booster combined with 4-term IF pure-4-term fails DIFF.

## References

- Cost autopsy: [COST_AUTOPSY.md](../w3prime/COST_AUTOPSY.md)
- O127 (2-term quality kill): VERDICT_SCOPE.md
- O128 (b2sparse cost close): VERDICT_SCOPE.md
- W3'' screen methodology: [screen_w3pp.py](../w3prime2/screen_w3pp.py)
