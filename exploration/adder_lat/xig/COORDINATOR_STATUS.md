# XIG Coordinator Status

**Started:** 2026-10-12 ~15:07 CEST
**Coordinator:** track-3 XIG (x_i XOR g_i) construction

## Dispatched workers

| Variant | Worker ID | Status |
|---------|-----------|--------|
| A (2-level, 8 inputs, 6.4u) | 81286ec5-... | Dispatched, pending_init |
| B (2-level, 16 inputs, 8.2u) | 44ccd5e5-... | Dispatched, pending_init |
| C (3-level, degree 4, 6.4u) | b080d09a-... | Dispatched, pending_init |

## Pipeline per worker

1. Claim worktree via wt.py
2. Write Verilog generator
3. For P1, P2, P3: S0 measure → bijectivity sampling (1M, then 10M)
4. Report results

## Next (coordinator, after workers complete)

1. Collect S0 + bijectivity results from all 3 variants.
2. For bijective + <10u candidates: run Fisher triage (`lin_diff.screen_lin_diff`).
3. Record verdicts in VERDICT_SCOPE.md (O149+).
4. Update LEADS_LEDGER.md.
5. Report DONE to parent with full synthesis.

## Variant C complete (2026-10-12 ~15:45 CEST)

**Result:** All 3 patterns 6.4u, bijective (10M sampling), but Fisher FAILS structurally.

**Key proof from worker:**
- LIN: Degree-≤4 maps on 6-bit cubes have rank ≤57 <61 guaranteed. Degree ≥5 needed.
- DIFF: Each input influences ~9 outputs; need ~32.

**Implication:** The single-layer XIG family at degree ≤4 is structurally incapable. This kills Variants A and B as well (both degree 2).

**Open:** Can we achieve degree ≥5 in XIG under 10u? Or is multi-layer required?

## Variant A complete (2026-10-12 ~15:47 CEST)

**Result:** All 3 patterns bijective (10M sampling). P1/P2: 5.8u (better than 6.4u estimate!). P3: 6.4u.

**Note:** Worker recommends Fisher on P1, but Variant C's structural proof (degree ≤4 → rank ≤57 <61 guaranteed) already covers Variant A (degree 2). Fisher would be confirmatory only.

**Process flags from worker:**
1. wt.py new timed out on 5.9G repo (120s sh() timeout) — half-claimed worktree repaired manually.
2. Registry lock contention: cmd_new holds flock across slow git worktree add — concurrent claimants serialize.

## Variant B complete (2026-10-12 ~15:59 CEST, recovered from worktree)

**Result:** P1: 8.2u, P2: 7.9u, P3: 7.7u. All bijective (10M sampling, 0 collisions).

## ALL VARIANTS COMPLETE — Final synthesis

| Variant | Degree | S0 (P1/P2/P3) | Bijective | Fisher |
|---------|--------|---------------|-----------|--------|
| A | 2 | 5.8/5.8/6.4u | YES (10M) | N/T (covered by C proof) |
| B | 2 | 8.2/7.9/7.7u | YES (10M) | N/T (covered by C proof) |
| C | 4 | 6.4/6.4/6.4u | YES (10M) | FAIL (structural) |

**Verdict O155 recorded in VERDICT_SCOPE.md.**

**Key findings:**
1. XIG construction WORKS: 9/9 combos bijective, all <10u (5.8-8.2u).
2. But degree ≤4 is STRUCTURALLY insufficient for Fisher LIN (rank ≤57<61 proven).
3. Re-test trigger: degree ≥5 XIG under 10u.

**End state: DONE**
