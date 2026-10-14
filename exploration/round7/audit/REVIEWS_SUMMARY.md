# Peer-review consolidation: r7_feist8_s1_1sbox (2026-10-02)

Four independent reviewers, no cross-communication. Each read the actual sources
and ran their own checks. Individual reports: [`review_rtl.md`](review_rtl.md),
[`review_statistics.md`](review_statistics.md), [`review_cryptanalysis.md`](review_cryptanalysis.md), [`review_synthesis.md`](review_synthesis.md).

## Verdicts

| Reviewer | Verdict | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|
| RTL | APPROVE | 0 | 0 | 3 |
| Statistics | APPROVE-WITH-FINDINGS | 0 | 6 | 4 |
| Cryptanalysis | APPROVE-WITH-FINDINGS | 0 | 3 | 1 |
| Synthesis | APPROVE | 0 | 0 | 0 |

**Overall: the design is APPROVED — no reviewer found a functional flaw or a
practical attack.** The 9 MAJORS are methodology/documentation/safety-case items,
not design defects. They require action before any production/adversarial claim.

## Consolidated MAJOR findings (all judged VALID)

### Cryptanalysis (most security-substantive)
1. **M9's differential bound is wrong; safety case must be revised.** M9 claimed
   best 2-round trail ≈2⁻¹⁰; the true best is 2⁻² (Feistel skip pattern: input
   difference (a,0), zero active S-boxes in round 1). The 8-round "≈2⁻⁵⁸" was
   extrapolated from the wrong number. Independent beam search: best 8-round
   trail = **2⁻⁶¹, 25 active S-boxes** (stable across width-4000 and width-8000
   runs). MEMORY.md's M9 entry must be corrected.
2. **Thin theoretical margin: 2⁻⁶¹ is 8× above the 2⁻⁶⁴ ideal threshold.**
   Adequate for a mixer (2⁶¹ queries utterly impractical; differentials give a
   hash-DoS attacker nothing beyond direct computation), not generous. Not a
   cipher-grade margin.
3. **Related-key differential 2⁻³⁷ beats single-key 2⁻⁶¹.** The affine key
   schedule (`rk(k^δ,i) = rk(k,i)^rotl64(δ,13(i+1))`, all 8 rotations distinct)
   hands a related-key attacker a strictly better trail — certificational
   weakness. NOT in the hash-DoS threat model (fixed key, no related-key
   oracles), so not a blocker; must be recorded in the safety case.

### Statistics (methodology — claims must be scoped to what was measured)
4. **S1 "honest FWER ≤ 0.04" is overstated.** 3 of 4 families Fisher-combine
   dependent p-values (liberal; admitted in their own docstring). Only LIN is
   rigorous. The bound must be restated honestly.
5. **Search multiplicity unaccounted.** 17 round-7 candidates at ~4% each →
   ~50% chance of ≥1 false CAL_PASS in the search. Leader selection is
   post-selection inference. Mitigated here by independent re-verification
   (audit + 4 reviews), but the screening claim must carry the caveat.
6. **Latent orchestrator bug: [`s1_screen.py`](../../fast_battery/src/s1_screen.py) drops the inner LIN/DIFF kill
   signal.** A borderline candidate could be misreported CAL_PASS. Did not fire
   for this leader (verified), but it is a real bug — fix per escape protocol
   (the two LIN/DIFF implementations also differ in pair sets/p-transforms).
7. **S2 kill threshold (1000 repeats) is ~7 orders of magnitude above the null**
   (E[repeats]≈1.2e-7; a single repeat is already damning). Threshold should be
   tied to the null, not arbitrary.
8. **S2 delta set is not S-box-driven.** 5 of the 10 worst S-box input diffs
   (0x6, 0xA, 0xC, 0xD, 0xF; max DP 2⁻²) are untested as single-nibble deltas.
   Drive deltas from the DDT.
9. **"Zero repeats at N=2²²" rules out per-pair repeat prob ≳2⁻³⁹ but only
   specific differentials at q ≳ 2⁻²⁰** — says nothing about 2⁻³²-level
   differentials. The claim must carry this interpretation bound.

## MINOR findings (valid, low priority)
- RTL: dead `r == 0` branch in `rk()` (unreachable for rounds 1..8); missing
  `` `timescale ``; shadowed loop variable `i` (correct but misreadable).
- Statistics: S1 DIFF docstring overstates pairs (2¹⁶ not 2¹⁷); S3 FAIL-only
  grep missed an "unusual" Gap-16:A at 16MB (benign, vanished at 32MB+) and a
  vacuous 16MB stage that ran zero tests; S3/S4 config coverage thin.
- Cryptanalysis: no weak keys found (0 fixed points over 2²² for k=0/random/
  all-ones; no slide pairs; F key-independent differential profile).

## Positive confirmations (independent re-verification)
- RTL: 22,139/22,139 vectors bit-exact (incl. edge cases); S-box table and key
  schedule verified entry-by-entry against code; mutation (1 flipped S-box
  entry) caught: 2090/2139 fail.
- Synthesis: clean-env re-run reproduces 56.5u/0.546× byte-exactly (Yosys pin
  verified working); ABC cec with a no-abc/no-dretime reference BLIF proves
  RTL≡netlist independently of the dretime failure mode; 2054/2054 mapped
  netlist vs model; mutation caught (2023/2054 mismatches ≈ (15/16)⁶⁴ prediction).
- Statistics: SmallCrush re-run with a new key 15/15 pass; raw S1/S2 numbers
  verified null-like from the JSON/logs.
- Cryptanalysis: no practical attack found by any method; weak-key,
  related-key-structure, and slide analyses all clean except the recorded
  2⁻³⁷ related-key trail bound.

## Required actions before any adversarial/production claim
1. Revise M9's safety case: replace 2-round 2⁻¹⁰ → 2⁻², 8-round 2⁻⁵⁸ → 2⁻⁶¹
   (beam search), record related-key 2⁻³⁷ bound and thin-margin assessment.
   Correct MEMORY.md's M9 entry.
2. Fix [`s1_screen.py`](../../fast_battery/src/s1_screen.py) dropped inner-kill signal (escape protocol: hunt the
   class — check other orchestrators for dropped signals).
3. Restate S1 FWER honestly; add search-multiplicity caveat to screening claims.
4. Tie S2 kill threshold to the null; drive S2 deltas from the S-box DDT.
5. Scope "zero repeats" claims with the q ≳ 2⁻²⁰ interpretation bound.
