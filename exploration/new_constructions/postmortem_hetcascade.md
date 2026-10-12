# Post-mortem: the 5-stage hetero MUX/AND cascade campaign (batches 53–56)

**Track 6, incarnation XXXI, 2026-10-12.** Mechanism-level read of what
b53–b56 actually ruled in/out. Every claim below is scoped to tested
configurations; evidence paths are given, no hand-waving.

## The campaign in one paragraph

Four batches assaulted the 19.3u frontier (hyb28_mu5_324, 5×MUXD) with a
5-stage hetero cascade (4×MUXD + 1×variant stage, pre-whiten `x ^= k`,
final `x ^= rotl(k,13)`). The variant stage took three forms: AND3
(`x ^= (ra&rb) ^ rc`, b53/b54/b55), ANDN (`x ^= (ra&~rb)`, b56),
OAAND (`x ^= ((ra|rb)&rc) ^ rd`, b56). Net result: **the family cannot
beat 19.3u — killed three ways.** AND3 died at S1-DIFF for 6/7 tested
schedules (O94/O96/O97) and at Q1-SAC for the one schedule that cleared
S1→S4 (O95). ANDN died at triage (0/80 fisher-keeps, O99). OAAND died at
cost (4/4 keeps 19.4–20.1u vs the strict <19.3u bar, O99/O100). The
frontier survived four assaults.

## What distinguishes h0 (the sole S1→S4 survivor)?

` t6_b53_h0`: AND3(16,10,5)@pos1 + 4×MUXD, triage z=2.95, S0 19.1u.
Raw: `new_constructions/batch53/pilot_keeps.jsonl` (line 2),
`fast_battery/results/t6_b53_h0/` (battery COMPLETE),
`new_constructions/batch53/q1_t6_b53_h0/q1_t6_b53_h0.json`
(sac_z5=9, bic_maxcorr=0.00906).

h0 cleared: S1 LIN (rej=0) + S1 per-bit DIFF (rej=0) + S1 low-8-bit
joint-chi2 DIFF (no FLAG — it predates the gate's isolation, but its S1
was CAL_PASS under the full battery), S2 (0 repeats), S3 (64M/256M/1G +
strided), S4. It died ONLY at Q1: sac_z5=9 (9 avalanche z5-cells;
bic fine at 0.00906).

What makes h0 different from the six S1-DIFF kills? **Position + schedule,
jointly — neither alone is sufficient:**

1. **Position is necessary but not sufficient.** O94: AND@pos2/3/4
   (h4/h1/h3) all S1-DIFF-killed even though h1's triage z=3.01 was
   *lower* than h0's 2.95. AND@pos0 (h2) was cost-doomed (19.7u),
   quality untested. So pos1 is the only position with ANY S1-clearing
   evidence — but O96 proved it is not sufficient: 5 more AND@pos1
   schedules (exact-DIFF-proxy-selected, triage z 4.28–9.44) ALL
   S1-DIFF-killed (per-bit gate, rej=1/1/2/4/5). The "AND@pos1
   tolerance" was h0-schedule-specific, not position-specific.

