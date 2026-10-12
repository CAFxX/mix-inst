# XIG Variants A & B — Empirical Fisher Verification

**Date:** 2026-10-12
**Directive:** Carlo — XIG A/B were killed by theoretical proof (O155, from Variant C degree-4)
without empirical testing. For 3.2x-frontier candidates (5.8u vs 18.6u), proof alone is a
process violation. This file records the empirical `lin_diff.screen_lin_diff` verbatim results.

## Protocol

- `lin_diff.screen_lin_diff` verbatim, imported from
  `/home/hatch/workspace/mix/exploration/fast_battery/src`.
- Input: N=2^18 sequential outputs, single cell (key=0). XIG is keyless, so no key whitening.
- Variant A: `fisher_triage_a.py` (new, mirrors B's protocol); vectorized `F_batch` cross-checked
  against scalar `make_f` on 2000 random inputs × P1/P2/P3 — all MATCH.
- Variant B: existing `fisher_triage.py` in `xig-varB/xig/`, run verbatim.
- All commands under `nice -n 10`.

## Variant A (5.8u S0, degree 2, g_i = XOR of 4 AND2, 8 inputs, bijective 10M/0-collision)

| Pattern | LIN verdict | LIN D/4096 | LIN logp | DIFF verdict | DIFF worst|z| | DIFF fisher_logp |
|---------|-------------|------------|----------|--------------|------------|------------------|
| P1 | FLAG | 4096 | -inf | FLAG | 739994.3 | -inf |
| P2 | FLAG | 4096 | -inf | FLAG | 1480000.0 | -inf |
| P3 | FLAG | 4096 | -inf | FLAG | 739994.3 | -inf |

## Variant B (8.2u S0, degree 2, g_i = XOR of 8 AND2, 16 inputs, bijective 10M/0-collision)

| Pattern | LIN verdict | LIN D/4096 | LIN logp | DIFF verdict | DIFF worst|z| | DIFF fisher_logp |
|---------|-------------|------------|----------|--------------|------------|------------------|
| P1 | FLAG | 4096 | -inf | FLAG | 739994.3 | -inf |
| P2 | FLAG | 4096 | -inf | FLAG | 1480000.0 | -inf |
| P3 | FLAG | 4096 | -inf | FLAG | 1480000.0 | -inf |

(Note: B's `fisher_triage.py` prints verdict lines to stdout rather than JSON; the three lines
above are verbatim from the run log. A's per-pattern JSONs are in the A worktree.)

## Raw artifacts

- A: `~/workspace/worktrees/mix/xig-varA/xig/xig_a_fisher_p1.json`,
  `xig_a_fisher_p2.json`, `xig_a_fisher_p3.json`
  (+ `fisher_triage_a.py`, the verbatim-protocol script written for this verification)
- B: stdout logs from `~/workspace/worktrees/mix/xig-varB/xig/fisher_triage.py`
  (P1/P2/P3); B's script does not write JSON, verdict lines captured in run logs.

## Verdict

**O155's theoretical kill is CONFIRMED empirically.** All 6 (variant, pattern) combinations fail
catastrophically on both LIN (D=4096/4096 — every output bit linearly dependent, the maximum
possible failure) and DIFF (worst|z| ~7.4e5–1.5e6, fisher_logp=-inf).

The degree bound is not just a proof — it is measured. No offset pattern (structured P1/P2 or
random P3) escapes it. Variants A and B are KILLED empirically, not just theoretically.

**What survives:** the XIG *construction* (f_i = x_i ⊕ g_i) is validated as a fast bijective
primitive family — 5.8u/8.2u, 10M-pair bijectivity on all patterns. The blocker is purely the
degree (≤2 here, ≤4 in Variant C) vs Fisher's degree-≥5 requirement. A degree-≥5 XIG under 10u
remains the open re-test trigger from O155.
