# W3' screen pre-check strictness — finding 2026-10-11 ~21:00 CEST

## Finding

The screen's sequential-affinity pre-check (`and_layer_rank`, reject if rank < 8)
is STRICTER than the triage spec's "assert NO AND is affine".

`and_layer_rank(a,b)` = GF(2) rank of the 64 output VALUES of
g(x) = x ^ (rotl(x,a) & rotl(x,b)) on V = 0..63 (64 sequential inputs).

Measured on d-constrained (a,b) (all d in {1..5,59..63}):
- d = +/-5 (single-bit interval intersection): rank 6 or 7, depending on
  whether the lone quadratic term lands on its own output bit (rank 7,
  e.g. (40,35)) or shares an output bit with a linear term (rank 6,
  e.g. (60,1)).
- Truly affine (d in {6..58}): rank 6 on V=0..63 (all constants zero out).

So the rk<8 threshold rejects ALL d=+/-5 ANDs plus d in {+/-1..+/-4} whose
quadratic terms align poorly. A d=+/-5 AND is NOT affine (it carries a genuine
quadratic term x_j*x_k) — it is merely WEAK (0-1 extra dimensions).

## Why this is acceptable (not a bug to fix mid-screen)

1. The W3_LIN_MECHANISM.md decisive experiment that PROVED the form used
   d in {1..4} — the strict subset. The screen enforces (a superset of) the
   validated configuration.
2. The full-rank probe (>= 62) remains the real S1-LIN safety gate; the
   pre-check is a cheap filter, and filtering toward MORE quadratic terms
   per AND is the safe direction.
3. The 2 KEEPs so far (idx 18/19) passed the strict filter — they are the
   strongest LIN-robustness candidates, not compromised ones.

## Consequence

The screen tests an effective d in {+/-1..+/-4}-with-good-alignment subset,
not the full DSET {+/-1..+/-5}. If the parent wants the looser spec-literal
screen (rk<7, d=+/-5 admitted), that is a FOLLOW-UP screen, not a fix —
do not invalidate the 25 completed entries / 2 KEEPs mid-run.

Observed pre-check pass rate ~8% (2/25 reach triage); expect ~12-20 of 200
to reach the DIFF triage + rank probe stages.
