# Directed Design — Next Iteration Status

Liveness heartbeat for the directed-design worker (30-min status cron).
Append a timestamped line at least every 30 minutes.

## 2026-10-07 20:55 CEST — worker start
- Read state: batch1–3 specs/S0 done; dd1_lin_5_13_nw + dd1_lin_8_15_nw S1 CAL_PASS (also dd1_lin_5_9_nw CAL_PASS but out of PART-1 scope — flagged to coordinator).
- PART 1: dd candidates have Python model.py but impl.c is a STUB → must generate bit-exact C impl, xcheck, then S2/S3/S4/Q1.
- PART 2: batch 4 = key-schedule variants (per README roadmap + batch3 pivot note); will extend gen_verilog.py with parameterized ks, write gen_batch4.py.

## 2026-10-07 21:10 CEST — PART 1 progress
- Wrote directed_design/mk_c_impl.py (spec → bit-exact impl.c; supports sbox_rounds, rots_varying, parameterized ks).
- Generated impl.c for dd1_lin_5_13_nw + dd1_lin_8_15_nw (stub backups in logs/).
- XCHECK: PASS 10000/10000 C==Python for both → C stages unblocked.
- S2 launched sequentially for both (diffprof key=0x123456789abcdef0 log2N=22 kill_repeats=10), logs in results/s2/<cand>/.

## 2026-10-07 21:15 CEST — PART 2 progress
- FOUND+FIXED infra bug: gen_verilog.py __main__ silently dropped pbox/sbox_rounds/ks (batch2/3 .v files were generated with an older working version — verified artifacts are correct). Fixed + regression-checked (regen of dd1_lin_5_13_nw.v differs only by added comment line).
- Extended gen_verilog.py: parameterized key schedule (rot_step int|[s1,s2], rc golden|zero|list).
- Wrote gen_batch4.py: 8 key-schedule variants on lin(5,13)/pba19/rasC2_0 base (golden control, norc, smallrc, rot7, rot1, rot32, norot, fold). specs/batch4_specs.json + 8 .v files; verified rk wires differ per variant.
- S0 launched for all 8 via authorized run_synth.py (Yosys 0.69), results/s0/.

## 2026-10-07 21:20 CEST — batch 4 S0 done
- Batch 4 S0 (8 ks variants, run_synth.py Yosys 0.69): norc/smallrc/rot1 hit 26.3u (-0.2u vs golden control, tie dd1_lin_5_9_nw lead); golden control reproduces dd1 26.5u exactly; norot ties 26.5u with -185 cells.
- S0 kills (delay objective, scoped): fold (+1.8u), rot7 (+0.2u), rot32 (+0.2u).
- S1 queue: norc, smallrc, rot1, norot. model.py generated for all; impl.c xcheck-verified for fold (pattern proven).
- PART 1 S2 dd1_lin_5_13_nw still running (no kills so far, max|z|~11, repeats<=1).
- Holding S1 launch until S2 finishes / load drops (load ~21, sweep diffprof active).

## 2026-10-07 21:28 CEST — checkpoint
- PART 1: impl.c generated + xcheck PASS (10000/10000) for dd1_lin_5_13_nw, dd1_lin_8_15_nw.
  S2 running sequentially (log2N=22, kill_repeats=10): candidate 1 at delta bit 52/64,
  zero kills so far (max|z| peak 18.9, repeats<=1 — in-family vs reference (5,13) S2 max|z|=25.1).
  S3/S4/Q1 queued behind S2 (builds ready: s3_gen, smallcrush linkable; q1_sacbic.py ready).
- PART 2: batch 4 = key-schedule axis (8 variants). S0 done, table in results/batch4_s0.md.
  Leads: norc/smallrc/rot1 @26.3u (-0.2u vs control); norot ties 26.5u (-185 cells).
  S0 kills: fold (+1.8u), rot7/rot32 (+0.2u). S1 queued for norc/smallrc/rot1/norot
  (model.py + impl.c generated, xcheck PASS 2000/2000 each); held for load (2-CPU VM, load ~10-18).
- Infra: fixed gen_verilog.py __main__ (was silently dropping pbox/sbox_rounds/ks);
  extended it + mk_c_impl.py + new mk_model.py with parameterized ks; golden control
  reproduces dd1_lin_5_13_nw bit-exact (S0 26.5u, goldens match).

