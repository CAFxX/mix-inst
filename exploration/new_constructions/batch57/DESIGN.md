# Batch-57 design note — "muxD5f": fisher-matched schedule search over the pure-MUXD 5-stage cascade (track 6, 2026-10-12)

**Status: CO-DESIGNED (incarnation XXXI, 2026-10-12 ~02:30 CEST). Pre-pilot next.**

## Trigger

Batch-56 CLOSED 2026-10-12 (O99/O100, XXX): hetMOA5 cost-closed —
4/4 best-ranked OAAND keeps measured 19.4/20.1/19.5/19.5u, all ≥19.3u.
ANDN hetero was triage-dead 0/80 (O99). The 5-stage hetero MUX/AND
cascade campaign is fully closed — post-mortem in
`new_constructions/postmortem_hetcascade.md` (mechanism-level,
evidence paths, closed-axis table). Zero active leads; the open-ended
search continues.

## The honest axis argument (options evaluated against evidence)

**(a) h0-schedule-family variants targeting the Q1-avalanche tail —
DEFERRED, not batch-57.** h0 (`t6_b53_h0`, AND3(16,10,5)@pos1, S0
19.1u) is the unique AND3-hetero schedule to clear S1→S4; it died at
Q1 (sac_z5=9). O95's discriminator (schedule-specific vs form-fatal)
never ran — b54's five discriminator schedules died at S1. The
question is scientifically real but frontier-irrelevant:
(i) S1-clearing AND3-hetero schedules yield ~1% (1/40 blind, 1/80
fisher), so each Q1 candidate costs ~100 S1 screens;
(ii) h0's cost headroom is 0.2u (19.1 vs 19.3), and every known
avalanche-tail cure (round-19 fm precedent: +0.9–1.9u) blows it —
only a *free* schedule tweak could work, which is a lottery ticket,
not a co-designed axis;
(iii) the form is already closed at S1 for frontier purposes
(O96/O97) — even a schedule-specific answer does not reopen it.
Recorded as a deferred lead (re-test trigger: a principled SAC-tail
mechanism for AND-in-cascade, not a schedule lottery).

**(b) A different hetero primitive (ANDN / OR-AND co-design) —
CLOSED, state verified.** ANDN hetero: 0/80 fisher-keeps under the
gate-matched bar (O99) — the form produces no S1-plausible schedules.
OAAND hetero: 4/4 best keeps cost-doomed 19.4–20.1u (O99/O100) —
the OR level costs ~0.1–0.8u vs AND3 with no quality upside on
record. Both arms of the b56 escalation are terminal. Do not pursue.

**(c) An entirely new construction family — NO CANDIDATE CLEARS THE
MEASURED-COST-THESIS BAR.** Surveyed against the wall map
(postmortem §Closed axes): 4st (mechanism-dead O89), 6st AND
(cost-blocked 19.8u), maj (~4.9u/stage cost-doomed + contractor
mechanism), nandM/norM/ornM homogeneous (triage-dead 0/40, b43),
no-rc (LIN-dead rej=10/10), chi-hetero (S1-marginal O82; word-fused
10/10 S1-DIFF-killed wave-13), Feistel/SPN frames (37u+/26u+ —
orders of magnitude off). No untested family has a *measured*
sub-19.3u cost thesis. An honest batch-57 does not invent one.

**Selected axis: the fisher-matched instrument on the frontier's own
form.** The b55 fisher-matched triage is the proven better instrument
(O97: triage n_reject=0 reproduced at S1's per-bit DIFF gate
bit-for-bit; O96: worst-z selection is blind to fisher-aggregated
deviations). **It has never been applied to the pure-MUXD schedule
space** — grep-verified: only `batch55/t6_b55_screen.py` and
`batch56/t6_b56_screen.py` use `holm_reject`, both hetero-only;
hyb28_mu5_324 was found with the obsolete worst-z triage (z=3.24).
The form is proven quality-clean (324 passes S0–S4 + Q1); the
instrument is proven gate-matched; any keep is cost-competitive by
construction (identical gate count to 324). This is orthogonal to
the closed hetero family (homogeneous, not hetero) and carries the
strongest EV of any evaluated option: it directly attacks the
frontier with the best selection method track 6 has.

## Axis: muxD5f

- **Form:** 5 stages of full MUXD
  `x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)`,
  pre-whiten `x ^= k`, final `x ^= rotl(k,13)` — bit-identical frame
  to hyb28_mu5_324. The ONLY delta from the frontier is the rotation
  schedule.
