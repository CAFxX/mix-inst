# Batch-55 design note — "hetMA5p1f": AND@pos1-fixed hetero cascade + FISHER-MATCHED triage (track 6, 2026-10-12)

**Status: PRE-PILOT LAUNCHED (incarnation XXIX, 2026-10-12 ~01:10 CEST).**

## Trigger

Batch-54 CLOSED 2026-10-12 (O96 recorded in VERDICT_SCOPE.md by XXIX):
5/5 exact-DIFF-proxy-selected AND@pos1 schedules **S1-DIFF-KILLED (rc=2)** —
LIN PASS (rej=0 all), DIFF FLAG rej=1/1/2/4/5 (fisher_logp to -70.4).
The b54 mechanism finding, raw-verified from
`fast_battery/results/t6_b54_{h1,h2,h3,h4,h6}/s1_result.json`:
**the triage's worst-z KEEP bar (z<10) does not predict the S1 DIFF gate.**
Full-S1 worst|z| reproduces triage z bit-for-bit (4.28/4.58/5.52/7.27/9.44),
yet all five keeps died on the gate's Holm-Bonferroni fisher aggregation —
hetMA5p1 produces many small systematic deviations (low max-z, strongly
negative fisher), which worst-z selection cannot see. The AND@pos1
"tolerance" was h0-schedule-specific, NOT position-specific. Combined with
O95 (h0 Q1-SAC-killed at sac_z5=9), hetMA5 is QUALITY-CLOSED **in this
construction** (5st 4xMUX+1xb33-AND, pre-whiten, rotl(k,13)) — failed at S1
(b54, 5/5) AND at Q1 (b53, 1/1).

**The honest gap:** the S1 gate was never given a fair chance at a
FISHER-clean schedule. b54's keeps were selected on the wrong statistic.
Before the form's S1 death is final, the instrument confound must be
isolated.

## Axis audit (batches 19–54, 2026-10-12, incarnation XXIX)

The b53/b54 wall map stands, plus the b54 verdicts:

- <=4st: every sparse mechanism dead (b43 zero-corner, b44 tap-count,
  b46 hetero, b51 firing-geometry); dense-4st quality-alive but
  cost-doomed (22.9–28u).
- 5st: sparse-AND homogeneous dead (b43); MUX-5st homogeneous IS the
  19.3u frontier (hyb28_mu5_324); MUX-5st-no-d dead on mechanism (b52:
  d load-bearing); **hetMA5 (4xMUX+1xb33-AND) QUALITY-CLOSED (O95+O96)** —
  S1 0/5 (b54) + Q1 0/1 (b53).
- 3st: dead x4 distinct mechanisms.
- Cubic mining CUT on structural cost (b52 cut #1, unchanged — re-test
  trigger unmet).
- maj-5st DEPRIORITIZED (no measured cost thesis, unchanged).
- 3+2 MUX/AND: stays CUT (b53 cut #3's condition failure stands;
  hetMA5 now quality-closed — doubling the AND is anti-escalation).
- **NEW (b54): the triage instrument is a confound, not a verdict.**
  worst-z selection ≠ gate-matched selection for hetMA5p1 (O96).

## Selected axis: hetMA5p1f — same form, gate-matched triage

- **Form:** bit-identical to batch-54 (5 stages — 4x full MUXD + 1x b33
  AND3 at stage index 1, FIXED, fail-loud asserts; pre-whiten `x ^= k`;
  final `x ^= rotl(k,13)`). The ONLY delta from b54 is the KEEP bar.
- **The instrument fix:** KEEP iff **0 Holm-Bonferroni rejections**
  on per-key fisher_logp at ALPHA=0.01 — `lin_diff.holm_reject`
  verbatim, the S1 DIFF gate's own rule (`screen_lin_diff`). The
  triage becomes a true pre-filter: a keep that survives triage has,
  by construction, already survived the gate's decision procedure on
  the same inputs.
- **Measured cost thesis:** unchanged from b54 — hetMA5 S0 18.7–19.2u
  on 4/5 cost-eligible keeps < STRICT 19.3u bar (b54 S0 log).
- **Mechanism question (crisp):** do FISHER-clean AND@pos1 schedules
  exist in the hetMA5p1 draw space?
- **Falsifier / escalation (pre-registered):**
  - Pre-pilot 12 draws (seed 0xB551): HARNESS CHECK ONLY (calibration
    must PASS both gates, fail-loud; draws must complete). 12 draws
    cannot falsify under the strict bar (P(0/12) ~ 0.89 at a 1% true
    keep rate) → PILOT (80 draws, seed 0xB552) runs regardless.
  - Pilot >=1 fisher-KEEP → bundle the min-rejection keep
    (`gen_b55_bundle.py`, b53/b54 pipeline verbatim: bit-exact
    C-vs-Python 2000/2000 + screener-vs-bundle 500/500) → S0
    (stratified min/med/max rejection count if multiple keeps; bar
    STRICTLY <19.3u, XCHECK clean) → S1 fail-fast on first
    cost-eligible → staged battery S1→S2→S3→S4 → Q1 (sac_z5=0
    mandatory).
  - Pilot 0/80 → CLOSE the pos1+fisher axis (O-entry); escalate to
    AND-form variants (ANDN / OR-AND) — b54 cut #8's condition.
