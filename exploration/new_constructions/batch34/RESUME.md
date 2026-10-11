# Batch-34 resume note (track-6 supervisor incarnation IV, 2026-10-11 ~01:35 CEST)

## Axis
Dense 3-term stage exact-DIFF schedule search (uniform cascades, 5 stages primary).
De-duplicated vs track-5 batch-22 (self-masking `x&(x)`, 1-AND@5st control) and
track-3 wave-14 (word-level fused; owns the narrow-add ARX re-test trigger).

## Arms (exact-DIFF triage, 200 draws, KEEP bar max|z|<10)
- B34-A: `x^=(ra&rb&rc)^rd` (AND3+mask) @5st — log screen_a3_5st.log, tag track6/b34-screen-a3
- B34-B: `x^=~((ra&rb)|rc)^rd` (AOI21+mask) @5st — log screen_aoi_5st.log, tag track6/b34-screen-aoi
- B34-C: `x^=(ra&rb&rc)^(rd&re&rf)^rg` (dual-AND3+mask) @4st — NOT YET LAUNCHED (long shot)
- B34-D: a3 @4st — NOT YET LAUNCHED (long shot)

## S0 cost probes (per-stage delay, kill-or-commit)
probes.v has 5 single-stage modules; run_synth.py needs TMPDIR workaround
(see INFRA). stg_and1 is the positive control (must read ~3.3u).
Re-run all 5 via s0_probes.sh AFTER exporting TMPDIR=$PWD/tmp
(the script does not export it yet — the manual TMPDIR run for stg_and1
is session proc_74f388fd4022).

## INFRA (LOUD, box-wide) — UPDATE 01:50: /tmp-full was TRANSIENT, now 1% used.
- The transient (01:05–01:45) WEDGED two S0 workers (mine + track-3 wave-14
  calib): 0–1s CPU in 11–14 min, yosys/abc hung, not crashed.
- Fixed: killed my wedged PIDs, re-launched s0_probes.sh clean (tag track6/b34-s0).
- Track-3's wedged PIDs already reaped; they must verify wave-14 calib.log
  (the 23:18Z w_add64 run is suspect).
- Lesson: a full /tmp makes ABC hang (not fail-loud). Watch for it.
- Triage script t6_b34_screen.py CALIBRATED: reproduces b33c z=3.3 exactly
  (and1 form + b33c schedule from gen_t6_b33.py).

## Method
t6_b34_screen.py <form> <nstages> <n_try> <seed> — forms: and1 (calibration),
a3, aoi, d2a3. Same harness as batch-33: pre-whiten, final ^rotl(k,13),
10 keys, sequential V, lin_diff.diff_cell_logps.

## Escalation (when screens complete)
1. Read KEEP lines from screen_*.log (z<10).
2. Cost gate: S0 per-stage u × nstages < 19.8u (frontier).
3. Survivors → bundle (model.py/impl.c/rtl.v/meta.json, mix/mix_np interface,
   goldens) → bit-exact C-vs-Python → full S0 → S1 (b33 playbook:
   gen_t6_b33.py is the template).
4. Update LEADS_LEDGER.md (prepend entry, supersede 01:25 CEST).

## Files
new_constructions/batch34/: probes.v, s0_probes.sh, t6_b34_screen.py,
screen_a3_5st.log, screen_aoi_5st.log, s0_probes/, tmp/ (TMPDIR), RESUME.md
Ledger: LEADS_LEDGER.md head entry 01:25 CEST (batch-34 opened).
Heartbeat: new_constructions/supervisor_heartbeat.txt (update every ~15 min).

## STOP 2026-10-11 ~01:52 CEST (parent cron timeout)
- B34-A (a3@5st): 0/200, min z=4128 -> TERMINAL KILL (VALID). Ledger entry pending.
- B34-C (d2a3@4st): 0/200, min z=6892 -> TERMINAL KILL (VALID). Ledger entry pending.
- B34-B (aoi@5st): 0/200 random (min 17.7) + hill-climb 12 gens plateaued at z~28.8, no KEEP -> NOT terminal but no survivor; needs S0 (blocked) or new idea.
- B34-D skipped (a3@5st catastrophic -> 4st certainly dead).
- S0: INFRA BROKEN box-wide (yosys->abc pipe deadlock post "YOSYS_ABC_DONE"; binary fine standalone; worked 2026-10-10, broken since ~01:18 2026-10-11). LOUD, needs toolchain owner.
- /tmp-full was transient (resolved); it wedged 2 S0 workers (mine killed+relaunched, then re-wedged by the pipe bug).
- NEXT: (1) ledger entry with the three verdicts; (2) fix S0 infra; (3) if S0 fixed and aoi<=3.96u/st, escalate best AOI schedule (z=28.78, in hillclimb log) or try a2a2 form (dual-AND2-ORed, 4 probes, 3 terms -- designed but never triaged).
