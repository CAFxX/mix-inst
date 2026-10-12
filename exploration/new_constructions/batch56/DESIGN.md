# Batch-56 design note — "AND-form variants": ANDN / OR-AND hetero in the 5-stage MUX cascade (track 6, 2026-10-12)

**Status: CO-DESIGNED (incarnation XXX, 2026-10-12 ~01:40 CEST). Pre-pilot next.**

## Trigger

Batch-55 TERMINAL 2026-10-12 (O97, XXIX): the pos1+fisher axis is CLOSED.
fisher-clean AND@pos1 schedules exist (~1%, 1/80 pilot KEEP t6_b55_f0,
18.8u cost-eligible) and the triage validated at S1's per-bit gate
(LIN PASS, DIFF PASS, rej=0 reproduced) — but the AND3@pos1 form cannot
clear S1's low-8-bit joint-distribution DIFF gate (`screen_lindiff`,
rej=2, worst chi2|z|=3.3 @ delta=16, broad elevation across keys).
Combined with O96 (5/5 worst-z keeps per-bit-DIFF-killed), no AND@pos1
schedule clears S1 under either differential statistic — **in the AND3
form**. The combined b53–b55 read: triage/proxy-DIFF does not predict
exact-DIFF for AND-in-cascade, and **the AND gate form itself is now
the open question**. This is XXIX's pre-registered escalation lead;
I (XXX) own it.

## Mechanism question (crisp)