- **Terminal conditions:**
  - A keep clearing Q1 at <19.3u → FRONTIER CHALLENGER.
  - A keep dying at Q1 SAC again → form-fatal CONFIRMED at the
    avalanche tail (O95's mechanism question resolved: form-fatal,
    not schedule-specific).
  - 0/80 → pos1 search closed even with a gate-matched instrument.

## De-dup (grep-verified 2026-10-12, incarnation XXIX)

- hetMA5p1 with a gate-matched (Holm-Bonferroni fisher) KEEP bar:
  NEVER run. b54 used worst-z<10; b53 drew blind. `grep -rn
  "holm_reject\|fisher" new_constructions/batch5*/t6_b5*_screen.py`
  shows the fisher rule only in b55's script.
- Ledger candidate rows: no fisher-selected hetero rows exist.
- directed_design / adder_lat / hybrid: no MUX/AND hetero cascade
  with gate-matched selection — no conflict.

## Cuts recorded (defensible reason at each cut site)

1. **worst-z KEEP bar: REPLACED (the batch's core change).** Premise
   (measured, O96): 5/5 worst-z<10 keeps died at the gate's fisher
   aggregation; full-S1 worst|z| reproduces triage z bit-for-bit, so
   the triage had the data and ignored it. Inference: the instrument
   must implement the gate's decision rule to be a valid pre-filter.
2. **AND@pos0/2/3/4 in the search: CUT.** Premises (measured):
   O94 (pos2/3/4 S1-DIFF-killed) + O96 (pos1 the only S1-clearing
   position; pos0 cost-doomed 19.7u). Unchanged from b54 cut #4.
3. **Blind-schedule draws: CUT.** O86 + b53/b54 measurements: proxy
   selection is the proven method; blind is the dominated comparator.
4. **3+2 MUX/AND hetero: stays CUT.** b53 cut #3's condition failure
   ("4+1 keeps strongly") stands; hetMA5 is now quality-closed —
   doubling the poisoning variable is anti-escalation.
5. **ANDN / OR-AND hetero forms: DEFERRED to escalation, not cut.**
   b54 cut #8's condition (a new mechanism finding) is MET — but
   running a new form before fixing the instrument would confound
   form effects with instrument effects. Pre-registered escalation
   if b55 closes (0/80 or Q1-SAC-kill).
6. **MUX-6st full form: CUT on measured per-stage cost** (b53 cut #4
   unchanged: 6x3.86=23.2u > 19.3u by arithmetic).
7. **d -> constant XOR on MUX stages: CUT on the b52 mechanism
   finding** (b53 cut #3 unchanged).
8. **Cubic S-box mining: stays CUT** (b52 cut #1; re-test trigger
   unmet).
9. **maj-5st: stays DEPRIORITIZED** (no measured cost thesis).
10. **Control arm (muxS5d): CUT for this batch.** Harness validated —
    b54 calibration PASS both gates; b55's CALIB-2 additionally
    validates the new bar against MU5-324 (0 rejections, measured).
11. **Track-1 next-tweak-batch as batch-55: CUT.** Unchanged from b54
    cut #9 (sweep terminal COMPLETE; out of lane).

## Harness

- `batch55/t6_b55_screen.py` — adapted from b54's verbatim (draw
  constraints, stage forms, AND@pos1 fail-loud asserts, calibration
  pair, draw-loop cap 10000, per-try JSONL checkpoint unchanged);
  the ONLY functional delta is `eval_sched` → Holm-Bonferroni
  rejection count via `lin_diff.holm_reject` (ALPHA=0.01), KEEP iff
  0 rejections. Seeds 0xB551/0xB552. py_compile clean; `selftest`
  PASS; 1-draw smoke PASS (n_reject=10 path exercised);
  `calibrate` PASS both gates (CALIB-1 and1/b33c z=3.3 EXACT;
  CALIB-2 MU5-324 n_reject=0, min_fisher=-3.7 — the bar is not
  miscalibrated against a known-good schedule).

## Backoff / launch log

- Pre-pilot `run_b55_prepilot.sh`: cleared-flag backoff pattern (the
  fixed b53-pilot template; the double-gate is never re-added —
  AGENTS.md lesson); calibration fail-loud → hetMA5p1f 12 draws
  0xB551 → `prepilot_keeps.jsonl` → "PRE-PILOT COMPLETE".
- Launch: `setsid agentwork-launch.sh --nice 19 --tag
  track6/b55-prepilot` (setsid per the batch-43 precedent).
- Heartbeat: `batch55/heartbeat.txt` touched at launch; re-touch
  every ~20 min while live.
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u.
- **Next**: pilot (80 draws, 0xB552) runs after the pre-pilot
  harness check; adjudicate per the pre-registered rules above
  when "PILOT COMPLETE" lands in `batch55/pilot.log`.