2. **The triage statistic does not see the poisoning.** O96's
   instrument-confound finding: full-S1 worst|z| reproduced triage z
   bit-for-bit (4.28/4.58/5.52/7.27/9.44), yet all five died on the
   gate's Holm-Bonferroni fisher aggregation. The form produces *many
   small systematic deviations* (low max-z, strongly negative fisher),
   which worst-z selection cannot see. O97 resolved the confound for
   the per-bit gate (fisher-matched triage: 1/80 keep, and the keep's
   n_reject=0 reproduced at S1's per-bit DIFF gate) — but the keep
   (f0) then died at the *joint* low-8-bit chi2 DIFF gate (rej=2,
   worst chi2|z|=3.3 @ delta=16). **The AND stage's poisoning is
   visible in the low-byte joint distribution even when per-bit
   marginals are clean.** Two differential statistics, two walls;
   no AND3@pos1 schedule clears both.

3. **h0's Q1 failure is the avalanche tail, not the differential
   body.** h0's differentials were clean through S4; its SAC tail
   (9 z5-cells) is a *different* failure mode from the S1-DIFF wall.
   O95's mechanism question — schedule-specific vs form-fatal —
   **never got its discriminator**: b54's five discriminator schedules
   died at S1, so no second schedule ever reached Q1. The question is
   OPEN, but see §"Is there a surviving sub-axis" for why it does not
   matter for the frontier.

## Is there a surviving sub-axis in the hetero-cascade form?

No. The three variant forms are each closed on independent evidence:

- **AND3** (b53/b54/b55): closed at S1 (6/7 schedules: 3 per-bit-DIFF,
  3 per-bit-DIFF under proxy selection, 1 joint-DIFF) and at Q1 (1/1:
  h0, sac_z5=9). The S1 wall binds first; the Q1 wall binds the only
  survivor. There is no remaining AND3 configuration with a positive
  evidence trail.
- **ANDN** (b56): closed at triage — 0/80 fisher-keeps under the
  gate-matched bar (O99). The form does not produce S1-plausible
  schedules at all. (Note: this is the *hetero* ANDN; homogeneous
  andnM was separately closed at b39/b43.)
- **OAAND** (b56): closed at cost — 4/4 best-ranked keeps measured
  19.4/20.1/19.5/19.5u, all ≥19.3u (O99/O100). The OR gate's extra
  level costs ~0.1–0.8u vs AND3; the cluster is tight, no tail
  below the bar. The 5 remaining keeps (z=3.58–4.55) are a recorded
  re-test trigger, not a live axis — worse triage rank has never
  beaten better rank on S0 in this campaign.

**The h0 Q1-tail sub-axis (option (a)) — evaluated honestly:**
The unresolved discriminator (is sac_z5=9 schedule-specific or
form-fatal?) is scientifically real but frontier-irrelevant:
(i) S1-clearing AND3-hetero schedules yield ~1% (1/40 blind, 1/80
fisher), so reaching Q1 costs ~100 S1 screens per candidate;
(ii) h0's cost headroom is 0.2u (19.1 vs 19.3), and every known
avalanche-tail cure (the round-19 fm precedent: +0.9–1.9u) blows
it — only a *free* schedule tweak could work, which is a lottery
ticket, not a co-designed axis; (iii) the form is already closed
at S1 for frontier purposes (O96/O97) — even a schedule-specific
answer does not reopen it, it only says "keep buying 1% lottery
tickets." **Verdict: recorded as a deferred lead, not batch-57.**
Re-test trigger: a principled SAC-tail mechanism (not a schedule
lottery) for AND-in-cascade.

## What the campaign ruled IN (positive evidence to build on)

1. **The fisher-matched triage is a proven instrument.** b55: the
   triage's n_reject=0 prediction reproduced at S1's per-bit DIFF
   gate bit-for-bit (O97). It is strictly better than worst-z
   selection (O96). **It has never been applied to the pure-MUXD
   schedule space** — 324 was found with the obsolete worst-z
   triage (z=3.24). This is the largest open instrument gap in
   track 6.
2. **The 5-stage per-bit cascade frame's cost structure is measured:**
   MUXD 3.86u/stage, AND3 ~3.3u/stage, OAAND ~3.4–3.8u/stage.
   Any 5-stage schedule with MUXD-class gate count is
   cost-competitive by construction; S0 adjudicates per schedule.
3. **Position-1 is the quality-tolerant slot** for hetero stages
   (O94) — relevant if a future hetero form shows life.
4. **The low-8-bit joint-chi2 DIFF gate is the binding constraint**
   for AND-in-cascade (O97) — any future AND-family proposal must
   address the joint distribution, not just per-bit marginals.

## Closed axes (do not retest without the stated trigger)

| Axis | Verdict | Scope | Re-test trigger |
|---|---|---|---|
| AND3-hetero 5st cascade | Quality-closed (S1 6/7, Q1 1/1) | 4×MUXD+1×AND3@any pos, pre-whiten, rotl(k,13) | principled SAC-tail mechanism |
| ANDN-hetero 5st cascade | Triage-closed (0/80) | ANDN@pos1 + fisher triage | none recorded (strong kill) |
| OAAND-hetero 5st cascade | Cost-closed (4/4 ≥19.3u) | 4×MUXD+1×OAAND@pos1 | a remaining keep (o4–o8) clearing <19.3u |
| 4st MUX cascade | Mechanism-closed (O89) | ≤4st MUX, triage z 3823+ | none (depth theorem) |
| 6st AND cascade | Cost-closed (19.8u floor) | t6_b33 form | none |
| MUX-no-d 5st | Mechanism-closed (b52) | d-term ablation | none (d load-bearing) |
| nandM/norM/ornM homog. 5st | Triage-closed (0/40 each, b43) | complemented-gate homog. | none |
| maj 5st+ | Cost-closed (~4.9u/stage) + contractor mechanism (fmaj6a) | majority gates | none |
| no-rc AND cascade | LIN-closed (rej=10/10, norc5a) | rc-term ablation | none (rc load-bearing for LIN) |
| 3+2 MUX/AND | Cut (b53) | doubled AND in hetero | AND variable reopened (it closed instead) |
| Cubic mining | Cut (b52) | structural cost | trigger unmet |
| 4st dense (chi/Q) | Cost-doomed (22.9–28u) | b45/b49/b50 | cheaper dense stage measured |

## Bottom line

The hetero-cascade form is exhausted: three variant gates, three
independent kills (S1-differential, triage-absence, cost-floor). h0
was a 1%-yield existence proof that an AND3-hetero schedule *can*
clear S1→S4, but its Q1 SAC tail (sac_z5=9) and 0.2u cost headroom
leave no co-designed path to the frontier. The campaign's durable
outputs are the fisher-matched triage instrument and the measured
5-stage cost structure — batch-57 builds on both, on the frontier's
own (proven quality-clean) MUXD form.