Does the AND gate form — ANDN / OR-AND vs AND3 — change exact-DIFF
survival of the single hetero stage inside the 5-stage MUX cascade?
The instrument (b55's gate-matched fisher triage) is FIXED verbatim:
any difference in keep rate or S1 fate isolates the FORM.

Product geometries of the candidate AND-stage tags (x = 64-bit word):

- AND3 (control, b55 verbatim): `x ^= (ra&rb) ^ rc` — one quadratic
  product (p,q) + linear mask rc. Zero-corner: degrades to `x ^= rc`.
- ANDN (prize arm): `x ^= (ra & ~rb)` — algebraically `ra ^ (ra&rb)`:
  the SAME product pair (p,q) but firing on support (p,~q) instead
  of (p,q), with an INHERENT linear mask ra. Zero-corner: degrades to
  `x ^= ra` (NOT identity — the b43 trap is avoided by construction).
  Gate cost: ANDN2 + 1 XOR level vs AND3's AND2 + 2 XOR levels —
  strictly no more expensive than the measured AND3 stage.
- OAAND (prize arm): `x ^= ((ra|rb) & rc) ^ rd` — OR-AND hetero: two
  quadratic products (p,r),(q,r) + one cubic (p,q,r) + linear mask rd.
  Zero-corner: the ((ra|rb)&rc) term is 0 on single-bit input (would
  be identity without the mask — the b53 cut-#6 trap), so the linear
  term rd is load-bearing, exactly as rc is for AND3. Gate cost: one
  OR2 more than AND3; projected stage ~3.4–3.8u → full-cascade
  projection 19.0–19.5u (cost RISK, recorded; S0 adjudicates —
  projections are not cost evidence).

## Axis audit + de-dup (b19–b55, incarnation XXX)

- The ANDN/OR-AND **hetero** axis (one variant stage inside 4xMUXD)
  was NEVER run. grep-verified: batch-39 screened `andn`
  (`x ^= (ra&~rb)`, 2-term) and `andnM` (`x ^= (ra&~rb)^rc`, 3-term)
  as HOMOGENEOUS 5/6-stage cascades (andnM6a cost-closed 21.8u, O-note
  in ledger XIV); batch-43 screened `ornM5` (`x ^= (ra|~rb)^rc`,
  ORN not OR-AND) homogeneous; batch-44 screened `andorM`
  (`x ^= (ra&rb)^(rc|rd)`, AND+OR-mask) homogeneous 5/6st.
  None is the hetero frame. Ledger candidate rows: no hetero-ANDN /
  hetero-OR-AND rows exist (the fz24_g/h lesson applied — grep covered
  code dirs, log dirs, AND ledger candidate rows).
- Closures inherited (do not retest): O95 (hetMA5 AND3 Q1-SAC-killed),
  O96 (hetMA5p1 5/5 S1 per-bit-DIFF-killed), O97 (hetMA5p1f 1/1 S1
  joint-DIFF-killed, axis closed). The AND3 control arm below is a
  RATE discriminator, not a retest of the closed axis.

## Cost thesis (measured components, arithmetic projection)

- Measured: hetero frame (4xMUXD + AND3@pos1) S0 18.7–19.2u on 4/5
  keeps (b54), 18.8u on the fisher keep (b55). MUXD stage 3.86u
  (MU5 measured). Implied AND3 stage ≈ 3.3–3.8u.
- ANDN: same frame, stage ≤ AND3 cost (fewer XOR levels) →
  projected ≤18.7–19.2u, possibly better. Measured components +
  arithmetic: a defensible thesis, S0 adjudicates.
- OAAND: same frame + 1 OR2 gate on the AND stage → projected
  19.0–19.5u. The strict <19.3u bar is at RISK on the upper end —
  recorded honestly; S0 is fail-loud on it.

## Cuts recorded (defensible reason at each cut site)

1. **AND@pos0/2/3/4: CUT for this batch.** Premise (measured, AND3):
   O94 (pos2/3/4 S1-DIFF-killed) + O95 (only pos1 ever cleared S1) +
   pos0 cost-doomed 19.7u. The position evidence is AND3-specific,
   so this is a PRIORITY ordering, not a verdict on other positions
   for the new forms: pos1 is the only position with ANY measured
   S1-clearing evidence — if a prize form shows quality life at pos1,
   positions become the next widen. (Honest scope: the cut's reason
   is "start where the only positive evidence is", recorded here.)
2. **worst-z triage: CUT (stays replaced).** O96 measured: worst-z
   selection is blind to the fisher-aggregated deviations that kill
   this frame. The gate-matched Holm-Bonferroni bar is the proven
   instrument (b55: 1/80 keep, validated at S1's per-bit gate).
3. **In-triage joint-chi2 pre-gate: CUT.** O97's re-test trigger
   (a both-statistics triage) carries expected yield ~0; adding it
   as a gate would confound the form question with an instrument
   change. S1 fail-fast (41s wall on t6_b55_f0) IS the joint test —
   cheap, authoritative, no confounding. The triage stays verbatim.
4. **3+2 MUX/AND: stays CUT.** b53 cut #3's condition failure
   stands; the AND variable is now quality-closed at 4+1 — doubling
   it is anti-escalation.
5. **MUX-6st full form: CUT on measured per-stage cost** (b53 cut #4:
   6x3.86=23.2u > 19.3u by arithmetic).
6. **d -> constant XOR on MUX stages: CUT** (b52 mechanism finding).
7. **Cubic S-box mining: stays CUT** (b52 cut #1; re-test trigger
   unmet).
8. **maj-5st: stays DEPRIORITIZED** (no measured cost thesis).
9. **A 4th rotation-free OR-AND (`(ra|rb)&rc ^ rc`): CUT — folded.**
   It equals `rc & ~(ra|rb)` (NOR-masked), a THIRD form; running it
   would split the pilot budget three ways on the prize side. It is
   a named re-test trigger if OAAND shows quality life.
10. **Track-1 next-tweak-batch as batch-56: CUT.** Unchanged
    (sweep terminal COMPLETE; out of lane; coordinator design call).
11. **Blind-schedule draws: CUT.** Proxy selection is the proven
    method (O86 + b53/b54/b55); blind is the dominated comparator.

## Pre-registered rules

- **Pre-pilot** (12 draws x 3 arms, seeds 0xB561/0xB562/0xB563):
  HARNESS CHECK ONLY. Calibration must PASS both gates (fail-loud);
  draws must complete; 12 draws cannot falsify at ~1% keep rates.
  → **PILOT runs regardless**, unless GATE-FAIL fires (then KILL
  LOUDLY, diagnose the harness).
- **Pilot**: ANDN 80 draws (0xB564) + OAAND 80 draws (0xB565) +
  AND3-control 24 draws (0xB566, b55 form verbatim — the rate
  discriminator: separates "gate form matters" from "draws bad";
  b55 measured 1/80). Adjudicate on "PILOT COMPLETE".
- **Escalation on >=1 prize-arm fisher-KEEP**: bundle the
  min-(n_reject, worstz) keep per arm (`gen_b56_bundle.py`: b55
  pipeline verbatim — bit-exact C-vs-Python 2000/2000 +
  screener-vs-bundle 500/500; stage tags extended with zero-corner
  unit asserts + fail-loud degeneracy checks) → S0 via run_synth.py
  (bar STRICTLY <19.3u, XCHECK clean) → S1 fail-fast on the first
  cost-eligible keep → staged battery S1→S2→S3→S4 → Q1 (sac_z5=0
  mandatory).
- **Control-arm keeps**: bundle + S0 only (rate/cost data point).
  The AND3 axis is CLOSED at S1 (O97) — re-running its battery is
  theater. A control keep does NOT trigger a new battery.
- **Falsifier (terminal)**: 0/160 prize-arm keeps with calibration
  clean → CLOSE the AND-form-variant axis at the triage level
  (O-entry; scope: ANDN/OAAND hetero @pos1 in the 5st MUX cascade
  + the fisher triage). Re-test triggers recorded: both-statistics
  triage (expected ~0), other AND positions (if any form shows
  quality life), the folded NOR-masked form (cut #9).
- **Terminal conditions**: a keep clearing Q1 at <19.3u →
  FRONTIER CHALLENGER (O-entry + notify); a keep dying at Q1 SAC →
  form-fatal CONFIRMED at the avalanche tail for that form
  (O-entry); a keep S1 joint-DIFF-killed (the b55 signature) →
  that form's joint-signature reproduced (O-entry, axis verdict
  per the falsifier rule).

## Harness

- `batch56/t6_b56_screen.py` — b55 verbatim except: new stage tags
  `ANDN` (`x ^= (ra&~rb)`, 2 rotations, degeneracy p≠q fail-loud)
  and `OAAND` (`x ^= ((ra|rb)&rc) ^ rd`, 4 distinct rotations
  fail-loud); forms `hetMA5N` (ANDN@pos1), `hetMOA5` (OAAND@pos1),
  `hetMA5p1f` (AND3 control, b55-identical); `eval_sched`,
  `holm_reject` bar, `calibrate`, `selftest` unchanged.
  Seeds 0xB561–0xB566. py_compile clean; `selftest` PASS;
  1-draw smoke PASS per arm; `calibrate` PASS both gates
  (CALIB-1 and1/b33c z=3.3 EXACT; CALIB-2 MU5-324 n_reject=0).

## Backoff / launch log

- Pre-pilot `run_b56_prepilot.sh`: cleared-flag backoff pattern
  (b53-pilot template; the double-gate is never re-added —
  AGENTS.md lesson); calibration fail-loud → 12 draws/arm
  (0xB561/0xB562/0xB563) → `prepilot_keeps.jsonl` →
  "PRE-PILOT COMPLETE".
- Launch: `setsid agentwork-launch.sh --nice 19 --tag
  track6/b56-prepilot` (setsid per the batch-43 precedent).
- Heartbeat: `batch56/heartbeat.txt` touched at launch; re-touch
  every ~30 min while live.
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u.
- **Next**: pilot (80+80+24 draws) after the pre-pilot harness
  check; adjudicate per the pre-registered rules above when
  "PILOT COMPLETE" lands in `batch56/pilot.log`.