## 2026-10-07 21:35 CEST — handoff worker active
- Verified S2 pipeline alive (cand1 dd1_lin_5_13_nw at structured-delta phase, zero kills, max|z| peak 18.9, repeats<=1); cand2 dd1_lin_8_15_nw queued next in same detached pipeline.
- PART-1 ext (coordinator decision): dd1_lin_5_9_nw now in scope. Generated impl.c via mk_c_impl.py, installed into fast_battery/candidates/dd1_lin_5_9_nw/, built diffprof binary, XCHECK PASS 10000/10000 C==Python. Launched detached waiter (s2_waiter_59.sh) that runs its S2 (key 0x123456789abcdef0, log2N=22, kill_repeats=10) after run.log prints ALLDONE, then appends ALLDONE_5_9.
- All three PART-1 candidates confirmed S1 CAL_PASS from results/s1/*/s1_result.json.
- Next: collect S2 verdicts when pipeline completes → S3/S4/Q1 for survivors; PART-2 S1 for 4 ks qualifiers once load allows (sweep in round_tweak/ has priority, current load ~13).

## 2026-10-07 22:04 CEST — worker start (resume)
- Previous worker's last heartbeat 21:35 CEST; sibling tracks killed by cron timeout 21:36 CEST. Treating as dead; resuming.
- Checkpoints: (1) collect PART-1 S2 verdicts for dd1_lin_5_13_nw, dd1_lin_8_15_nw (ALLDONE rc=0 expected), (2) dd1_lin_5_9_nw S2 waiter status, (3) S3/S4/Q1 for survivors, (4) PART-2 S1 for 4 ks qualifiers when load allows.

## 2026-10-07 22:06 CEST — S2 verdicts collected, holding new launches (high load)
- S2 VERDICTS (results/s2/, key=0x123456789abcdef0, log2N=22, kill_repeats=10):
  - dd1_lin_5_13_nw: PASS (max_repeats=1, max|z|=25.1, all 115 deltas), rc=0. Advances to S3/S4/Q1.
  - dd1_lin_8_15_nw: PASS (max_repeats=1, max|z|=14.2, all 115 deltas), rc=0, run.log ALLDONE. Advances to S3/S4/Q1.
  - dd1_lin_5_9_nw: S2 IN FLIGHT (pid 145355, started 19:55 UTC; 56/115 delta lines, zero kills so far — worst |z| seen 10.3). Waiter script already had it launched; NOT dead, just slower than the first two. ETA ~10 min.
- S2 pipelines for 5_13/8_15 are done (no process to babysit); 5_9's waiter will append ALLDONE_5_9 on completion — nothing to fix.
- S3/S4/Q1 for 5_13+8_15 and PART-2 S1 (norc/smallrc/rot1/norot): ALL INPUTS STAGED (sc_dd1_* + gen_* binaries in fast_battery/build/; dd4_ks_* candidates installed with model.py+impl.c+meta.json; RNG_test present at /home/hatch/tools/practrand/PractRand/RNG_test; q1_sacbic.py at exploration/round13/). Launch commands are trivial:
  - S3: nice -19 src/s3_practrand.sh <cand> build/gen_<cand> results/s3/<cand> <key>
  - S4: src/s4_smallcrush.c built via sc_<cand> binary
  - S1: nice -19 python3 src/s1_screen.py <dd4_ks_X_nw> s1_results/<dd4_ks_X_nw>
- HOLDING launches: VM load ~11.9 on 2 CPUs at 22:04 (graalgo-m8 wave2 java/go + qemu-riscv64 kernels — other projects, not mine to touch). sweep.py (pid 1663) alive, priority respected. 5_9's S2 is already CPU-starved (28% on its own core); adding nice'd work now would gain nothing and risk priority inversion. POLITE-MODE rule: launch when 1-min load < ~4 or when 5_9 S2 completes and load clears.
- Track is nominal: alive processes (sweep.py, 5_9 diffprof), all results on disk, heartbeat continuing. Next check will launch whatever fits the load.

## 2026-10-08 00:07 CEST — worker start (resume)
- Previous worker's last heartbeat 22:06 CEST (over 2h ago); treating as dead; resuming.
- VERIFIED from raw logs: dd1_lin_5_13_nw S2 PASS (max_repeats=1, max|z|=25.1), dd1_lin_8_15_nw S2 PASS (max_repeats=1, max|z|=14.2), dd1_lin_5_9_nw S2 PASS (max_repeats=2, max|z|=14.8, log results/s2/dd1_lin_5_9_nw/s2_diffprof.log, run.log ALLDONE_5_9). All three advance to S3/S4/Q1.
- sweep.py pid 1663 alive (priority respected). Current 1-min load 6.74 (was 11.9 at handoff) — trending down but still above <4 heavy-launch gate. Holding heavy batteries; doing light staging checks meanwhile.
- HYB_LOG.md note (hybrid track batch-4): lin(3,11) co-designed P-box (3,1) hit 26.1u — NEW fastest of hybrid batch 4, beats dd 26.3u leads. Coordinates for next directed iteration: P-box co-design axis for lin(5,13) should take the (a,b) scan approach from hybrid/codesign/lin_trail.py rather than blind swaps.
- Next: launch PART-2 S1 for norc/smallrc/rot1/norot (inputs staged) when load < ~4; then S3/S4/Q1 for the three dd survivors.

## 2026-10-08 00:20 CEST — next-iteration proposal (batch-5 design; launch after S1 ks verdicts)
- Key-schedule axis outcome: norc/smallrc/rot1 all 26.3u (tie dd1_lin_5_9_nw lead), norot 26.5u/-185 cells. S1 queued; verdicts pending.
- NEXT AXIS (per 2026-10-07 hybridization directive — co-design, never blind-swap): P-box × key-schedule co-combination FOR lin(5,13), using hybrid/codesign/lin_trail.py (a,b) rankings for (5,13), not arbitrary swaps. Mechanistic hypothesis: batch-4 proved the ks path sits on the critical path (-0.2u when the RC XOR or rotl13 depth is removed); the co-designed P-boxes that scored min=39 lin-trail for (5,13) distribute rotation alignment differently — combining a top-tier (a,b) with norc/smallrc/rot1 should stack, not collide.
- Non-duplication guard vs hybrid batch-4: hybrid already S1-queued (43,7) [CAL_PASS], (53,1) [FLAG], (61,1), (3,7) [26.2u] in THEIR construction; batch-5 stays in the directed 4r-keyed-SPN rasC2_0 construction with batch-4 ks leads, and targets (a,b) pairs hybrid did NOT take: top (5,13) lin-trail tier members beyond (43,1),(43,7),(53,1),(21,1),(21,5),(29,1),(35,7),(3,7),(61,1) — e.g. a=53 b in other top-min groups, a=21 tier, a=29 tier — crossed with ks=norc/smallrc/rot1. Only pairs with lin-trail min>=39 AND b in the same a's top-min group (hybrid's stated selection rule).
- Rule: every batch-5 verdict scoped in VERDICT_SCOPE.md as "<(a,b),ks> in the 4r rasC2_0/pba19/lin(5,13) construction".
- Sequence: S1 ks verdicts first (they decide which ks leg survives); S3/S4/Q1 for dd1_lin_5_13/8_15/5_9 in parallel when load allows (load gate <~4, concurrency 1, nice -19, sweep.py priority).

## 2026-10-08 00:25 CEST — holding (load gate not met)
- 1-min load went 6.74 -> 7.72 -> 10.10 (sibling tracks' S1/S2/Q1 + graalgo-m8 wave2 + round_tweak S1 rtw_n7b_050913 all active). Polite-mode gate (<~4) not met; launching nothing this cycle.
- All queued work remains staged and inputs verified: S1 for dd4_ks_norc/smallrc/rot1/norot (model.py+impl.c+meta.json present, xcheck PASS); S3 (gen_dd1_* + RNG_test present), S4 (sc_dd1_* present), Q1 (q1_sacbic.py present) for the three S2-passed dd survivors.
- Next-iteration proposal (batch-5: P-box × ks co-design for lin(5,13), non-duplicating hybrid batch-4) written above; gated on S1 ks verdicts.
- Track nominal: heartbeat maintained, no dead processes, no fixes needed.
- 2026-10-08 02:44 CEST: resume supervisor start (replaces session dead since 00:25). Track nominal, nothing to restart: S2 verdicts all collected on disk (5_13/8_15/5_9 all PASS), no orphan processes. Inputs for staged next steps verified: sc_dd1_*/gen_dd1_* binaries + RNG_test + q1_sacbic.py present; dd4_ks_norc/smallrc/rot1/norot candidates installed with model.py+impl.c+meta.json, xcheck PASS. HELD: PART-2 S1 (4 ks qualifiers) + S3/S4/Q1 for the 3 dd survivors -- 1-min load ~13 > 4 polite gate, sweep.py priority, concurrency-1 across tracks (hybrid S2 currently holds the slot). Will launch when gate clears.