- **Draw constraints (fail-loud):** MUX stages s,a,b pairwise
  distinct (b51 cut #10 degeneracy proof); d free; duplicate
  stage-tuples re-drawn within a try (b41); draw-loop cap 10000
  (b45 fail-loud pattern).
- **KEEP bar:** n_reject == 0 under Holm-Bonferroni on per-key
  fisher_logp (ALPHA=0.01) — `holm_reject` verbatim from b55, the S1
  per-bit DIFF gate's own rule. Calibrated: 324 itself is a
  fisher-KEEP (n_reject=0, z=3.24, min_fisher=-3.7 — verified
  2026-10-12 on the b57 harness's inherited `calibrate`).
- **Measured cost thesis:** MUXD stage 3.86u (324 measured); a new
  schedule has the identical gate count → S0 ~19.3u ± synthesis
  noise. Bar STRICTLY <19.3u; S0 adjudicates per keep (run_synth.py,
  ref mul64 103.5u, pinned yosys 0.69, XCHECK clean). This is
  measured-component reasoning (b56 precedent), not projection.
- **Mechanism question (crisp):** does the gate-matched instrument
  find MUXD schedules better than 324, the worst-z-triage winner?
  (Better = lower S0 at full quality, or equal S0 with better
  margins / fewer cells.)

## Cuts (defensible reason at each cut site)

1. **Hetero stage forms (AND3/ANDN/OAAND): CUT.** Postmortem:
   three independent kills (S1-differential, triage-absence,
   cost-floor). The hetero family is exhausted.
2. **h0-neighborhood / Q1-tail lottery: DEFERRED** (see (a) above).
   Not a cut on the question's validity — on its EV as batch-57.
3. **Worst-z triage: CUT (stays replaced).** O96 measured: blind to
   the fisher-aggregated deviations. The gate-matched bar is the
   proven instrument.
4. **4-stage / 6-stage / non-MUXD gates: CUT.** Wall map closed
   (postmortem §Closed axes); re-test triggers recorded there.
5. **Blind-schedule draws: CUT.** Proxy/instrument selection is the
   proven method (O86 + b53/b54/b55); blind is the dominated
   comparator.
6. **324-rediscovery: NOT a challenger.** If a draw reproduces
   MU5_324_SCHED exactly, it is logged `[324-REDISCOVERY]` and
   adjudicated as instrument validation (the fisher bar accepts the
   frontier), not a frontier challenger. (Probability ~0 in 80
   draws over a 64^20 space; the flag is fail-loud honesty.)

## Pre-registered rules

- **Pre-pilot** (12 draws, seed 0xB571): HARNESS CHECK ONLY.
  Calibration must PASS both gates (CALIB-1 and1/b33c z=3.3 EXACT;
  CALIB-2 MU5-324 n_reject=0 — fail-loud); draws must complete;
  12 draws cannot falsify → **PILOT runs regardless**, unless
  GATE-FAIL fires (0 kills across 12 → KILL LOUDLY, diagnose —
  the fisher bar would be vacuous on MUXD, which contradicts
  CALIB-2).
- **Pilot** (80 draws, seed 0xB572): adjudicate on "PILOT COMPLETE".
- **Escalation on ≥1 fisher-KEEP:** bundle the min-(n_reject,
  worstz) keep (`gen_b57_bundle.py`: b55 pipeline verbatim —
  bit-exact C-vs-Python 2000/2000 + screener-vs-bundle 500/500;
  MUXD-only stage tags) → S0 via run_synth.py (bar STRICTLY
  <19.3u, XCHECK clean) → first cost-eligible keep → staged
  battery S1→S2→S3→S4 → Q1 (sac_z5=0 mandatory).
- **Falsifier:** 0/80 keeps with calibration clean → the fisher
  instrument finds nothing in MUXD space beyond 324 (O-entry):
  324's optimality under both triages; the MUXD schedule space is
  instrument-closed. Next: re-examine deferred leads.
- **Terminal conditions:** a keep clearing Q1 at <19.3u →
  FRONTIER CHALLENGER (O-entry + notify parent); a keep dying at
  any gate → O-entry scoped to the tested schedule (the form
  itself is proven — a keep's death is schedule-specific, not
  form-fatal, by the 324 existence proof).

## Harness

- `batch57/t6_b57_screen.py` — b55 verbatim except: form `muxD5f`
  (5×MUXD via `draw_muxD5f`); `draw_and`/`draw_hetMA5p1` removed;
  `eval_sched`, `holm_reject` bar, `calibrate` (both gates),
  `selftest`, MU5_324_SCHED reference, draw-loop cap unchanged.
  Seeds 0xB571 (pre-pilot) / 0xB572 (pilot). py_compile clean;
  `selftest` PASS; 2-draw smoke PASS (both killed, fisher bar live).
- `batch57/run_b57_prepilot.sh` — cleared-flag backoff pattern
  (b53-pilot template; the double-gate is never re-added —
  AGENTS.md lesson); calibration fail-loud → 12 draws (0xB571) →
  `prepilot_keeps.jsonl` → "PRE-PILOT COMPLETE".
- Launch: `setsid agentwork-launch.sh --nice 19 --tag
  track6/b57-prepilot` (setsid per the batch-43 precedent).
- Heartbeat: `batch57/heartbeat.txt` touched at launch; re-touch
  every ~20 min while live.
- **Frontier unchanged:** hyb28_mu5_324 at 19.3u.
